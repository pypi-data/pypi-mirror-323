import json
import warnings
from os import _exit as exit
from typing import Tuple

import requests
from langchain_openai.chat_models import ChatOpenAI
from urllib3.exceptions import InsecureRequestWarning

import constants.constants as bdb_constants
from constants.constants import (DEFAULT_BUCKET, connect_project_to_ml_url,
                                 create_annotations_url, create_database_url,
                                 create_label_studio_project_url,
                                 create_predictions_url, create_schema_url,
                                 debug_mode, delete_database_url,
                                 evaluate_endpoints, get_database_id_url,
                                 get_database_list_by_api_key_url,
                                 get_schema_id_url,
                                 reimport_label_studio_project_url,
                                 setup_label_config_url, validate_api_key_url)
from database.database import Database
from utils.utils import Utils


class BerryDB:

    @staticmethod
    def __validate_initialization():
        """
        Validates that `init` has been called. If not, prints a guide and exits.
        """
        if bdb_constants.BASE_URL is None:
            print(
                """
                # BerryDB SDK Initialization Guide
                Before using any features of the SDK, you **must** initialize it by setting the base URL for BerryDB using the `init` method.
                This is a required step to configure the SDK to communicate with your BerryDB instance.

                Example:
                    BerryDB.init("https://my-berrydb-instance.com/api")
                    **or**
                    BerryDB.init("http://101.102.103.104")

                You can use the BerryDB SDK methods, after initializing.

                """)
            raise SystemExit(0)

    @staticmethod
    def init(berrydb_base_url: str) -> None:
        """
        Initializes the SDK with the BerryDB base URL.

        berrydb_base_url: The base URL of the BerryDB installation.

        Example:
                    BerryDB.init("https://my-berrydb-instance.com/api")
                    **or**
                    BerryDB.init("http://101.102.103.104")
        """
        evaluate_endpoints(berrydb_base_url)

    @classmethod
    def connect(
        self,
        api_key: str,
        database_name: str,
        bucket_name: str = DEFAULT_BUCKET,
    ):
        """Function summary

        Args:
            arg1 (str): API Key
            arg2 (str): Database Name
            arg3 (str): Bucket Name (Optional)

        Returns:
            Database: An instance of the database
        """
        BerryDB.__validate_initialization()

        bucket_name = self.__validate_bucket_name(bucket_name)

        if debug_mode:
            print("api_key: ", api_key)
            print("database_name: ", database_name)
            print("bucket_name: ", bucket_name)
            print("\n\n")

        try:
            org_name: str = self.__validate_api_key(self, api_key, database_name)
        except Exception as e:
            raise e

        if org_name is None:
            raise ValueError(f"Error: Either your API key is invalid or you are not authorized to access the database {database_name}")

        return Database(api_key, bucket_name, org_name, database_name)

    @classmethod
    def databases(self, api_key: str):
        """Function summary

        Args:
            arg1 (str): API Key

        Returns:
            list: Dict of Databases
        """
        BerryDB.__validate_initialization()
        url = bdb_constants.BASE_URL + get_database_list_by_api_key_url
        params = {"apiKey": api_key}

        if debug_mode:
            print("url:", url)
            print("params:", params)

        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)
            jsonResponse = response.json()
            if debug_mode:
                print("databases result ", jsonResponse)
            if (
                "database" in jsonResponse
                and "responseList" in jsonResponse["database"]
            ):
                databaseNames = {}
                # print("\nDatabases:")
                for db in jsonResponse["database"]["responseList"]:
                    name = db["name"] if "name" in db else ""
                    schemaName = db["schemaName"] if "schemaName" in db else ""
                    description = db["description"] if "description" in db else ""
                    dbId = db["id"] if "id" in db else ""
                    schemaId = db["schemaId"] if "schemaId" in db else ""
                    isContentType = db["contentType"] if "contentType" in db else ""
                    databaseNames[name] = {
                        "id": dbId,
                        "schemaId": schemaId,
                        "schemaName": schemaName,
                        "description": description,
                        "isContentType": isContentType,
                    }
                    # print(name + " : " + str(databaseNames[name]))
                # print("\n")
                return databaseNames
            return {}
        except Exception as e:
            print("Failed to fetch databases: {}".format(str(e)))
            return {}

    @classmethod
    def create_schema(self, api_key, schema_name, schema_desc, schema_details):
        """Function summary

        Args:
            arg1 (str): API Key
            arg3 (str): Schema Name
            arg4 (str): Schema Description
            arg5 (str): Schema Details
        Returns:
            str:  Connection to the database
        """
        BerryDB.__validate_initialization()
        if debug_mode:
            print("schema_details: ", schema_details)

        url = bdb_constants.BASE_URL + create_schema_url
        params = {"apiKey": api_key}

        payload = json.dumps(
            {
                "name": schema_name,
                "description": schema_desc,
                "details": schema_details,
            }
        )
        headers = {
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json",
        }

        if debug_mode:
            print("url:", url)
            print("payload:", payload)
            # print("headers:", headers)

        try:
            response = requests.post(url, params=params, data=payload, headers=headers)
            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if debug_mode:
                print("Schema creation result ", response.json())
            json_res = json.loads(response.text)
            if json_res["responseList"][0]["schemaId"]:
                print(
                    json_res["message"]
                    if json_res["message"]
                    else "Schema created successfully"
                )
                res = json_res["responseList"][0]
                res["schema_name"] = schema_name
                return res
            else:
                Utils.handleApiCallFailure(
                    "Schema creation failed, please try again later.",
                    response.status_code,
                )
        except Exception as e:
            print("Failed to create the Schema: {}".format(str(e)))
            return None

    @classmethod
    def create_database(
        self, api_key, database_name, schema_name, bucket_name=DEFAULT_BUCKET
    ):
        """Function summary

        Args:
            arg1 (str): API Key
            arg2 (str): Database Name
            arg3 (str): Schema Name

        Returns:
            Database: An instance of the newly created database, if database with name already exists, prints a failure message and returns None
        """
        BerryDB.__validate_initialization()
        schema_id = None
        user_id = None
        try:
            schema_id, user_id = self.__get_schema_id_by_name(api_key, schema_name)
        except Exception as e:
            pass
        if debug_mode:
            print("schema_id :", schema_id)
            print("user_id: ", user_id)
        if not (schema_id and user_id):
            return

        url = bdb_constants.BASE_URL + create_database_url
        payload = {
            "schemaId": str(schema_id),
            "userId": user_id,
            "databaseName": database_name,
        }
        # headers = Utils.get_headers(api_key, "multipart/form-data")
        params = {"apiKey": api_key}

        if debug_mode:
            print("url:", url)
            print("payload:", payload)
            print("params:", params)
            # print("headers:", headers)

        try:
            session = requests.session()
            response = session.post(url, data=payload, params=params)
            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if debug_mode:
                print("Database creation result ", response.json())
            json_res = json.loads(response.text)
            if json_res["databaseId"]:
                print(
                    json_res["message"]
                    if json_res["message"]
                    else "Database created successfully"
                )
                return Database(
                    api_key, bucket_name, json_res["databaseId"], database_name
                )
            else:
                Utils.handleApiCallFailure(
                    "Database creation failed, please try again later.",
                    response.status_code,
                )


        except Exception as e:
            raise Exception("Failed to create the database: {}".format(str(e)))


    @classmethod
    def delete_database(self, api_key, database_name):
        """Function summary

        Args:
            arg1 (str): API Key
            arg2 (str): Database Name

        Returns:
            str:  Connection to the database
        """
        BerryDB.__validate_initialization()
        schema_id = None
        user_id = None
        database = self.__get_database(self, api_key, database_name)
        print("database :", database)

        schema_id = None
        user_id = None
        try:
            schema_id, user_id = self.__get_schema_id_by_name(
                api_key, database["schemaName"]
            )
        except Exception as e:
            pass
        if debug_mode:
            print("schema_id :", schema_id)
            print("user_id: ", user_id)
        if not (schema_id and user_id):
            return

        url = bdb_constants.BASE_URL + delete_database_url
        params = {"databaseId": database["id"], "userId": user_id, "apiKey": api_key}
        headers = {
            "Content-Type": "application/json",
        }

        if debug_mode:
            print("url:", url)
            print("params:", params)

        try:
            response = requests.delete(url, params=params, headers=headers)
            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if debug_mode:
                print("Database deletion result ", response.json())
            json_res = json.loads(response.text)
            return json_res["message"]
        except Exception as e:
            print("Failed to delete the database: {}".format(str(e)))
            return None

    @classmethod
    def create_project(
        self, annotations_api_key, project_name, project_description=""
    ):
        """Function summary

        Args:
            arg1 (str): API Key
            arg2 (str): Project Name
            arg3 (str): Project Description (Optional)

        Returns:
            str:  Success/failure message
        """
        BerryDB.__validate_initialization()

        url = bdb_constants.LABEL_STUDIO_BASE_URL + create_label_studio_project_url
        payload = {"title": project_name, "description": project_description}
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {annotations_api_key}",
        }

        if debug_mode:
            print("url:", url)
            print("payload:", payload)

        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            if response.status_code != 201:
                print("Failed to create Project!")
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if debug_mode:
                print("Create LS project result ", response.json())
            # json_res = json.loads(response.text)
            print("Project created successfully")
            return response.json()
        except Exception as e:
            print(f"Failed to create your project: {str(e)}")
            return None

    @classmethod
    def setup_label_config(self, annotations_api_key, project_id, label_config):
        """Function summary

        Args:
            arg1 (str): Annotations API Key
            arg2 (int): Project ID
            arg3 (str): Label Config

        Returns:
            str:  Success/failure message
        """
        BerryDB.__validate_initialization()

        url = bdb_constants.LABEL_STUDIO_BASE_URL + setup_label_config_url.format(project_id)
        payload = json.dumps({"label_config": label_config})
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {annotations_api_key}",
        }

        if debug_mode:
            print("url:", url)
            print("payload:", payload)

        try:
            response = requests.patch(url, data=payload, headers=headers)
            if response.status_code != 200:
                print("Project label config setup Failed!")
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if debug_mode:
                print("Setup config result ", response.json())
            print("Project label config setup successful!")
            return response.json()
        except Exception as e:
            print(f"Failed to setup config: {str(e)}")
            return None

    @classmethod
    def populate_project(self, annotations_api_key, project_id, database_name, berrydb_api_key):
        """Function summary

        Args:
            arg1 (str): Annotations API Key
            arg2 (int): Annotations project ID
            arg3 (str): Database Name
            arg4 (str): BerryDB API Key

        Returns:
            json: Project details
        """
        BerryDB.__validate_initialization()

        try:
            reimport_url = bdb_constants.LABEL_STUDIO_BASE_URL + reimport_label_studio_project_url.format(project_id)
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Token {}".format(annotations_api_key),
            }
            reimport_data = {
                "file_upload_ids": [],
                "files_as_tasks_list": False,
                "database_name": database_name,
                "bdb_api_key": berrydb_api_key,
            }

            if debug_mode:
                print("url:", reimport_url)
                print("payload:", reimport_data)

            reimport_response = requests.post(
                reimport_url, data=json.dumps(reimport_data), headers=headers
            )
            if reimport_response.status_code != 201:
                print("Project populated Failed!")
                Utils.handleApiCallFailure(
                    reimport_response.json(), reimport_response.status_code
                )
            if debug_mode:
                print("Populate project result: ", reimport_response.json())
            print("Project populated successfully!")
            return reimport_response.json()
        except Exception as e:
            print(f"Failed to populate your project: {str(e)}")
            if debug_mode:
                raise e
            return None

    @classmethod
    def connect_project_to_ml(self, annotations_api_key, project_id, ml_url, ml_title="ML Model"):
        """Function summary

        Args:
            arg1 (str): Annotations API Key
            arg2 (int): Annotations project ID
            arg3 (str): ML Backend URL you want to connect the project to
            arg4 (str): A title for the connection (Optional)

        Returns:
            None
        """
        BerryDB.__validate_initialization()

        # TODO: Check for existing connected ML models and use the PATCH method to update the existing ML model connection
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Token {}".format(annotations_api_key),
            }
            ml_payload = {
                "project": project_id,
                "title": ml_title or "ML Model",
                "url": ml_url,
                "is_interactive": False,
            }
            ml_connect_response = requests.post(
                bdb_constants.LABEL_STUDIO_BASE_URL + connect_project_to_ml_url, data=json.dumps(ml_payload), headers=headers
            )
            if ml_connect_response.status_code != 201:
                print("Project Failed to connect to ML Model")
                Utils.handleApiCallFailure(
                    ml_connect_response.json(), ml_connect_response.status_code
                )
            if debug_mode:
                    print("Connect project to ML result: ", ml_connect_response.json())
            print("Project connected to ML Model successfully!")
        except Exception as e:
            print(f"Failed to Connect project to BerryDB ML backend: {str(e)}")
            return None

    @classmethod
    def create_prediction(self, annotations_api_key, project_id, task_id, prediction):
        """Function summary

        Args:
            arg1 (str): Annotations API Key
            arg2 (int): Annotations project ID
            arg3 (int): Task ID in the project
            arg4 (dict): The prediction dict to add to the task (Optional)

        Returns:
            None
        """
        BerryDB.__validate_initialization()

        try:
            # Suppress only the InsecureRequestWarning from urllib3
            warnings.simplefilter('ignore', InsecureRequestWarning)
            if not annotations_api_key:
                print("Error: annotations_api_key is required and must be of type str")
                return
            if not project_id:
                print("Error: project_id is required and must be of type int")
                return
            if not task_id:
                print("Error: task_id is required and must be of type int")
                return

            url = bdb_constants.LABEL_STUDIO_BASE_URL + create_predictions_url.format(task_id)

            if type(prediction) != dict:
                print("Error: prediction has to be dict type")
                return
            prediction["project"] = project_id
            prediction["task"] = task_id

            payload = json.dumps(prediction)
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Token {annotations_api_key}",
            }

            if debug_mode:
                print("url:", url)
                print("payload:", payload)

            print(f"Adding prediction to task with ID: {task_id} in project with ID: {project_id}")
            response = requests.post(url, data=payload, headers=headers, verify=False)
            if response.status_code != 201:
                print(f"Failed to add prediction to task with ID: {task_id}")
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if debug_mode:
                print("Setup config result ", response.json())
            print(f"Successfully added prediction to task with ID: {task_id}")
            return response.json()
        except Exception as e:
            print(f"Failed to create prediction: {str(e)}")
            return None

    @classmethod
    def create_annotation(self, annotations_api_key, project_id, task_id, annotation):
        """Function summary

        Args:
            arg1 (str): Annotations API Key
            arg2 (int): Annotations project ID
            arg3 (int): Task ID in the project
            arg4 (dict): The annotation dict to add to the task (Optional)

        Returns:
            None
        """
        BerryDB.__validate_initialization()

        try:
            # Suppress only the InsecureRequestWarning from urllib3
            warnings.simplefilter('ignore', InsecureRequestWarning)
            if not annotations_api_key:
                print("Error: annotations_api_key is required and must be of type str")
                return
            if not project_id:
                print("Error: project_id is required and must be of type int")
                return
            if not task_id:
                print("Error: task_id is required and must be of type int")
                return

            url = bdb_constants.LABEL_STUDIO_BASE_URL + create_annotations_url.format(task_id, project_id)

            if type(annotation) != dict:
                print("Error: annotations has to be dict type")
                return
            annotation["project"] = project_id

            payload = json.dumps(annotation)
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Token {annotations_api_key}",
            }

            if debug_mode:
                print("url:", url)
                print("payload:", payload)

            print(f"Adding annotation to task with ID: {task_id} in project with ID: {project_id}")
            response = requests.post(url, data=payload, headers=headers, verify=False)
            if response.status_code != 201:
                print(f"Failed to add annotation to task with ID: {task_id}")
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if debug_mode:
                print("Setup config result ", response.json())
            print(f"Successfully added annotation to task with ID: {task_id}")
            return response.json()
        except Exception as e:
            print(f"Failed to create annotations: {str(e)}")
            return None

    """ @classmethod
    def __get_project(self, annotations_api_key, project_id):
        try:
            if debug_mode:
                print(annotations_api_key)
                print(project_id)
            ls = Client(url=label_studio_base_url, api_key=annotations_api_key)
            project = ls.get_project(id=project_id)
            if not project:
                print(f"Failed to get project")
            if debug_mode:
                print("Fetched project result: ",  project)
            return project
        except Exception as e:
            print(f"Failed to get project: {str(e)}")
            raise Exception(e)
            return None """

    @classmethod
    def get_task_ids(self, annotations_api_key, project_id):
        """Function summary

        Args:
            arg1 (str): Annotations API Key
            arg2 (int): Annotations project ID

        Returns:
            list: List of task ids in the project
        """
        BerryDB.__validate_initialization()
        try:
            from label_studio_sdk import Client
        except ImportError:
            raise Exception('Could not import label_studio_sdk module. Please install the required dependencies.')

        ls = Client(url=bdb_constants.LABEL_STUDIO_BASE_URL, api_key=annotations_api_key)
        project = ls.get_project(id=project_id)
        return project.get_tasks(only_ids=True)

    @classmethod
    def get_task_by_id(self, annotations_api_key, project_id, task_id):
        BerryDB.__validate_initialization()
        try:
            from label_studio_sdk import Client
        except ImportError:
            raise Exception('Could not import label_studio_sdk module. Please install the required dependencies.')

        ls = Client(url=bdb_constants.LABEL_STUDIO_BASE_URL, api_key=annotations_api_key)
        project = ls.get_project(id=project_id)
        return project.get_task(task_id)

    @classmethod
    def get_tasks(self, annotations_api_key, project_id):
        BerryDB.__validate_initialization()
        try:
            from label_studio_sdk import Client
        except ImportError:
            raise Exception('Could not import label_studio_sdk module. Please install the required dependencies.')

        ls = Client(url=bdb_constants.LABEL_STUDIO_BASE_URL, api_key=annotations_api_key)
        project = ls.get_project(id=project_id)
        return project.get_tasks()

    @classmethod
    def get_answer_for_prompt(
        self,
        open_ai_api_key,
        prompt,
        question,
        temperature=None,
        open_ai_model=None,
    ):
        BerryDB.__validate_initialization()

        print("Prompt: " + prompt)
        print("Question: " + question)
        llm = ChatOpenAI(
            model=open_ai_model or bdb_constants.DEFAULT_OPEN_AI_MODEL,
            temperature=temperature or bdb_constants.DEFAULT_OPEN_AI_TEMPERATURE,
            api_key=open_ai_api_key,
        )
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": question},
        ]

        try:
            llm_response = llm.invoke(messages)
            llm_response = llm_response.content
            print("Answer: " + str(llm_response))
            return llm_response
        except Exception as e:
            print(e)

    @classmethod
    def __get_schema_id_by_name(self, api_key: str, schema_name: str) -> Tuple[int, int]:
        """Function summary

        Args:
            arg1 (str): API Key
            arg2 (str): Schema Name

        Returns:
            (int : Schema ID, int : User ID)
        """

        url = bdb_constants.BASE_URL + get_schema_id_url
        params = {"apiKey": api_key, "schemaName": schema_name}

        if debug_mode:
            print("url:", url)
            print("params:", params)

        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if debug_mode:
                print("Get schema id by name result ", response.json())
            json_res = json.loads(response.text)
            if json_res.get("schema", None):
                return (
                    json_res["schema"].get("id", None),
                    json_res["schema"].get("userId", None),
                )
            return
        except Exception as e:
            # err_msg = "Either the schema does not exist or does not belong to you."
            print("Failed to fetch your schema: {}".format(str(e)))
            return None

    def __validate_bucket_name(bucket_name: str) -> str:
        """Validate the bucket name, to check if it is supported

        Args:
            bucket_name (str): Bucket name

        Returns:
            str : Bucket name
        """
        if not bucket_name:
            return DEFAULT_BUCKET
        if bucket_name not in bdb_constants.ALLOWED_BUCKET_NAMES:
            print(f"{bdb_constants.TEXT_COLOR_WARNING}Warning: Bucket name that you have provided is not supported, using the default bucket.{bdb_constants.TEXT_COLOR_ENDC}")
            return DEFAULT_BUCKET
        return bucket_name

    def __validate_api_key(self, api_key: str, database_name: str) -> str:
        """Validate the API key and check if the user is authorized to access the database.

        Args:
            arg1 (str): API Key
            arg2 (str): Database Name

        Returns:
            str : Organization name
        """

        url = bdb_constants.BASE_URL + validate_api_key_url
        params = {"apiKey": api_key, "databaseName": database_name}

        if debug_mode:
            print("url:", url)
            print("params:", params)

        try:
            response = requests.post(url, params=params)
            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if debug_mode:
                print("Validate API key result: ", response.json())
            json_res = response.json()
            if json_res.get("organizationName", None):
                return json_res["organizationName"]
            return
        except Exception as e:
            raise Exception("Failed to validate your API key: {}".format(str(e)))

    def __get_database_id(self, api_key: str, database_name: str) -> int:
        """Function summary

        Args:
            arg1 (str): API Key
            arg2 (str): Database Name

        Returns:
            int : Database ID
        """

        url = bdb_constants.BASE_URL + get_database_id_url
        params = {"apiKey": api_key, "databaseName": database_name}

        if debug_mode:
            print("url:", url)
            print("params:", params)

        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if debug_mode:
                print("Get database id by name result: ", response.json())
            json_res = json.loads(response.text)
            if json_res.get("database", None):
                return json_res["database"].get("id", None)
            return
        except Exception as e:
            print("Failed to fetch your database: {}".format(str(e)))
            return None

    def __get_database(self, api_key: str, database_name: str) -> int:
        """Function summary

        Args:
            arg1 (str): API Key
            arg2 (str): Database Name

        Returns:
            int : Database ID
        """

        url = bdb_constants.BASE_URL + get_database_id_url
        params = {"apiKey": api_key, "databaseName": database_name}

        if debug_mode:
            print("url:", url)
            print("params:", params)

        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if debug_mode:
                print("Get database id by name result: ", response.json())
            json_res = json.loads(response.text)
            if json_res.get("database", None):
                return json_res["database"]
            return
        except Exception as e:
            print("Failed to fetch your database: {}".format(str(e)))
            return None


if __name__ == "__main__":
    pass