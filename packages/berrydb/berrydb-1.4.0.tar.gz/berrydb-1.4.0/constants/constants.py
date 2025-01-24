import logging

debug_mode = False
LOGGING_LEVEL = logging.DEBUG

ALLOWED_BUCKET_NAMES = ["BerryDb", "Generic", "Vectors"]

BASE_URL:str | None = None
ML_BACKEND_BASE_URL:str | None = None
BERRY_GPT_BASE_URL:str | None = None
LABEL_STUDIO_BASE_URL:str | None = None

# Text Color
TEXT_COLOR_SUCCESS = '\033[92m'
TEXT_COLOR_WARNING = '\033[93m'
TEXT_COLOR_FAILURE = '\033[91m'
TEXT_COLOR_ENDC = '\033[0m'

# Profile service endpoints
get_schema_id_url = "/profile/schema"
get_database_id_url = "/profile/database"
create_database_url = "/profile/database"
delete_database_url = "/profile/database"
create_schema_url = "/profile/schema"
get_database_list_by_api_key_url = "/profile/database/list-by-api-key"

# Label Studio endpoints
create_label_studio_project_url = "/api/projects"
setup_label_config_url = "/api/projects/{}"
import_label_studio_project_url = "/api/projects/{}/import?commit_to_project=false"
reimport_label_studio_project_url = "/api/projects/{}/reimport"
connect_project_to_ml_url = "/api/ml"
create_annotations_url = "/api/tasks/{}/annotations?project={}"
create_predictions_url = "/api/predictions"

# Berrydb service endpoints
documents_url = "/berrydb/documents"
documents_query_builder_url = "/berrydb/documents/query-builder"
query_url = "/berrydb/query"
document_by_id_url = "/berrydb/documents/{}"
bulk_upsert_documents_url = "/berrydb/documents/bulk"
validate_api_key_url = "/berrydb/validate"
get_embedded_dbs_url = "/berrydb/database/embedded"

# ML backend endpoint
transcription_url = "/transcription"
transcription_yt_url = "/transcription-yt"
caption_url = "/caption"
label_summary_url = "/label-summary"

# Berry GPT backend endpoint
extract_pdf_url = "/extract-pdf"
embed_database_url = "/chat/embed"
chat_with_database_url = "/chat"

# Semantic extraction API endpoints
SEMANTICS_PREDICT_URL = "/profile/semantics/predictions"
SEMANTICS_ANNOTATE_URL = "/profile/semantics/annotations"

# Semantic extraction types
NER_SE_TYPE = "NER"
MEDICAL_NER_SE_TYPE = "Medical NER"
TEXT_CLASSIFICATION_SE_TYPE = "Text Classification"
TEXT_SUMMARIZATION_SE_TYPE = "Text Summarization"
IMAGE_CLASSIFICATION_SE_TYPE = "Image Classification"
IMAGE_CAPTIONING_SE_TYPE = "Image Captioning"
PNEUMONIA_SE_TYPE = "Pneumonia"
ALZHEIMER_SE_TYPE = "Alzheimer"
FASHION_SE_TYPE = "Fashion"
AUDIO_TRANSCRIPTION_SE_TYPE = "Audio Transcription"
TEXT_CLASSIFICATION_SE_TYPE = "Text Classification"

generic_error_message = "Oops! something went wrong. Please try again later."

# Default variables
DEFAULT_BUCKET = "BerryDb"
DEFAULT_TOKENS_PER_MINUTE = 150000
OPEN_AI_EMBEDDINGS_COST_PER_THOUSAND_TOKENS = 0.0001

# LLM related variables
DEFAULT_OPEN_AI_MODEL = "gpt-4o-mini"
DEFAULT_OPEN_AI_TEMPERATURE = 0.5
OPEN_AI_MODEL_TYPE_NAME = "OpenAI"
HUGGING_FACE_MIXTRAL_MODEL = "Mixtral 7B Instruct v0.2"
HUGGING_FACE_MIXTRAL_MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.1"
HUGGING_FACE_LLAMA_MODEL = "LLama 2 7b chat"
HUGGING_FACE_LLAMA_MODEL_ID = "meta-llama/Llama-2-7b-chat"
HUGGING_FACE_FALCON_MODEL = "Falcon 40b"
HUGGING_FACE_FALCON_MODEL_ID = "tiiuae/falcon-40b"
HUGGING_FACE_TEXT_EMBEDDING_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
LANGCHAIN_ENDPOINT = "https://api.smith.langchain.com"

def evaluate_endpoints(berrydb_base_url: str = None):
    global BASE_URL, ML_BACKEND_BASE_URL, BERRY_GPT_BASE_URL, LABEL_STUDIO_BASE_URL

    # BerryDB Base URLs
    if berrydb_base_url is not None:
        from utils.utils import Utils
        berrydb_base_url = Utils.validate_url(berrydb_base_url, "BerryDB")
        BASE_URL = __sanitize_url(berrydb_base_url)
        BERRY_GPT_BASE_URL = BASE_URL + "/gpt"
        ML_BACKEND_BASE_URL = BASE_URL + "/ml-backend"
        LABEL_STUDIO_BASE_URL = BASE_URL + "/annotations"

def __sanitize_url(url :str):
    return url.strip().rstrip('/') if url and isinstance(url, str) else None
