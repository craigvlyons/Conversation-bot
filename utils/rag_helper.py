import hashlib
import numpy as np
import logging
from datetime import datetime, timezone
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from urllib.parse import quote_plus
from utils.db_connection import get_mongo_client
from utils.constants import LOG_LEVEL_VALUE

# Initialize logging
logging.basicConfig(level=LOG_LEVEL_VALUE, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# RAGHelper class for managing memory chunks with Azure MongoDB
class RAGHelper:
    def __init__(self, collection_name="memory_chunks"):
        logger.info(f"Initializing RAGHelper with collection: {collection_name}")
        self.client = get_mongo_client()  # <-- Uses centralized connection
        self.db = self.client["rag_memory"]
        self.collection = self.db[collection_name]
        self.embedder = None  # SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("RAGHelper initialized")

    def embed_text(self, text: str):
        if not self.embedder:
            logger.info("Loading SentenceTransformer model for embeddings")
            self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        return self.embedder.encode(text).tolist()

    def add_memory(self, text: str, category="general"):
        logger.info(f"Adding memory: category={category}, text={text[:60]}...")
        embedding = self.embed_text(text)
        memory_id = hashlib.md5(f"{text}_{category}".encode()).hexdigest()
        timestamp = datetime.now(timezone.utc).isoformat()  
        logger.debug(f"Generated memory_id: {memory_id}, timestamp: {timestamp}")

        result = self.collection.replace_one(
            {"_id": memory_id},
            {
                "_id": memory_id,
                "content": text,
                "embedding": embedding,
                "category": category,
                "timestamp": timestamp
            },
            upsert=True
        )
        logger.info(f"Memory {'updated' if result.modified_count else 'inserted'} (id={memory_id})")
        return memory_id

    def query_memory(self, query: str, top_k=3, category=None):
        logger.info(f"Querying memory: query='{query[:60]}...', top_k={top_k}, category={category}")
        query_vec = np.array(self.embed_text(query))
        results = []

        # Optionally filter by category
        filter_query = {"category": category} if category else {}
        logger.debug(f"MongoDB filter: {filter_query}")

        for doc in self.collection.find(filter_query):
            vec = np.array(doc["embedding"])
            sim = self.cosine_similarity(query_vec, vec)
            logger.debug(f"Doc id={doc['_id']} sim={sim:.4f}")
            results.append((sim, doc["content"]))

        results.sort(reverse=True)
        logger.info(f"Returning top {min(top_k, len(results))} results from {len(results)} candidates")
        return [r[1] for r in results[:top_k]]
    
    def query_today(self, category="note"):
        today = datetime.now(timezone.utc).date()
        logger.info(f"Querying today's memories for category: {category}, date: {today}")
        results = list(self.collection.find({
            "category": category,
            "$expr": {
                "$eq": [
                    {"$dateToString": {"format": "%Y-%m-%d", "date": {"$toDate": "$timestamp"}}},
                    today.isoformat()
                ]
            }
        }))
        logger.info(f"Found {len(results)} memories for today.")
        return results

    @staticmethod
    def cosine_similarity(a, b):
        sim = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        logger.debug(f"Cosine similarity: {sim:.4f}")
        return sim