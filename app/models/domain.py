from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid

class User(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    resumes: List["Resume"] = Relationship(back_populates="user")
    reports: List["AnalysisReport"] = Relationship(back_populates="user")
    job_descriptions: List["JobDescriptionLibrary"] = Relationship(back_populates="user")
    cover_letters: List["CoverLetter"] = Relationship(back_populates="user")
    profile: Optional["UserProfile"] = Relationship(back_populates="user")

class UserProfile(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    career_goal: Optional[str] = None
    target_roles: Optional[str] = None # Comma separated
    experience_level: Optional[str] = None
    
    user: User = Relationship(back_populates="profile")

class JobDescriptionLibrary(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    title: str
    company: Optional[str] = None
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: User = Relationship(back_populates="job_descriptions")

class Resume(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    filename: str
    file_path: str
    file_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: User = Relationship(back_populates="resumes")
    reports: List["AnalysisReport"] = Relationship(back_populates="resume")
    versions: List["ResumeVersion"] = Relationship(back_populates="original_resume")

class ResumeVersion(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    resume_id: str = Field(foreign_key="resume.id")
    name: str # e.g. "Software Engineer Tailored"
    content_json: str # The edited resume JSON
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    original_resume: Resume = Relationship(back_populates="versions")

class AnalysisReport(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    resume_id: str = Field(foreign_key="resume.id")
    job_description: Optional[str] = None
    overall_score: int
    result_json: str
    rebuilt_json: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: User = Relationship(back_populates="reports")
    resume: Resume = Relationship(back_populates="reports")

class CoverLetter(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    title: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: User = Relationship(back_populates="cover_letters")
