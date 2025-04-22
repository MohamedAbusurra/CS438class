from datetime import datetime, timezone
from typing import Optional
from models.database import db


class Task(db.Model):
    __tablename__ = 'tasks'

    STATUS_OPTIONS = ["not begun", "in progress", "finished"]
    IMPORTANCE_OPTIONS = ["high", "normal"]

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    importance = db.Column(db.String(20), default="normal")
    status = db.Column(db.String(20), default="not begun")
    due_date = db.Column(db.Date)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    milestone_id = db.Column(db.Integer, db.ForeignKey('milestones.id'))
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    estimated_duration = db.Column(db.Integer)
    start_date = db.Column(db.Date)
    actual_start_datetime = db.Column(db.DateTime)
    actual_end_datetime = db.Column(db.DateTime)

    def __init__(
        self,
        title: str,
        project_id: int,
        description: Optional[str] = None,
        importance: str = "normal",
        status: str = "not begun",
        due_date: Optional[datetime] = None,
        milestone_id: Optional[int] = None,
        assigned_to_id: Optional[int] = None,
        created_by_id: Optional[int] = None,
        estimated_duration: Optional[int] = None,
        start_date: Optional[datetime] = None,
        actual_start_datetime: Optional[datetime] = None,
        actual_end_datetime: Optional[datetime] = None
    ):
        if importance not in self.IMPORTANCE_OPTIONS:
            raise ValueError(f"Invalid importance. Choose from: {', '.join(self.IMPORTANCE_OPTIONS)}")

        if status not in self.STATUS_OPTIONS:
            raise ValueError(f"Invalid status. Choose from: {', '.join(self.STATUS_OPTIONS)}")

        self.title = title
        self.project_id = project_id
        self.description = description
        self.importance = importance
        self.status = status
        self.due_date = due_date
        self.milestone_id = milestone_id
        self.assigned_to_id = assigned_to_id
        self.created_by_id = created_by_id
        self.estimated_duration = estimated_duration
        self.start_date = start_date
        self.actual_start_datetime = actual_start_datetime
        self.actual_end_datetime = actual_end_datetime

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'importance': self.importance,
            'status': self.status,
            'due_date': self.due_date.strftime('%Y-%m-%d') if self.due_date else None,
            'project_id': self.project_id,
            'milestone_id': self.milestone_id,
            'assigned_to_id': self.assigned_to_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'is_high_importance': self.importance == "high",
            'estimated_duration': self.estimated_duration,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'actual_start_datetime': self.actual_start_datetime.strftime('%Y-%m-%d %H:%M:%S') if self.actual_start_datetime else None,
            'actual_end_datetime': self.actual_end_datetime.strftime('%Y-%m-%d %H:%M:%S') if self.actual_end_datetime else None
        }
