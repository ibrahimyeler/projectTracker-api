from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas
from datetime import date

def get_projects(db: Session, tag: str = None, search: str = None):
    query = db.query(models.Project)
    if tag:
        query = query.filter(models.Project.tags.contains(tag))
    if search:
        query = query.filter(models.Project.title.contains(search))
    return query.all()

def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def get_project(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def update_project(db: Session, project_id: int, project: schemas.ProjectCreate):
    db_project = get_project(db, project_id)
    if not db_project:
        return None  # Proje bulunamazsa None döner
    for key, value in project.dict().items():
        setattr(db_project, key, value)
    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project(db: Session, project_id: int):
    db_project = get_project(db, project_id)
    if not db_project:
        return None  # Silinecek proje bulunamazsa None döner
    db.delete(db_project)
    db.commit()
    return db_project

def create_task(db: Session, project_id: int, task: schemas.TaskCreate):
    db_task = models.Task(**task.dict(), project_id=project_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks_by_project(db: Session, project_id: int, status: str = None):
    query = db.query(models.Task).filter(models.Task.project_id == project_id)
    if status:
        query = query.filter(models.Task.status == status)
    return query.all()

def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def update_task(db: Session, task_id: int, task: schemas.TaskUpdate):
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    for key, value in task.dict(exclude_unset=True).items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    db.delete(db_task)
    db.commit()
    return db_task

def create_note(db: Session, project_id: int, note: schemas.NoteCreate):
    db_note = models.Note(**note.dict(), project_id=project_id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def get_notes_by_project(db: Session, project_id: int):
    return db.query(models.Note).filter(models.Note.project_id == project_id).all()

def get_note(db: Session, note_id: int):
    return db.query(models.Note).filter(models.Note.id == note_id).first()

def update_note(db: Session, note_id: int, note: schemas.NoteUpdate):
    db_note = get_note(db, note_id)
    if not db_note:
        return None
    db_note.content = note.content
    db.commit()
    db.refresh(db_note)
    return db_note

def delete_note(db: Session, note_id: int):
    db_note = get_note(db, note_id)
    if not db_note:
        return None
    db.delete(db_note)
    db.commit()
    return db_note

def get_upcoming_tasks(db: Session):
    today = date.today()
    return db.query(models.Task).filter(
        models.Task.due_date != None,
        models.Task.due_date >= today,
        models.Task.status != "done"
    ).order_by(models.Task.due_date.asc()).all()

def get_dashboard_stats(db: Session):
    # Aktif proje sayısı (status != "completed")
    active_projects = db.query(models.Project).filter(models.Project.status != "completed").count()
    
    # Toplam proje sayısı
    total_projects = db.query(models.Project).count()
    
    # Toplam görev sayısı
    total_tasks = db.query(models.Task).count()
    
    # Tamamlanan görev sayısı (status == "done")
    completed_tasks = db.query(models.Task).filter(models.Task.status == "done").count()
    
    # Son güncellenen projeler (son 5 proje)
    recent_projects = db.query(models.Project).order_by(models.Project.id.desc()).limit(5).all()
    
    # Proje durumlarına göre dağılım
    project_status_stats = db.query(
        models.Project.status,
        func.count(models.Project.id).label('count')
    ).group_by(models.Project.status).all()
    
    # Görev durumlarına göre dağılım
    task_status_stats = db.query(
        models.Task.status,
        func.count(models.Task.id).label('count')
    ).group_by(models.Task.status).all()
    
    return {
        "active_projects": active_projects,
        "total_projects": total_projects,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
        "recent_projects": recent_projects,
        "project_status_stats": [{"status": status, "count": count} for status, count in project_status_stats],
        "task_status_stats": [{"status": status, "count": count} for status, count in task_status_stats]
    }

def export_all_data(db: Session):
    # Tüm projeleri al
    projects = db.query(models.Project).all()
    
    # Her proje için görevleri ve notları al
    export_data = []
    for project in projects:
        project_data = {
            "id": project.id,
            "title": project.title,
            "description": project.description,
            "status": project.status,
            "tags": project.tags,
            "start_date": project.start_date.isoformat() if project.start_date else None,
            "end_date": project.end_date.isoformat() if project.end_date else None,
            "tasks": [],
            "notes": []
        }
        
        # Projenin görevlerini ekle
        tasks = db.query(models.Task).filter(models.Task.project_id == project.id).all()
        for task in tasks:
            task_data = {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "due_date": task.due_date.isoformat() if task.due_date else None
            }
            project_data["tasks"].append(task_data)
        
        # Projenin notlarını ekle
        notes = db.query(models.Note).filter(models.Note.project_id == project.id).all()
        for note in notes:
            note_data = {
                "id": note.id,
                "content": note.content
            }
            project_data["notes"].append(note_data)
        
        export_data.append(project_data)
    
    return export_data