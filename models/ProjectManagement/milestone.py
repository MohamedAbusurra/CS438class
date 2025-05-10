from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import traceback  
from models.database import db

class Milestone(db.Model):
    
    __tablename__ = 'milestones' 
    
    
    STATUS_NOT_STARTED = "not_started"  
    STATUS_IN_PROGRESS = "in_progress" 
    STATUS_COMPLETED = "completed"    
    STATUS_DELAYED = "delayed"         
    
    STATUS_OPTIONS = [
        STATUS_NOT_STARTED,
        STATUS_IN_PROGRESS, 
        STATUS_COMPLETED,
        STATUS_DELAYED
    ]
    
    # Basic milestone attributes
    id = db.Column(db.Integer, primary_key=True)  # primary key
    title = db.Column(db.String(100), nullable=False)  # required name
    description = db.Column(db.Text)  # optional longer description
    
    # Timeline fields
    due_date = db.Column(db.Date, nullable=False)  # when milestone should be completed
    
    # Status and progress tracking
    status = db.Column(db.String(20), default=STATUS_NOT_STARTED)  # current status
    completion_percentage = db.Column(db.Float, default=0.0)  # percentage complete (0-100)
    
    # Foreign keys
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)  # link to project
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # creation timestamp
    
    # Relationships
    # Tasks associated with this milestone
    tasks = db.relationship(
        'Task',
        backref='milestone',
        lazy=True,
        foreign_keys='Task.milestone_id'
    )
    
    def __init__(self, title: str, project_id: int, due_date: datetime, 
                 description: str = None, status: str = STATUS_NOT_STARTED):
       
        try:
            # Validate inputs
            if not title or len(title) < 3:
                raise ValueError("Milestone title must be at least 3 characters")
                
            if not project_id:
                raise ValueError("Project ID is required")
                
            if not due_date:
                raise ValueError("Due date is required")
            
            # Set basic attributes
            self.title = title
            self.project_id = project_id
            self.description = description or ""  # default to empty string if None
            self.due_date = due_date
            
            # Validate and set status
            if status not in self.STATUS_OPTIONS:
                print(f"Warning: Invalid status '{status}', defaulting to 'not_started'")
                self.status = self.STATUS_NOT_STARTED
            else:
                self.status = status
                
            # Initialize completion percentage to 0
            self.completion_percentage = 0.0
            
        except Exception as e:
            # Log the error
            print(f"ERROR creating milestone: {str(e)}")
            traceback.print_exc()
            # Re-raise the exception
            raise ValueError(f"Could not create milestone: {str(e)}")
    
    def update_completion(self):
        
        try:
            # Get all tasks for this milestone
            tasks = self.tasks
            
            # If no tasks, completion is 0%
            if not tasks or len(tasks) == 0:
                self.completion_percentage = 0.0
                self.status = self.STATUS_NOT_STARTED
                return self.completion_percentage
            
            # Count completed tasks
            completed_tasks = sum(1 for task in tasks if task.status == 'completed')
            total_tasks = len(tasks)
            
            # Calculate percentage
            self.completion_percentage = (completed_tasks / total_tasks) * 100
            
            # Update status based on completion and due date
            if self.completion_percentage == 100:
                self.status = self.STATUS_COMPLETED
            elif self.completion_percentage > 0:
                # Check if milestone is delayed
                if self.due_date < datetime.now(timezone.utc).date():
                    self.status = self.STATUS_DELAYED
                else:
                    self.status = self.STATUS_IN_PROGRESS
            else:
                # Check if milestone is delayed
                if self.due_date < datetime.now(timezone.utc).date():
                    self.status = self.STATUS_DELAYED
                else:
                    self.status = self.STATUS_NOT_STARTED
            
            # Commit changes to database
            from models.database import db
            db.session.commit()
            
            return self.completion_percentage
            
        except Exception as e:
            # Log the error
            print(f"ERROR updating milestone completion: {str(e)}")
            traceback.print_exc()
            # Re-raise the exception
            raise ValueError(f"Could not update milestone completion: {str(e)}")
    
    def get_tasks(self):
        """
        Get all tasks for this milestone.
        
        Returns all tasks linked to this milestone, without any sorting.
        
        Returns:
            list: List of Task objects for this milestone
        """
        try:
            # Import here to avoid circular imports
            from models.TaskManagement.task import Task
            
            # Query for tasks with this milestone_id
            tasks = Task.query.filter_by(milestone_id=self.id).all()
            
            return tasks
            
        except Exception as e:
            # Log the error
            print(f"ERROR getting milestone tasks: {str(e)}")
            traceback.print_exc()
            # Re-raise the exception
            raise ValueError(f"Could not get milestone tasks: {str(e)}")
    
    def to_dict(self):
        """
        Convert milestone object to dictionary for API/JSON responses.
        
        Returns:
            dict: Milestone data as dictionary
        """
        try:
            return {
                'id': self.id,
                'title': self.title,
                'description': self.description,
                'due_date': self.due_date.isoformat() if self.due_date else None,
                'status': self.status,
                'completion_percentage': self.completion_percentage,
                'project_id': self.project_id,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'tasks': [task.id for task in self.tasks] if self.tasks else []
            }
        except Exception as e:
            print(f"Error converting milestone to dict: {str(e)}")
            return {'error': 'Could not convert milestone to dictionary'}
    
    @classmethod
    def create_milestone(cls, title, project_id, due_date, description=None, status=None):
        """
        Create a new milestone.
        
        Returns:
            The created milestone object.
        """
        try:
            # Import here to avoid circular imports
            from models.database import db
            
            # Validate status
            if status and status not in cls.STATUS_OPTIONS:
                print(f"Warning: Invalid status '{status}', defaulting to 'not_started'")
                status = cls.STATUS_NOT_STARTED
            
            # Create the new milestone object
            new_milestone = cls(
                title=title,  # required
                project_id=project_id,  # required
                due_date=due_date,  # required
                description=description,  # optional
                status=status or cls.STATUS_NOT_STARTED  # defaulted above
            )
            
      
            db.session.add(new_milestone)  # stage the new object
            db.session.commit()  # commit the transaction
            
            # Return the new milestone object
            return new_milestone
            
        except Exception as e:
            # Log the error
            print(f"ERROR creating milestone: {str(e)}")
            traceback.print_exc()
            
            # Try to rollback any partial changes
            try:
                db.session.rollback()
            except:
                pass
            
            # raise the exception
            raise ValueError(f"Could not create milestone: {str(e)}")
