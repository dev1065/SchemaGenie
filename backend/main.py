from database import get_db
from fastapi import Depends, FastAPI, HTTPException
from models import Conversation, Message, Project
from schemas import (
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    RequirementCreate,
    RequirementResponse,
    RequirementUpdate,
)
from services.conversation_service import generate_conversation_response
from services.requirement_service import (
    create_requirement,
    delete_requirement,
    get_requirements,
    update_requirement,
)
from sqlalchemy.orm import Session

app = FastAPI()


@app.get("/")
def hello_world():
    return {"message": "Welcome to SchemaGenie"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/projects", response_model=ProjectResponse)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db)  # noqa: B008
):
    project = Project(
        name=project_data.name,
        description=project_data.description,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    return project


@app.get("/projects", response_model=list[ProjectResponse])
def get_projects(db: Session = Depends(get_db)):  # noqa: B008
    projects = db.query(Project).all()

    return projects


@app.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):  # noqa: B008
    project = db.query(Project).filter(Project.id == project_id).first()

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.patch("/projects/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),  # noqa: B008
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    if project_data.name is not None:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description

    db.commit()
    db.refresh(project)

    return project


@app.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db)  # noqa: B008
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()

    return {"message": "project deleted successfully"}


@app.post("/projects/{project_id}/conversations", response_model=ConversationResponse)
def create_conversation(
    project_id: int,
    db: Session = Depends(get_db)  # noqa: B008
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    conversation = Conversation(
        project_id=project_id
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


@app.get("/projects/{project_id}/conversations", response_model=list[ConversationResponse])
def get_conversations(
    project_id: int,
    db: Session = Depends(get_db)  # noqa: B008
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    conversations = (
        db.query(Conversation).filter(
            Conversation.project_id == project_id).all()
    )
    return conversations


@app.get("/conversations/{conversation_id}",
         response_model=ConversationResponse)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)  # noqa: B008
):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@app.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageResponse
)
def create_message(
    conversation_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db)  # noqa: B008
):
    try:
        return generate_conversation_response(
            conversation_id=conversation_id,
            user_content=message_data.content,
            db=db
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


@app.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db)  # noqa: B008
):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at).all()
    )

    return messages


@app.post(
    "/conversations/{conversation_id}/requirements",
    response_model=RequirementResponse
)
def create_requirement_endpoint(
    conversation_id: int,
    requirement_data: RequirementCreate,
    db: Session = Depends(get_db)  # noqa: B008
):
    try:
        return create_requirement(
            conversation_id=conversation_id,
            key=requirement_data.key,
            value=requirement_data.value,
            db=db
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


@app.get(
    "/conversations/{conversation_id}/requirements",
    response_model=list[RequirementResponse]
)
def get_requirements_endpoint(
    conversation_id: int,
    db: Session = Depends(get_db)  # noqa: B008
):
    try:
        return get_requirements(
            conversation_id=conversation_id,
            db=db
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


@app.patch(
    "/requirements/{requirement_id}",
    response_model=RequirementResponse
)
def update_requirement_endpoint(
    requirement_id: int,
    requirement_data: RequirementUpdate,
    db: Session = Depends(get_db)  # noqa: B008
):
    try:
        return update_requirement(
            requirement_id=requirement_id,
            value=requirement_data.value,
            db=db
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


@app.delete(
    "/requirements/{requirement_id}"
)
def delete_requirement_endpoint(
    requirement_id: int,
    db: Session = Depends(get_db)  # noqa: B008
):
    try:
        delete_requirement(
            requirement_id=requirement_id,
            db=db
        )
        return {"message": "requirement deleted successfully"}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
