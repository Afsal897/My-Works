from flask import Blueprint, jsonify, request
from .models import Project, Skill, ProjectSkill, Contact
from . import db
import re

views = Blueprint("views", __name__)

@views.route("/projects", methods=["GET"])
def get_projects():
    projects = Project.query.all()
    result = []

    for project in projects:
        skills = [ps.skill.name for ps in project.skills]
        result.append({
            "id": project.id,
            "title": project.title,
            "description": project.description,
            "github_url": project.github_url,
            "live_demo_url": project.live_demo_url,
            "image_url": project.image_url,
            "skills": skills
        })

    return jsonify(result)


@views.route("/skills", methods=["POST"])
def create_skill():
    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"error": "Skill name is required"}), 400

    existing = Skill.query.filter_by(name=name).first()
    if existing:
        return jsonify({"error": "Skill already exists", "id": existing.id}), 409

    skill = Skill(name=name)
    db.session.add(skill)
    db.session.commit()

    return jsonify({"id": skill.id, "name": skill.name}), 201


@views.route("/projects", methods=["POST"])
def create_project():
    data = request.get_json()

    title = data.get("title")
    description = data.get("description")
    github_url = data.get("github_url")
    live_demo_url = data.get("live_demo_url")
    image_url = data.get("image_url")
    skill_ids = data.get("skill_ids", [])

    if not title:
        return jsonify({"error": "Project title is required"}), 400

    # Validate skills
    skills = Skill.query.filter(Skill.id.in_(skill_ids)).all()
    if len(skills) != len(skill_ids):
        return jsonify({"error": "Some skill IDs are invalid"}), 400

    # Create the project
    project = Project(
        title=title,
        description=description,
        github_url=github_url,
        live_demo_url=live_demo_url,
        image_url=image_url
    )
    db.session.add(project)
    db.session.flush()  # gets project.id before commit

    # Create bridge table records
    for skill in skills:
        link = ProjectSkill(project_id=project.id, skill_id=skill.id)
        db.session.add(link)

    db.session.commit()

    return jsonify({
        "id": project.id,
        "title": project.title,
        "description": project.description,
        "skills": [{"id": s.id, "name": s.name} for s in skills]
    }), 201


@views.route("/projects/<int:id>", methods=["PUT"])
def update_project(id):
    data = request.get_json()

    title = data.get("title")
    description = data.get("description")
    github_url = data.get("github_url")
    live_demo_url = data.get("live_demo_url")
    image_url = data.get("image_url")
    skill_ids = data.get("skill_ids", [])

    project = Project.query.get(id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    if not title:
        return jsonify({"error": "Project title is required"}), 400

    # Validate skill IDs
    skills = Skill.query.filter(Skill.id.in_(skill_ids)).all()
    if len(skills) != len(skill_ids):
        return jsonify({"error": "Some skill IDs are invalid"}), 400

    # Update project fields
    project.title = title
    project.description = description
    project.github_url = github_url
    project.live_demo_url = live_demo_url
    project.image_url = image_url

    # Clear and update skill links (bridge table)
    ProjectSkill.query.filter_by(project_id=project.id).delete()
    for skill in skills:
        db.session.add(ProjectSkill(project_id=project.id, skill_id=skill.id))

    db.session.commit()

    return jsonify({
        "id": project.id,
        "title": project.title,
        "description": project.description,
        "github_url": project.github_url,
        "live_demo_url": project.live_demo_url,
        "image_url": project.image_url,
        "skills": [{"id": s.id, "name": s.name} for s in skills]
    }), 200


@views.route("/skills", methods=["GET"])
def get_all_skills():
    skills = Skill.query.all()
    result = [{"id": skill.id, "name": skill.name} for skill in skills]
    return jsonify(result)



@views.route("/contact_form", methods=["POST"])
def handle_contact():
    data = request.get_json()

    # Basic validations
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()
    message = data.get("message", "").strip()

    errors = {}

    if not name:
        errors["name"] = "Name is required."
    if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        errors["email"] = "A valid email is required."
    if not message:
        errors["message"] = "Message cannot be empty."
    if phone and not re.match(r"^\+?[0-9\s\-]{7,15}$", phone):
        errors["phone"] = "Enter a valid phone number."

    if errors:
        return jsonify({"errors": errors}), 400

    try:
        new_contact = Contact(name=name, email=email, phone=phone, message=message)
        db.session.add(new_contact)
        db.session.commit()
        return jsonify({"message": "Contact submitted successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error"}), 500