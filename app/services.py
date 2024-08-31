import os
import subprocess
import git
import psutil
from .models import Project
from typing import List, Optional

projects = []

def list_projects() -> List[Project]:
    # Verificar status dos projetos
    for project in projects:
        if not is_port_in_use(project.hostPort):
            project.status = "stopped"
    return projects

def is_port_in_use(port: int) -> bool:
    for conn in psutil.net_connections(kind='inet'):
        if conn.laddr.port == port:
            return True
    return False

def validate_repo(repo_url: str, name: str) -> bool:    
    try:
        git.Repo.clone_from(repo_url, name, depth=1)
        return True
    except:
        return False

def start_project(project_data: Project) -> Project:
    if is_port_in_use(project_data.hostPort):
        raise ValueError("Port is already in use")
    
    if not validate_repo(project_data.repo, project_data.name):
        print(project_data)
        raise ValueError("Repository does not exist or is not accessible")
    
    repo_path = f"/tmp/{project_data.name}"
    if not os.path.exists(repo_path):
        repo = git.Repo.clone_from(project_data.repo, repo_path, branch=project_data.branch)
    else:
        repo = git.Repo(repo_path)
        repo.git.checkout(project_data.branch)
        repo.remotes.origin.pull()

    # Executar a aplicação na porta especificada
    subprocess.run(f"nvm use {project_data.nodeVersion}", shell=True, cwd=repo_path)
    subprocess.run("npm cache clean --force", shell=True, cwd=repo_path)
    subprocess.run("npm install", shell=True, cwd=repo_path)
    subprocess.Popen(f"npm start -- --port {project_data.hostPort}", shell=True, cwd=repo_path)
    
    project_data.status = "running"
    projects.append(project_data)
    return project_data

def stop_project(id: str):
    project = next((p for p in projects if p.id == id), None)
    if project and project.status == "running":
        for proc in psutil.process_iter(['pid', 'cmdline']):
            try:
                if proc.info['cmdline'] and f"--port {project.hostPort}" in ' '.join(proc.info['cmdline']):
                    proc.terminate()
                    project.status = "stopped"
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        else:
            raise ValueError("Process not found or already stopped")
    else:
        raise ValueError("Project not found or already stopped")

def restart_project(id: str):
    project = next((p for p in projects if p.id == id), None)
    if project and project.status == "stopped":
        return start_project(project)
    else:
        raise ValueError("Project not found or is already running")
