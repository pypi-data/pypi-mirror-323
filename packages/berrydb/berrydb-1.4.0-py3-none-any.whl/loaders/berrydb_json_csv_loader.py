import json

from typing import Any, Callable, Dict, List, Optional, Union

from langchain_core.documents import Document
from langchain_core.document_loaders.base import BaseLoader

class BerryDBJSONCSVLoader(BaseLoader):
  """Loads a JSON file using a jq schema.

  Example:
      [{"text": ...}, {"text": ...}, {"text": ...}] -> schema = .[].text
      {"key": [{"text": ...}, {"text": ...}, {"text": ...}]} -> schema = .key[].text
      ["", "", ""] -> schema = .[]
  """

  def __init__(
    self,
    json_data: Union[List, Dict],
    #jq_schema: str,
    content_key: Optional[str] = None,
    metadata_func: Optional[Callable[[Dict, Dict], Dict]] = None,
    text_content: bool = True
  ):
    """Initialize the JSONLoader.

    Args:
        json_data (Union[List, Dict]): JSON data to be parsed.
        jq_schema (str): The jq schema to use to extract the data or text from
            the JSON.
        content_key (str): The key to use to extract the content from the JSON if
            the jq_schema results to a list of objects (dict).
        metadata_func (Callable[Dict, Dict]): A function that takes in the JSON
            object extracted by the jq_schema and the default metadata and returns
            a dict of the updated metadata.
        text_content (bool): Boolean flag to indicate whether the content is in
            string format, default to True.
    """
    # try:
        #import jq  # noqa:F401
    # except ImportError:
    #     raise ImportError(
    #         "jq package not found, please install it with `pip install jq`"
    #     )
    self._json_data = json_data
    #self._jq_schema = jq.compile(jq_schema)
    self._content_key = content_key
    self._metadata_func = metadata_func
    self._text_content = text_content

  def load(self) -> List[Document]:
    """Load and return documents from the JSON file."""
    #pdb.set_trace()
    docs: List[Document] = []
    self._parse(self._json_data, docs)
    return docs

  def _parse(self, content: str, docs: List[Document]) -> None:
    """Convert given content to documents."""
    data = content #self._jq_schema.input(content)
    page_content = ''
    # Perform some validation
    # This is not a perfect validation, but it should catch most cases
    # and prevent the user from getting a cryptic error later on.
    if self._content_key is not None:
      self._validate_content_key(data)

    #data = data.all()
    for i, sample in enumerate(data, len(docs) + 1):
      metadata = dict(
          source='json input',
          row=i,
      )
      hyphen = '-'
      text = self._get_text(sample=sample, metadata=metadata)
      for k, v in text.items():
          page_content = "\n".join(f"{k.strip()}: {str(v).strip()}" for k, v in text.items())
      print(f'\n{hyphen *  10}\n\n {page_content}')
      docs.append(Document(page_content=page_content, metadata=metadata))

  def _get_text(self, sample: Any, metadata: dict) -> str:
    """Convert sample to string format"""
    if self._content_key is not None:
      content = sample.get(self._content_key)
      if self._metadata_func is not None:
          # We pass in the metadata dict to the metadata_func
          # so that the user can customize the default metadata
          # based on the content of the JSON object.
          metadata = self._metadata_func(sample, metadata)
    else:
      content = sample

    if self._text_content and not isinstance(content, str):
      raise ValueError(
          f"Since Text_content is true, the Expected page_content is string, got {type(content)} instead. \
              Set `text_content=False` if the desired input for \
              `page_content` is not a string \
              The loader expects the sent in content to resolve to a Dict object eventually"
      )

    # In case the text is None, set it to an empty string
    elif isinstance(content, str):
      content = json.loads(str)
      if not isinstance(content, dict):
        raise ValueError(
          f"Unable to convert Text Content to a Dict object, converted type from Text is {type(content)}. \
              Set `text_content=False` if the desired input for \
              `page_content` is not a string \
              The loader expects the sent in content to resolve to a Dict object eventually"
      )
      return content
    elif isinstance(content, dict):
      return content
    else:
      raise ValueError(
          f"The loader expects the sent in content to resolve to a Dict object eventually \
            If you are passing a string as content, make sure that: \
            1. Text_content is set to true \
            2. The passed in string(text content) can resolve to a Dict object"
      )

  def _validate_content_key(self, data: Any) -> None:
    """Check if a content key is valid"""
    sample = data.first()
    if not isinstance(sample, dict):
      raise ValueError(
          f"Expected the jq schema to result in a list of objects (dict), \
              so sample must be a dict but got `{type(sample)}`"
      )

    if sample.get(self._content_key) is None:
      raise ValueError(
          f"Expected the jq schema to result in a list of objects (dict) \
              with the key `{self._content_key}`"
      )

    if self._metadata_func is not None:
      sample_metadata = self._metadata_func(sample, {})
      if not isinstance(sample_metadata, dict):
        raise ValueError(
            f"Expected the metadata_func to return a dict but got \
                `{type(sample_metadata)}`"
        )
