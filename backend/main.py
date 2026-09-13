from database import get_db
from fastapi import Depends, FastAPI
from models import Project
from schemas import ProjectCreate, ProjectResponse
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

