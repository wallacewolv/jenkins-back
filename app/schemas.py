from pydantic import BaseModel

class ProjectCreate(BaseModel):
    name: str
    repo: str
    branch: str
    hostPort: int
    type: str
    nodeVersion: str
