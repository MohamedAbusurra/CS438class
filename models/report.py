from datetime import datetime, timezone
from typing import Optional, Dict, Any
import json
from models.database import db

class Report(db.Model):
    __tablename__ = 'reports'

    STATUS_OPTIONS = ["pending", "generating", "completed", "failed"]
    TYPE_OPTIONS = ["performance"]

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    report_type = db.Column(db.String(50), default="performance")
    status = db.Column(db.String(20), default="pending")
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime)
    file_path = db.Column(db.String(255))
    progress = db.Column(db.Integer, default=0)
    _filters = db.Column(db.Text)

    project = db.relationship('Project', backref='reports')
    created_by = db.relationship('User', backref='reports_created', foreign_keys=[created_by_id])

    def __init__(
        self,
        project_id: int,
        report_type: str = "performance",
        created_by_id: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ):
        if report_type not in self.TYPE_OPTIONS:
            raise ValueError(f"Invalid report type. Choose from: {', '.join(self.TYPE_OPTIONS)}")

        self.project_id = project_id
        self.report_type = report_type
        self.created_by_id = created_by_id
        self.status = "pending"
        self.progress = 0
        self.filters = filters or {
            "include_completed_tasks": True,
            "include_missed_deadlines": True,
            "include_contributions": True,
            "format": "pdf"
        }

    @property
    def filters(self) -> Dict[str, Any]:
        return json.loads(self._filters) if self._filters else {}

    @filters.setter
    def filters(self, value: Dict[str, Any]):
        self._filters = json.dumps(value) if value else None

    def update_progress(self, progress: int):
        if 0 <= progress <= 100:
            self.progress = progress
            if progress == 100:
                self.status = "completed"
                self.completed_at = datetime.now(timezone.utc)
        else:
            raise ValueError("Progress must be between 0 and 100")

    def mark_as_failed(self):
        self.status = "failed"
        self.completed_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'project_id': self.project_id,
            'report_type': self.report_type,
            'status': self.status,
            'created_by_id': self.created_by_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M:%S') if self.completed_at else None,
            'file_path': self.file_path,
            'progress': self.progress,
            'filters': self.filters
        }
