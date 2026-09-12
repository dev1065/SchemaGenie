from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def hello_world():
    return {"message": "Welcome to SchemaGenie"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
