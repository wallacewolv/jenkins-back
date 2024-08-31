from typing import Optional
from pydantic import BaseModel
from uuid import uuid4

class Project(BaseModel):
    id: str = uuid4().hex
    name: str
    repo: str
    branch: str
    hostPort: int
    type: str
    nodeVersion: str
    status: str = "stopped"
