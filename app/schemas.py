from pydantic import BaseModel
from typing import Optional
from datetime import date

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = ""
    status: Optional[str] = "planned"
    tags: Optional[str] = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    
    model_config = {
        "from_attributes": True
    }

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = ""
    status: Optional[str] = "todo"
    due_date: Optional[date] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class Task(TaskBase):
    id: int
    project_id: int
    
    model_config = {
        "from_attributes": True
    }

class NoteBase(BaseModel):
    content: str

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    content: str

class Note(NoteBase):
    id: int
    project_id: int
    
    model_config = {
        "from_attributes": True
    }

class ProjectStatusStat(BaseModel):
    status: str
    count: int

class TaskStatusStat(BaseModel):
    status: str
    count: int

class RecentProject(BaseModel):
    id: int
    title: str
    status: str
    
    model_config = {
        "from_attributes": True
    }

class DashboardStats(BaseModel):
    active_projects: int
    total_projects: int
    total_tasks: int
    completed_tasks: int
    completion_rate: float
    recent_projects: list[RecentProject]
    project_status_stats: list[ProjectStatusStat]
    task_status_stats: list[TaskStatusStat]

class ExportNote(BaseModel):
    id: int
    content: str

class ExportTask(BaseModel):
    id: int
    title: str
    description: str
    status: str
    due_date: Optional[str] = None

class ExportProject(BaseModel):
    id: int
    title: str
    description: str
    status: str
    tags: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    tasks: list[ExportTask]
    notes: list[ExportNote]

class ExportData(BaseModel):
    projects: list[ExportProject]
    export_date: str
    total_projects: int
    total_tasks: int
    total_notes: int