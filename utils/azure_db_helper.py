"""
    Azure DevOps Database Helper Module, for the Azrure Devops tool.
    This module provides functionality to log work items and tasks in an Azure database
"""
from utils.db_connection import get_mongo_client
from datetime import datetime, timezone
import hashlib

class AzureDevOpsDBHelper:
    def __init__(self, collection_name="devops_activity"):
        client = get_mongo_client()
        self.collection = client["activity_log"][collection_name]

    def log_task(self, parent_id: int, title: str, description: str):
        _id = hashlib.md5(f"{parent_id}-{title}".encode()).hexdigest()
        timestamp = datetime.now(timezone.utc).isoformat()

        self.collection.replace_one(
            {"_id": _id},
            {
                "_id": _id,
                "parent_id": parent_id,
                "title": title,
                "description": description,
                "timestamp": timestamp
            },
            upsert=True
        )

    # get task
    # get work items
    # delete task
    # delete work item if its now status done.
    # update work items 