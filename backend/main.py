from database import get_db
from fastapi import Depends, FastAPI, HTTPException
from models import Conversation, Project
from schemas import ConversationResponse, ProjectCreate, ProjectResponse, ProjectUpdate
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
