from datetime import datetime, timezone
from typing import Optional, List
from models.database import db

class Task(db.Model):
    """
    Task class representing a task in a project.
    """
    __tablename__ = 'tasks'

    # Status options
    STATUS_NOT_BEGUN = "not begun"
    STATUS_IN_PROGRESS = "in progress"
    STATUS_FINISHED = "finished"
    STATUS_OPTIONS = [STATUS_NOT_BEGUN, STATUS_IN_PROGRESS, STATUS_FINISHED]

    # Importance options
    IMPORTANCE_HIGH = "high"
    IMPORTANCE_NORMAL = "normal"
    IMPORTANCE_OPTIONS = [IMPORTANCE_HIGH, IMPORTANCE_NORMAL]

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    importance = db.Column(db.String(20), default=IMPORTANCE_NORMAL)
    status = db.Column(db.String(20), default=STATUS_NOT_BEGUN)
    due_date = db.Column(db.Date)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    milestone_id = db.Column(db.Integer, db.ForeignKey('milestones.id'))
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    estimated_duration = db.Column(db.Integer)  # Duration in hours
    start_date = db.Column(db.Date)
    actual_start_datetime = db.Column(db.DateTime)
    actual_end_datetime = db.Column(db.DateTime)

    def __init__(self, title: str, project_id: int, description: str = None,
                 importance: str = IMPORTANCE_NORMAL, status: str = STATUS_NOT_BEGUN,
                 due_date: Optional[datetime] = None, milestone_id: Optional[int] = None,
                 assigned_to_id: Optional[int] = None, created_by_id: Optional[int] = None,
                 estimated_duration: Optional[int] = None, start_date: Optional[datetime] = None,
                 actual_start_datetime: Optional[datetime] = None, actual_end_datetime: Optional[datetime] = None):
        """
        Initialize a Task object.

        Args:
            title (str): Title of the task
            project_id (int): ID of the project this task belongs to
            description (str, optional): Description of the task
            importance (str, optional): Importance of the task (high, normal)
            status (str, optional): Status of the task (not begun, in progress, finished)
            due_date (datetime, optional): Due date of the task
            milestone_id (int, optional): ID of the milestone this task is associated with
            assigned_to_id (int, optional): ID of the user this task is assigned to
            created_by_id (int, optional): ID of the user who created the task
            estimated_duration (int, optional): Estimated duration in hours
            start_date (datetime, optional): Planned start date
            actual_start_datetime (datetime, optional): Actual start date and time
            actual_end_datetime (datetime, optional): Actual end date and time
        """
        self.title = title
        self.project_id = project_id
        self.description = description

        # Validate importance
        if importance not in self.IMPORTANCE_OPTIONS:
            raise ValueError(f"Invalid importance value. Must be one of: {', '.join(self.IMPORTANCE_OPTIONS)}")
        self.importance = importance

        # Validate status
        if status not in self.STATUS_OPTIONS:
            raise ValueError(f"Invalid status value. Must be one of: {', '.join(self.STATUS_OPTIONS)}")
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
        """
        Convert task object to dictionary for serialization.

        Returns:
            dict: Dictionary representation of the task
        """
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
            'is_high_importance': self.importance == self.IMPORTANCE_HIGH,
            'estimated_duration': self.estimated_duration,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'actual_start_datetime': self.actual_start_datetime.strftime('%Y-%m-%d %H:%M:%S') if self.actual_start_datetime else None,
            'actual_end_datetime': self.actual_end_datetime.strftime('%Y-%m-%d %H:%M:%S') if self.actual_end_datetime else None
        }
