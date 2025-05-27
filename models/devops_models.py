from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WorkItem(BaseModel):
    id: int
    parent_id: Optional[int] = None
    title: str
    description: Optional[str] = ""
    status: str
    created_at: Optional[datetime] = None

    @classmethod
    def from_api_workitem(cls, data: dict):
        return cls(
            id=data.get("id"),
            title=data.get("fields", {}).get("System.Title"),
            description=data.get("fields", {}).get("System.Description"),
            status=data.get("fields", {}).get("System.State"),
            created_at=data.get("fields", {}).get("System.CreatedDate")
        )
    
    def to_prompt_string(self) -> str:
        return (
            f"ID: {self.id}\n"
            f"Title: {self.title}\n"
            f"Status: {self.status}\n"
            f"Created At: {self.created_at}\n"
            f"Description: {self.description or 'No description'}"
        )

class DevOpsTask(BaseModel):
    parent_id: int
    title: str
    description: Optional[str] = ""
    created_at: Optional[datetime] = None

    @classmethod
    def from_api_task(cls, data: dict):
        return cls(
            parent_id=data.get("id"),
            title=data.get("fields", {}).get("System.Title"),
            description=data.get("fields", {}).get("System.Description"),
            status=data.get("fields", {}).get("System.State"),
            created_at=data.get("fields", {}).get("System.CreatedDate")
        )