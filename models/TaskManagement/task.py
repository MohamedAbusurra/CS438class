from datetime import datetime, timezone
from typing import Optional, Dict
from models.database import db
import json

class Task(db.Model):
    """
    Task class for project tasks. Tracks status, importance, and timing info.
    """

    __tablename__ = 'tasks'

    # Status constants
    STATUS_NOT_BEGUN = "not begun"
    STATUS_IN_PROGRESS = "in progress"
    STATUS_FINISHED = "finished"
    STATUS_OPTIONS = [STATUS_NOT_BEGUN, STATUS_IN_PROGRESS, STATUS_FINISHED]

    # Importance levels
    IMPORTANCE_HIGH = "high"
    IMPORTANCE_NORMAL = "normal"
    IMPORTANCE_OPTIONS = [IMPORTANCE_HIGH, IMPORTANCE_NORMAL]

    # DB columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    importance = db.Column(db.String(20), default=IMPORTANCE_NORMAL)
    status = db.Column(db.String(20), default=STATUS_NOT_BEGUN)

    due_date = db.Column(db.Date)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)

    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    estimated_duration = db.Column(db.Integer)
    start_date = db.Column(db.Date)
    actual_start_time = db.Column(db.DateTime)
    actual_end_datetime = db.Column(db.DateTime)

    def __init__(self, title: str, project_id: int,
                 description: Optional[str] = None,
                 importance: str = IMPORTANCE_NORMAL,
                 status: str = STATUS_NOT_BEGUN,
                 due_date: Optional[datetime] = None,
                 assigned_to_id: Optional[int] = None,
                 created_by_id: Optional[int] = None,
                 estimated_duration: Optional[int] = None,
                 start_date: Optional[datetime] = None,
                 actual_start_time: Optional[datetime] = None,
                 actual_end_datetime: Optional[datetime] = None):
        
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
        self.assigned_to_id = assigned_to_id
        self.created_by_id = created_by_id
        self.estimated_duration = estimated_duration
        self.start_date = start_date
        self.actual_start_time = actual_start_time
        self.actual_end_datetime = actual_end_datetime

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "importance": self.importance,
            "status": self.status,
            "due_date": self._format_date(self.due_date),
            "created_at": self._format_datetime(self.created_at),
            "start_date": self._format_date(self.start_date),
            "actual_start_datetime": self._format_datetime(self.actual_start_time),
            "actual_end_datetime": self._format_datetime(self.actual_end_datetime),
            "project_id": self.project_id,
            "assigned_to_id": self.assigned_to_id,
            "estimated_duration": self.estimated_duration,
            "is_high_importance": self.importance == self.IMPORTANCE_HIGH
        }

    def update(self, **kwargs):
        for field in ['title', 'description', 'importance', 'status', 'due_date', 
                      'assigned_to_id', 'estimated_duration', 'start_date', 
                      'actual_start_time', 'actual_end_datetime']:
            if field in kwargs and kwargs[field] is not None:
                setattr(self, field, kwargs[field])

        if self.importance not in self.IMPORTANCE_OPTIONS:
            raise ValueError("Bad importance value")

        if self.status not in self.STATUS_OPTIONS:
            raise ValueError("Invalid status value")

        db.session.commit()
        return self

    def delete(self):
        project_id = self.project_id
        db.session.delete(self)
        db.session.commit()
        return project_id

    @classmethod
    def create_task(cls, title, project_id, **kwargs):
        importance = kwargs.get("importance", cls.IMPORTANCE_NORMAL)
        status = kwargs.get("status", cls.STATUS_NOT_BEGUN)

        task = cls(
            title=title,
            project_id=project_id,
            description=kwargs.get("description"),
            importance=importance,
            status=status,
            due_date=kwargs.get("due_date"),
            assigned_to_id=kwargs.get("assigned_to_id"),
            created_by_id=kwargs.get("created_by_id"),
            estimated_duration=kwargs.get("estimated_duration"),
            start_date=kwargs.get("start_date"),
            actual_start_time=None,
            actual_end_datetime=None
        )
        db.session.add(task)
        db.session.commit()
        return task

    @classmethod
    def get_project_tasks(cls, project_id):
        return cls.query.filter_by(project_id=project_id).all()

    @staticmethod
    def _format_date(date_obj):
        return date_obj.strftime('%Y-%m-%d') if date_obj else None

    @staticmethod
    def _format_datetime(dt_obj):
        return dt_obj.strftime('%Y-%m-%d %H:%M:%S') if dt_obj else None