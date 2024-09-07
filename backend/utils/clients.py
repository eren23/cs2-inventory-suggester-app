import os
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


def initialize_clients():
    qdrant_client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
    )
    encoder = SentenceTransformer(
        "Alibaba-NLP/gte-large-en-v1.5", trust_remote_code=True
    )
    return qdrant_client, encoder
