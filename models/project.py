from datetime import datetime , timezone 
from typing import Optional
from models.database import db


class project(db.model):
    """ 
    This representing project class in the cmt system.
    """
    __tablename__ = 'projects'

    STATUS_OPTIONS = ["active","completed","pending","on hold","cancelled"]

    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(100), nullable =False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date,nullable=False)
    expected_end_date = db.Column(db.Date,nullable=False)
    status = db.Column(db.String(20),default="active")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_by_id = db.Column(db.Integer,db.Foreignkey('users.id'))

    files = db.relationship('File', backref='project' ,lazy=True)

    def__init__(
        self,
        project_name: str,
        description: str,
        start_date: datatime,
        expected_end_date: Optional[datetime] = None,
        status: str = "active",
        created_by_id: Optinonal[int] = None,
    ):
        """
        Init  a Prject object.
        """
        self.project_name = project_name
        self.description = description
        self.start_date = start_date
        self.expected_end_date = expected_end_date
        self.status = status if status in self.STATUS_OPTIONS else "active"
        self.created_by_id = created_by_id
    
    def to_dict(self) -> dict:
        """
        Converet Project object  to dictionary.

        Returns:
            Dicitonary represention for the project object.
        """
        return {
            'id' : self.id,
            'project_name': self.project_name,
            'description' : self.description,
            'start_date': (
                self.start_date.strftime('%Y-%m-%d') if self.start_date else None
            ),
            'expected_end_date': (
                self.expected_end_date('%Y-%m-%d') 
                if self.expected_end_date
                else None
            ),
            'status': self.status,
            
        }
