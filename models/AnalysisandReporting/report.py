from datetime import datetime, timezone
from typing import Optional, Dict, Any
import json
from models.database import db

class Report(db.Model):
    """
    Report class representing a performance report in the system.
    """

    __tablename__ = 'reports'

    # Report Types
    TYPE_PERFORMANCE = "performance"
    TYPE_OPTIONS = [TYPE_PERFORMANCE]

    # Report Statuses
    STATUS_PENDING = "pending"
    STATUS_GENERATING = "generating"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_OPTIONS = [STATUS_PENDING, STATUS_GENERATING, STATUS_COMPLETED, STATUS_FAILED]

    # Database columns
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    report_type = db.Column(db.String(50), default=TYPE_PERFORMANCE)
    status = db.Column(db.String(20), default=STATUS_PENDING)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime)
    file_path = db.Column(db.String(255))
    progress = db.Column(db.Integer, default=0)
    _filters = db.Column(db.Text)

    # Relationships
    project = db.relationship('Project', backref='reports')
    created_by = db.relationship('User', backref='reports_created', foreign_keys=[created_by_id])

    DEFAULT_FILTERS = {
        "include_completed_tasks": True,
        "includeMissedDeadlines": True,
        "include_contributions": True,
        "format": "pdf"
    }

    def __init__(self, project_id: int, report_type: str = TYPE_PERFORMANCE,
                 created_by_id: Optional[int] = None, filters: Optional[Dict[str, Any]] = None):
        if report_type not in self.TYPE_OPTIONS:
            raise ValueError(f"Invalid report type. Must be one of: {', '.join(self.TYPE_OPTIONS)}")

        self.project_id = project_id
        self.report_type = report_type
        self.created_by_id = created_by_id
        self.status = self.STATUS_PENDING
        self.progress = 0
        self.filters = filters if filters else self.DEFAULT_FILTERS

    @property
    def filters(self) -> Dict[str, Any]:
        """
        Get filters as a dictionary from JSON string.
        """
        try:
            if not self._filters:
                return {}
            return json.loads(self._filters)
        except json.JSONDecodeError:
            print("Broken filter JSON")
            return {}

    @filters.setter
    def filters(self, value: Dict[str, Any]):
        """
        Set filters from a dictionary.
        """
        if value:
            self._filters = json.dumps(value)
        else:
            self._filters = json.dumps(self.DEFAULT_FILTERS)

    def update_progress(self, progress: int):
        """
        Update report generation progress.
        """
        if 0 <= progress <= 100:
            self.progress = progress
            if progress == 100:
                self.status = self.STATUS_COMPLETED
                self.completed_at = datetime.now(timezone.utc)
        else:
            raise ValueError("Progress must be between 0 and 100")

    def mark_as_failed(self):
        """
        Mark report as failed.
        """
        self.status = self.STATUS_FAILED
        self.completed_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert report to dictionary format for serialization.
        """
        return {
            "id": self.id,
            "project_id": self.project_id,
            "report_type": self.report_type,
            "status": self.status.strip(),
            "created_by_id": self.created_by_id,
            "created_at": self._format_date(self.created_at),
            "completed_at": self._format_date(self.completed_at),
            "file_path": self.file_path,
            "progress": self.progress,
            "filters": self.filters
        }

    @classmethod
    def create_report(cls, project_id, report_type=None, created_by_id=None, filters=None):
        """
        Create and save a new report to the database.
        """
        report = cls(
            project_id=project_id,
            report_type=report_type or cls.TYPE_PERFORMANCE,
            created_by_id=created_by_id,
            filters=filters
        )
        db.session.add(report)
        db.session.commit()
        return report

    @classmethod
    def get_project_reports(cls, project_id):
        """
        Retrieve all reports for a specific project.
        """
        return cls.query.filter_by(project_id=project_id).order_by(cls.created_at.desc()).all()

    def get_status(self):
        """
        Get current status of the report.
        """
        return {
            "status": self.status.strip(),
            "progress": self.progress,
            "completed_at": self._format_date(self.completed_at),
            "file_path": self.file_path if self.status == self.STATUS_COMPLETED else None
        }

    @staticmethod
    def _format_date(date_obj):
        if not date_obj:
            return None
        return date_obj.strftime('%Y-%m-%d %H:%M:%S')