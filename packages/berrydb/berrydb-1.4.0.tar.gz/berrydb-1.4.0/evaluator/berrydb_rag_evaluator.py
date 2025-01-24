from ast import Str
import os, time
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
from typing import List, Dict, Any, Union, Optional
from utils.berrydb_metrics import Metrics


from deepeval.test_case import LLMTestCase
import deepeval.metrics

class BerryDBRAGEvaluator:

    def __init__(self, api_key:str, database_name:str, open_ai_api_key:str,
                 langchain_api_key:str="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",
                 langchain_project_name:str="BerryDB",
                 metrics_database_name:Optional[str]="EvalMetricsDB"):
      from berrydb.BerryDB import BerryDB
      self.__api_key = api_key
      self.__database_name = database_name
      self.__open_ai_api_key = open_ai_api_key
      self.__db = BerryDB.connect(api_key, database_name)
      self.__langchain_api_key = langchain_api_key
      self.__langchain_project_name = langchain_project_name
      self.__metrics_database_name = metrics_database_name


    def __check_openai_key(self):
      if not self.__open_ai_api_key:
          raise EnvironmentError("open_ai_api_key is required")

    def eval(self, test_params: Dict[str, Any], metrics_names: Union[str, List[str]], metrics_args:Optional[Dict[str, Any]] = None , metrics_processor=None):
      """
        This method evaluates the given test cases using the specified metrics.

        Parameters:
        test_params (Dict[str, Any]): A dictionary containing the test parameters. This can include
                                              1. The dataset used for testing, under the key "test_data".
                                              2. Name of the database that is being evaluated, under the key "database_name". (Optional)
                                              3. The name of the test suite, under the key "test_suite_name". (Optional)
                                              4. In case you have multiple runs against the same test suite, you can use the run_name to differentiate. The name of the run should be under the key "run_name". (Optional)

        metrics_names (Union[str, List[str]]): The names of the metrics to be used for evaluation. Redundant metrics are flatten in the code. Metrics can be passed in any of  the following ways:
                                                    1. A single metric name as a string.
                                                          OR
                                                    2. Multiple metrics as a list of individual metric names.
                                                          OR
                                                    3. A single metrics collection name.
                                                          OR
                                                    4. Multiple metrics collections as a list of individual metric names.
                                                          OR
                                                    5. Combination of metrics and metrics collection name/s as a list


        metrics_args:Optional[Dict[str, Any]] = None: Metric parameters like the threshold, the model to use for the evaluation, whether to include a reason or not can be passed as a Dict.

        metrics_processor: A custom metrics processor function. If not provided, the default metrics processor will be used which upserts all the metrics to EvalMetricsDB.


        Returns:
        None
      """
      metrics_names, metrics_args = self.__process_input(metrics_names, metrics_args)
      all_metrics = self.__all_metrics(metrics_names, metrics_args)
      self.__trigger_time = int(datetime.now().timestamp() * 1000)
      self.__test_params = test_params
      test_data = test_params["test_data"]
      if metrics_processor is None:
        metrics_processor = self.__store

      for i in range(len(test_data)):
        question = test_data[i]["input"]

        response = self.__chat(question)
        print(f"response:{response}")
        test_case = self.__create_test_case(test_data[i], response)

        for metric in all_metrics:
          metric.measure(test_case)
          metrics_processor(metric, question, response)

    def __all_metrics(self, metrics_names, metrics_args):
      all_metrics = set()
      for metric_name in metrics_names:
        try:
          metrics_enum_value = getattr(Metrics, metric_name).value
        except AttributeError:
          raise ValueError(f"Invalid metric name: {metric_name}")
        metric_objects = self.__create_metric_objects(metrics_enum_value, metrics_args)
        all_metrics.update(metric_objects)
      return all_metrics

    def __create_metric_objects(self, metrics_enum_value, metrics_args):
      print(f"Creating metrics object for {metrics_enum_value}")
      metric_objects = []
      for metric_name in metrics_enum_value:
        try:
          metrics_object = getattr(deepeval.metrics, metric_name)(**metrics_args)
        except AttributeError:
          raise ValueError(f"Invalid metric name: {metric_name}")
        metric_objects.append(metrics_object)
      return metric_objects

    def __process_input(self, metrics_names, metrics_args):
      if isinstance(metrics_names, list):
        if metrics_names is None or len(metrics_names) == 0:
          raise ValueError("Did not receive any metrics names. List of metrics names is blank.")
      elif isinstance(metrics_names, str):
          metrics_names = [metrics_names]
      else:
          raise ValueError("Did not receive any metrics names. You can either pass a single metricname/ metric collection name or a list of metric names and metric collection anmes.")

      if metrics_args is None:
        metrics_args = {
            "threshold": 0.5,
            "model": "gpt-4o-mini",
            "include_reason": True
        }
      return metrics_names, metrics_args

    def __store(self,metric, question, response):
      from berrydb.BerryDB import BerryDB
      metrics_db = BerryDB.connect(self.__api_key, self.__metrics_database_name)
      metrics_db.upsert({
          "question": question,
          "answer": response['answer'],
          "context": response['context'],
          "score": metric.score,
          "reason": metric.reason,
          "threshold": metric.threshold,
          "isSuccessful": metric.is_successful(),
          "metricName": metric.__class__.__name__,
          "runName": self.__test_params["run_name"],
          "testSuiteName": self.__test_params["test_suite_name"],
          "databaseName": self.__test_params["database_name"],
          "triggerTimestamp": self.__trigger_time
      })

    def __chat(self, question):
      response = self.__db.chat_for_eval(
          self.__open_ai_api_key,
          question,
          3,
          0.8,
          "gpt-4o-mini",
          langchain_api_key= self.__langchain_api_key,
          langchain_project_name= self.__langchain_project_name
        )
      return response

    def __create_test_case(self, test_data, response):
      test_case = LLMTestCase(
        input=test_data["input"],
        expected_output=test_data["expected_output"],
        actual_output= response['answer'],
        retrieval_context=response['context'])
      return test_case