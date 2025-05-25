import hashlib
import numpy as np
import logging
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from urllib.parse import quote_plus
from utils.db_connection import get_mongo_client

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# RAGHelper class for managing memory chunks with Azure MongoDB
class RAGHelper:
    def __init__(self, collection_name="memory_chunks"):
        self.client = get_mongo_client()  # <-- Uses centralized connection
        self.db = self.client["rag_memory"]
        self.collection = self.db[collection_name]
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_text(self, text: str):
        return self.embedder.encode(text).tolist()

    def add_memory(self, text: str, category="general"):
        embedding = self.embed_text(text)
        memory_id = hashlib.md5(f"{text}_{category}".encode()).hexdigest()
        self.collection.replace_one(
            {"_id": memory_id},
            {
                "_id": memory_id,
                "content": text,
                "embedding": embedding,
                "category": category
            },
            upsert=True
        )
        return memory_id

    def query_memory(self, query: str, top_k=3, category=None):
        query_vec = np.array(self.embed_text(query))
        results = []

        # Optionally filter by category
        filter_query = {"category": category} if category else {}

        for doc in self.collection.find(filter_query):
            vec = np.array(doc["embedding"])
            sim = self.cosine_similarity(query_vec, vec)
            results.append((sim, doc["content"]))

        results.sort(reverse=True)
        return [r[1] for r in results[:top_k]]

    @staticmethod
    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))