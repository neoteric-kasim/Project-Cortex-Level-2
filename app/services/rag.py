import os
import io
import pandas as pd
from dotenv import load_dotenv

from azure.storage.filedatalake import DataLakeServiceClient

from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.llms.azure_openai import AzureOpenAI

load_dotenv()

llm = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    api_version="2024-12-01-preview"
)

Settings.llm = llm
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

index = None

def load_index():
    global index

    print("📂 Loading parquet from ADLS...")

    conn_str = os.getenv("ADLS_CONNECTION_STRING")
    file_system = os.getenv("FILE_SYSTEM_NAME")

    if not conn_str:
        raise ValueError("ADLS_CONNECTION_STRING not found in .env")

    if not file_system:
        raise ValueError("FILE_SYSTEM_NAME not found in .env")

    file_path = "Kasim/Gold/userdata.parquet"

    print("🔗 Connecting to ADLS...")
    service_client = DataLakeServiceClient.from_connection_string(conn_str)
    fs_client = service_client.get_file_system_client(file_system)
    file_client = fs_client.get_file_client(file_path)

    print("⬇️ Downloading file...")
    download = file_client.download_file()
    file_bytes = download.readall()

    print("📊 Reading parquet into pandas...")
    df = pd.read_parquet(io.BytesIO(file_bytes))

    df = df.head(50)

    print("🧠 Creating documents...")

    documents = [
        Document(
            text=f"""
            Name: {row.get('first_name', '')} {row.get('last_name', '')}
            Email: {row.get('email', '')}
            Country: {row.get('country', '')}
            Gender: {row.get('gender', '')}
            Salary: {row.get('salary', '')}
            Job Title: {row.get('title', '')}
            Comments: {row.get('comments', '')}
            """
        )
        for _, row in df.iterrows()
    ]

    print("📦 Building index...")
    index = VectorStoreIndex.from_documents(documents)

    print("✅ Index created!")

def query_index(question: str):
    global index

    if index is None:
        return "Index not loaded"

    query_engine = index.as_query_engine(
        similarity_top_k=5,
        response_mode="compact"
    )

    response = query_engine.query(question)

    return str(response)