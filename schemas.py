from pydantic import BaseModel
from typing import Optional
import datetime

class APIKeyCreate(BaseModel):
    name: Optional[str] = "Untitled Key"
    model_name: str

class APIKeyResponse(BaseModel):
    id: int
    name: str
    secret_key_display: str
    created_at: datetime.datetime
    project_access: str
    
    class Config:
        from_attributes = True