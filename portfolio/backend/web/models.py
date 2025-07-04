from . import db
from datetime import datetime


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    github_url = db.Column(db.String(255))
    live_demo_url = db.Column(db.String(255))
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to project_skills
    skills = db.relationship("ProjectSkill", back_populates="project", cascade="all, delete-orphan")


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to project_skills
    projects = db.relationship("ProjectSkill", back_populates="skill", cascade="all, delete-orphan")


class ProjectSkill(db.Model):
    __tablename__ = "project_skills"

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Backrefs
    project = db.relationship("Project", back_populates="skills")
    skill = db.relationship("Skill", back_populates="projects")


class Contact(db.Model):
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    message = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
