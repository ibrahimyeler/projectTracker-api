from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date
from app.database import Base
from sqlalchemy.orm import relationship

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, default="")
    status = Column(String, default="planned")
    tags = Column(String, default="")
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="project", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, default="")
    status = Column(String, default="todo")
    project_id = Column(Integer, ForeignKey("projects.id"))
    due_date = Column(Date, nullable=True)

    project = relationship("Project", back_populates="tasks")

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, default="")
    project_id = Column(Integer, ForeignKey("projects.id"))

    project = relationship("Project", back_populates="notes")