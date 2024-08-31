from fastapi import FastAPI, HTTPException, BackgroundTasks
from app.schemas import ProjectCreate
from app.models import Project
from app.services import list_projects, start_project, stop_project, restart_project, is_port_in_use
import threading
import time

app = FastAPI()

# Lista de projetos gerenciados
projects = []

def monitor_projects():
    while True:
        for project in projects:
            if not is_port_in_use(project.hostPort) and project.status == "running":
                project.status = "stopped"
                print(f"{project.name} stopped.")
            elif is_port_in_use(project.hostPort) and project.status == "stopped":
                project.status = "running"
                print(f"{project.name} is running.")
        time.sleep(5)  # Verificar a cada 5 segundos

@app.on_event("startup")
def on_startup():
    # Inicia a thread de monitoramento quando o servidor inicia
    monitor_thread = threading.Thread(target=monitor_projects, daemon=True)
    monitor_thread.start()

@app.get("/projects")
def get_projects():
    return list_projects()

@app.post("/projects")
def create_project(project_data: ProjectCreate):
    try:
        project = Project(**project_data.dict())
        projects.append(project)
        return start_project(project)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/projects/{id}/stop")
def stop_project_endpoint(id: str):
    try:
        stop_project(id)
        return {"message": "Project stopped successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/projects/{id}/restart")
def restart_project_endpoint(id: str):
    try:
        return restart_project(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
