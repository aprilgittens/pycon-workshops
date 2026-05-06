from os import environ
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores.azure_cosmos_db import AzureCosmosDBVectorSearch



load_dotenv(override=False)


client: MongoClient | None = None
vector_store: AzureCosmosDBVectorSearch | None=None


def get_embeddings_client() -> AzureOpenAIEmbeddings:
    azure_endpoint = environ.get("AZURE_OPENAI_ENDPOINT")
    azure_api_key = environ.get("AZURE_OPENAI_API_KEY")
    azure_api_version = environ.get("AZURE_OPENAI_API_VERSION")
    azure_deployment = environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

    missing = []
    if not azure_endpoint:
        missing.append("AZURE_OPENAI_ENDPOINT")
    if not azure_api_key:
        missing.append("AZURE_OPENAI_API_KEY")
    if not azure_api_version:
        missing.append("AZURE_OPENAI_API_VERSION")
    if not azure_deployment:
        missing.append("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

    if missing:
        missing_vars = ", ".join(missing)
        raise ValueError(
            f"Missing required Azure OpenAI settings: {missing_vars}. "
            "Set them in your environment or .env file before starting the API."
        )

    return AzureOpenAIEmbeddings(
        azure_endpoint=azure_endpoint,
        api_key=azure_api_key,
        api_version=azure_api_version,
        azure_deployment=azure_deployment,
    )


def mongodb_init():
    MONGO_CONNECTION_STRING = environ.get("MONGO_CONNECTION_STRING")
    DB_NAME = "travel"
    COLLECTION_NAME = "ships"
    INDEX_NAME = "vectorSearchIndex"

    global client, vector_store
    client = MongoClient(MONGO_CONNECTION_STRING)
    vector_store = AzureCosmosDBVectorSearch.from_connection_string(MONGO_CONNECTION_STRING,
                                                                    DB_NAME + "." + COLLECTION_NAME,
                                                                    get_embeddings_client(),
                                                                    index_name=INDEX_NAME )                                                                  


mongodb_init()

