from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.database import engine, SessionLocal, Base
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import Task, TaskCreate, TaskUpdate, Note, NoteCreate, NoteUpdate, DashboardStats, ExportData
from fastapi.responses import JSONResponse, PlainTextResponse
from datetime import datetime
import csv
import io

# Veritabanı tablolarını oluştur
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Project Tracker API",
    description="A FastAPI-based project tracking system",
    version="1.0.0"
)

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# CORS ayarları (production için)
import os

# Environment'dan CORS origins'i al
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB oturumu dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------- Proje Endpoint'leri -----------

@app.get("/projects", response_model=list[schemas.Project])
def read_projects(
    tag: str = Query(None),
    search: str = Query(None),
    db: Session = Depends(get_db)
):
    return crud.get_projects(db, tag=tag, search=search)

@app.post("/projects", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    return crud.create_project(db, project)

@app.get("/projects/{project_id}", response_model=schemas.Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.put("/projects/{project_id}", response_model=schemas.Project)
def update_project(project_id: int, project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    updated = crud.update_project(db, project_id, project)
    if not updated:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated

@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_project(db, project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}

@app.post("/projects/{project_id}/tasks", response_model=Task)
def create_task_for_project(project_id: int, task: TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, project_id, task)

@app.get("/projects/{project_id}/tasks", response_model=list[Task])
def list_tasks_for_project(project_id: int, status: str = Query(None), db: Session = Depends(get_db)):
    return crud.get_tasks_by_project(db, project_id, status=status)

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    updated = crud.update_task(db, task_id, task)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}

@app.get("/tasks/upcoming", response_model=list[Task])
def get_upcoming_tasks(db: Session = Depends(get_db)):
    return crud.get_upcoming_tasks(db)

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/projects/{project_id}/notes", response_model=Note)
def create_note_for_project(project_id: int, note: NoteCreate, db: Session = Depends(get_db)):
    return crud.create_note(db, project_id, note)

@app.get("/projects/{project_id}/notes", response_model=list[Note])
def list_notes_for_project(project_id: int, db: Session = Depends(get_db)):
    return crud.get_notes_by_project(db, project_id)

@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = crud.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: int, note: NoteUpdate, db: Session = Depends(get_db)):
    updated = crud.update_note(db, note_id, note)
    if not updated:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated

@app.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_note(db, note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted successfully"}

@app.get("/dashboard", response_model=DashboardStats)
def get_dashboard(db: Session = Depends(get_db)):
    return crud.get_dashboard_stats(db)

@app.get("/export/json", response_model=ExportData)
def export_json(db: Session = Depends(get_db)):
    export_data = crud.export_all_data(db)
    
    # İstatistikleri hesapla
    total_projects = len(export_data)
    total_tasks = sum(len(project["tasks"]) for project in export_data)
    total_notes = sum(len(project["notes"]) for project in export_data)
    
    return {
        "projects": export_data,
        "export_date": datetime.now().isoformat(),
        "total_projects": total_projects,
        "total_tasks": total_tasks,
        "total_notes": total_notes
    }

@app.get("/export/csv")
def export_csv(db: Session = Depends(get_db)):
    export_data = crud.export_all_data(db)
    
    # CSV oluştur
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Başlık satırı
    writer.writerow(["Project ID", "Project Title", "Project Status", "Task ID", "Task Title", "Task Status", "Task Due Date", "Note ID", "Note Content"])
    
    # Verileri yaz
    for project in export_data:
        project_id = project["id"]
        project_title = project["title"]
        project_status = project["status"]
        
        # Görevler
        for task in project["tasks"]:
            writer.writerow([
                project_id,
                project_title,
                project_status,
                task["id"],
                task["title"],
                task["status"],
                task["due_date"] or "",
                "",
                ""
            ])
        
        # Notlar
        for note in project["notes"]:
            writer.writerow([
                project_id,
                project_title,
                project_status,
                "",
                "",
                "",
                "",
                note["id"],
                note["content"]
            ])
    
    output.seek(0)
    return PlainTextResponse(output.getvalue(), media_type="text/csv")