from datetime import datetime

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ConversationResponse(BaseModel):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class MessageCreate(BaseModel):
    role: str
    content: str


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
