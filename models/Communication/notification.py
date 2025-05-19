# models /Communication / notification.py

from datetime import datetime, timezone
from models.database import db
from models.UserManagement.user import User
from models.ProjectManagement.project import Project
from models.TaskManagement.task import Task
from models.ProjectManagement.milestone import Milestone


class Notification(db.Model):
    """
    this for represents the  notification in the system
    
    each notification is linked
      to a user  and  
    project, task  or milestone
    """
    __tablename__ =  'notifications'  # db  table name
    
    # types 
    TYPE_TASK_ASSIGNED   = "task_assigned" # this when new task assigned to user he get notfication
    TYPE_TASK_UPDATED  = "task_updated"

    #TYPE_TASK_ COMMENTED   =  "task_commented" #TODO we add this may be 
    TYPE_PROJECT_UPDATED  =  "project_updated"
    #TYPE_ PROJECT_  COMMENTED = "project_commented"  #TODO we add this may be like later
    TYPE_DEADLINE_APPROACHING =  "deadline_approaching"

    #TYPE_ MILESTONE_ COMMENTED = "milestone_commented"   #TODO we add this may be later
    TYPE_MILESTONE_COMPLETED = "milestone_completed"

    TYPE_CUSTOM = "custom" 

    
    # valid  the notification types
    NOTIFICATION_TYPES = [
        TYPE_TASK_ASSIGNED,
        TYPE_TASK_UPDATED,
        TYPE_PROJECT_UPDATED,
        TYPE_DEADLINE_APPROACHING,
        TYPE_MILESTONE_COMPLETED,
        TYPE_CUSTOM
    ]
    
    # DB columns
    id = db.Column(db.Integer,
                     primary_key=True)  # primary key

    user_id = db.Column(db.Integer,
                         db.ForeignKey('users.id'), 
                         nullable=False)  # recipient
    project_id = db.Column(db.Integer,
                            db.ForeignKey('projects.id'), 
                            nullable=True)  # related project (optional)
    task_id = db.Column(db.Integer, 
                        db.ForeignKey('tasks.id'),
                          nullable=True)  # related task (optional)
    milestone_id = db.Column(db.Integer,
                              db.ForeignKey('milestones.id'),
                                nullable=True)  # related milestone (optional)
    
    title = db.Column(db.String(200), 
                      nullable=False)  # notification title
    content = db.Column(db.Text, 
                        nullable=True)  # notification details
    notification_type = db.Column(db.String(50),
                                   nullable=False)  # type of notification
    
    timestamp = db.Column(db.DateTime,
                           default=lambda: datetime.now(timezone.utc), 
                           nullable=False)  # when created
    
    is_read = db.Column(db.Boolean, 
                        default=False,
                          nullable=False)  # read status
    
    # this are for the relationships
    user = db.relationship('User', 
                           foreign_keys=[user_id],
                             backref='notifications')
    project = db.relationship('Project', 
                              foreign_keys=[project_id], 
                              backref='notifications')
    task = db.relationship('Task',
                            foreign_keys=[task_id], 
                            backref='notifications')
    milestone = db.relationship('Milestone',
                                 foreign_keys=[milestone_id],
                                   backref='notifications')
    
    def __init__(self, 
                user_id, 
                title,
                notification_type=TYPE_CUSTOM, 
                content=None,
                project_id=None, 
                task_id=None,
                milestone_id=None):
        """
        initialize a notification object.
        

        """
        try:
            if not title:
                raise ValueError("notification title must have value")
                
            if notification_type not in self.NOTIFICATION_TYPES:
                print(f" invalid notification type '{notification_type}', ")
                notification_type = self.TYPE_CUSTOM
                
            self.user_id = user_id

            self.title =  title
            self.content =   content
            self.notification_type  = notification_type
            self.project_id   = project_id
            self.task_id =  task_id
            self.milestone_id  = milestone_id
            self.is_read =  False  # default to  unread
            
        except ValueError as ve:

            print(f"error creating  notification: {ve}")
            raise
        except Exception as e:
            print(f"unexpected error  creating notification: {e}")
            raise
    
    def mark_as_read(self):
        """mark the notification as read."""
        try:
            self.is_read = True

            db.session.commit()
            return True
        except Exception as e:
            print(f"error marking notification as read: {e}")
            db.session.rollback()
            return False
    
    def get_link(self):
        """
        get the link to the related item.
        
        returns:
            str url of  related item like project or task 
        """
        try:
            if self.task_id:

                return f"/task/{self.task_id}"
            elif self.milestone_id:

                return f"/milestone/{self.milestone_id}"
            elif self.project_id:

                return f"/project/{self.project_id}"
            else:
                return "#"  # No specific link
        except Exception as e:

            print(f"error getting notification link: {e}")
            return "#"  # default  fallback
    
    @classmethod
    def create_notification(cls, 
                           user_id,
                           title, 
                           notification_type=TYPE_CUSTOM, 
                           content=None, 
                           project_id=None, 
                           task_id=None,
                           milestone_id=None):
        """
        create and save a new  notification
    
        Returns:
            notification  the  created notification  object or  None
        """
        try:
            notification = cls(
                user_id=user_id  ,
                title=title ,
                
                notification_type=notification_type,
                content=content,
                project_id=project_id ,
                task_id= task_id  ,

                milestone_id =milestone_id
            )
            
            db.session.add(notification)

            db.session.commit()
            
            return notification
        except Exception as e:
            print(f"error creating notification:  {e}")
            db.session.rollback()
            return None
