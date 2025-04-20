from datetime import datetime, timezone, date
from typing import Optional, List
from io import BytesIO

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
except ImportError:
    print("ReportLab not installed. PDF generation will fail. Run: pip install reportlab")
    class SimpleDocTemplate: pass
    class Paragraph: pass
    class Spacer: pass
    def getSampleStyleSheet(): return {'h1': None, 'h2': None, 'Normal': None, 'Bullet': None}
    letter = None
    colors = None


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(100), unique=True, nullable=False)


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(255), unique=True, nullable=False)


class Milestone(db.Model):
     __tablename__ = 'milestones'
     id = db.Column(db.Integer, primary_key=True)


class Task(db.Model):
    __tablename__ = 'tasks'

    IMPORTANCE_OPTIONS: List[str] = ["normal", "high"]
    STATUS_OPTIONS: List[str] = ["not begun", "in progress", "finished"]

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    milestone_id = db.Column(db.Integer, db.ForeignKey('milestones.id'), nullable=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    importance = db.Column(db.String(10), nullable=False, default='normal')
    status = db.Column(db.String(20), nullable=False, default='not begun')
    due_date = db.Column(db.Date, nullable=True)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(
        self,
        title: str,
        project_id: int,
        created_by_id: int,
        milestone_id: int,
        description: Optional[str] = None,
        importance: str = "normal",
        status: str = "not begun",
        due_date: Optional[date] = None,
        assigned_to_id: Optional[int] = None,
    ):
        self.title = title
        self.project_id = project_id
        self.created_by_id = created_by_id
        self.milestone_id = milestone_id
        self.description = description
        self.importance = importance if importance in self.IMPORTANCE_OPTIONS else "normal"
        self.status = status if status in self.STATUS_OPTIONS else "not begun"
        self.due_date = due_date
        self.assigned_to_id = assigned_to_id

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'project_id': self.project_id,
            'milestone_id': self.milestone_id,
            'title': self.title,
            'description': self.description,
            'importance': self.importance,
            'status': self.status,
            'due_date': self.due_date.strftime('%Y-%m-%d') if self.due_date else None,
            'assigned_to_id': self.assigned_to_id,
            'created_by_id': self.created_by_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self) -> str:
        return f"<Task {self.id}: '{self.title}' Status: {self.status}>"


def generate_performance_report(project_id: int) -> Optional[bytes]:
    if not colors:
        print("Reportlab not available, cannot generate PDF.")
        return None
    try:
        project = Project.query.get(project_id)
        if not project:
            return None

        tasks = Task.query.filter_by(project_id=project_id).order_by(Task.due_date).all()
        user_ids = {t.assigned_to_id for t in tasks if t.assigned_to_id}
        users = User.query.filter(User.id.in_(user_ids)).all()
        user_map = {user.id: user for user in users}

        today = date.today()
        completed_tasks = []
        missed_deadline_tasks = []
        contributions = {}

        for task in tasks:
            if task.status == 'finished':
                completed_tasks.append(task)

            if task.due_date and task.due_date < today and task.status != 'finished':
                missed_deadline_tasks.append(task)

            if task.status == 'finished' and task.assigned_to_id:
                user_id = task.assigned_to_id
                assignee = user_map.get(user_id)
                if assignee:
                    user_name = getattr(assignee, 'userName', f'User {user_id}')
                    if user_id not in contributions:
                        contributions[user_id] = {'name': user_name, 'completed': 0}
                    contributions[user_id]['completed'] += 1

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        project_name_str = getattr(project, 'project_name', f'Project {project.id}')
        story.append(Paragraph(f"Performance Report: {project_name_str}", styles['h1']))
        story.append(Paragraph(f"Project ID: {project.id}", styles['Normal']))
        story.append(Paragraph(f"Generated on: {today.strftime('%Y-%m-%d')}", styles['Normal']))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Tasks Completed", styles['h2']))
        if completed_tasks:
            for task in completed_tasks:
                assignee_name = "Unassigned"
                if task.assigned_to_id in user_map:
                     assignee_name = getattr(user_map[task.assigned_to_id], 'userName', f'User {task.assigned_to_id}')
                due_date_str = task.due_date.strftime('%Y-%m-%d') if task.due_date else 'N/A'
                story.append(Paragraph(f"- {task.title} (Assigned: {assignee_name}, Due: {due_date_str})", styles['Bullet']))
        else:
            story.append(Paragraph("No tasks completed yet.", styles['Normal']))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Tasks Missing Deadlines", styles['h2']))
        if missed_deadline_tasks:
            for task in missed_deadline_tasks:
                assignee_name = "Unassigned"
                if task.assigned_to_id in user_map:
                    assignee_name = getattr(user_map[task.assigned_to_id], 'userName', f'User {task.assigned_to_id}')
                due_date_str = task.due_date.strftime('%Y-%m-%d') if task.due_date else 'Error: Missing Due Date'
                story.append(Paragraph(f"- {task.title} (Assigned: {assignee_name}, Due: {due_date_str})", styles['Bullet']))
        else:
            story.append(Paragraph("No tasks currently past their deadline.", styles['Normal']))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Individual Contributions (Completed Tasks)", styles['h2']))
        if contributions:
            for user_id, data in contributions.items():
                 story.append(Paragraph(f"- {data['name']}: {data['completed']} task(s)", styles['Bullet']))
        else:
            story.append(Paragraph("No completed tasks assigned to users yet.", styles['Normal']))
        story.append(Spacer(1, 12))

        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()
        return pdf_data

    except Exception as e:
        print(f"Error generating report for project {project_id}: {e}")
        return None