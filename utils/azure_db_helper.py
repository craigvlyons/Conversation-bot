"""
    Azure DevOps Database Helper Module, for the Azrure Devops tool.
    This module provides functionality to log work items and tasks in an Azure database
"""
from utils.db_connection import get_mongo_client
from datetime import datetime, timezone
import hashlib
from models.devops_models import WorkItem, DevOpsTask
from typing import Optional, List
import logging
from utils.constants import LOG_LEVEL_VALUE
logging.basicConfig(level=LOG_LEVEL_VALUE, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AzureDevOpsDBHelper:
    def __init__(self, collection_name="devops_activity"):
        client = get_mongo_client()
        self.collection = client["activity_log"][collection_name]
        # self.clear_all()  # Optional: for fresh test state
        # logger.info("clear_all() called on AzureDevOpsDBHelper, collection cleared.")

    def log_task(self, devops_task: DevOpsTask):
        _id = hashlib.md5(f"{devops_task.parent_id}-{devops_task.title}".encode()).hexdigest()
        timestamp = datetime.now(timezone.utc).isoformat()

        self.collection.replace_one(
            {"_id": _id},
            {
                "_id": _id,
                "parent_id": devops_task.parent_id,
                "title": devops_task.title,
                "description": devops_task.description,
                "timestamp": timestamp
            },
            upsert=True
        )

    def log_work_item(self, work_item: WorkItem):
        timestamp = datetime.now(timezone.utc).isoformat()

        self.collection.replace_one(
            {"_id": work_item.id},
            {
                "_id": work_item.id,
                "parent_id": work_item.parent_id,
                "title": work_item.title,
                "description": work_item.description,
                "status": work_item.status,
                "timestamp": timestamp
            },
            upsert=True
        )

    def get_work_item_by_id(self, id: int) -> Optional[WorkItem]:
        doc = self.collection.find_one({"_id": id})
        if doc:
            doc["id"] = doc.pop("_id")  # Convert _id to id for model
            return WorkItem(**doc)
        return None

    def get_work_item(self, parent_id: int, title: str):
        _id = hashlib.md5(f"{parent_id}-{title}".encode()).hexdigest()
        doc = self.collection.find_one({"_id": _id})
        if doc:
            doc["id"] = doc.pop("_id")
        return doc

    def get_task(self, parent_id: int, title: str):
        _id = hashlib.md5(f"{parent_id}-{title}".encode()).hexdigest()
        doc = self.collection.find_one({"_id": _id})
        if doc:
            doc["id"] = doc.pop("_id")
        return doc

    def get_tasks(self, parent_id: int):
        docs = list(self.collection.find({"parent_id": parent_id}))
        for doc in docs:
            if "_id" in doc:
                doc["id"] = doc.pop("_id")
        return docs

    def get_work_items(self):
        docs = list(self.collection.find())
        for doc in docs:
            if "_id" in doc:
                doc["id"] = doc.pop("_id")
        return docs

    def delete_task(self, parent_id: int, title: str):
        _id = hashlib.md5(f"{parent_id}-{title}".encode()).hexdigest()
        result = self.collection.delete_one({"_id": _id})
        return result.deleted_count

    def delete_work_item_and_tasks(self, parent_id: int):
        result = self.collection.delete_many({"parent_id": parent_id})
        return result.deleted_count

    def update_task_status(self, parent_id: int, title: str, status: str):
        _id = hashlib.md5(f"{parent_id}-{title}".encode()).hexdigest()
        result = self.collection.update_one(
            {"_id": _id},
            {"$set": {"status": status}}
        )
        return result.modified_count

    def clear_all(self):
        result = self.collection.delete_many({})
        logger.info(f"Cleared {result.deleted_count} documents from the collection.")