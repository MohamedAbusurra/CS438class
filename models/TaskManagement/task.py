from datetime import datetime, timezone

from typing import Optional, List

from models.database import db

# TODO: prob need to clean up these imports later

class Task(db.Model ):
    """
    task class for project tasks. Tracks status, importance, and timing info.
    """

    __tablename__ = 'tasks' 



    # Status constants
    STATUS_NOT_BEGUN = "not begun"

    statusInProgress = "in progress"  # Why camelCase here? idk, tired


    STATUS_FINISHED = "finished"
    
    status_options = [STATUS_NOT_BEGUN,
                       statusInProgress,
                         STATUS_FINISHED]

    # Importance levels
    IMPORTANCE_HIGH = "high"

    importanceNormal = "normal"  # Mixed naming, oops

    IMPORTANCE_OPTIONS = [IMPORTANCE_HIGH, importanceNormal]

    # DB columns
    id = db. Column(db. Integer ,
                     primary_key=True )

    taskTitle = db. Column(db. String(100),
                           
                           nullable=False)  # Descriptive name
    description = db. Column(db.Text)

    importance = db. Column(db. String(20),
                            default= importanceNormal)
    status = db. Column(db. String(20), 
                        default=STATUS_NOT_BEGUN)


    dueDate = db.Column(db.Date)  # When it's gotta be done
    project_id = db. Column(db. Integer,
                            db.ForeignKey('projects.id'), 
                           nullable=False)

    assignedToId = db. Column(db.Integer,
                              db.ForeignKey('users.id'))

    created_by_id = db. Column(db. Integer, 
                               db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime,
                            default=lambda: datetime.now(timezone.utc))
    
    estimatedDuration = db. Column(db.Integer)  # Hours expected
    start_date = db.Column(db.Date)

    actualStartTime = db. Column(db.DateTime)

    actual_end_datetime = db.Column(db.DateTime)

    def __init__(self, title: str, projectId: int,
                  description: str = None,
                 importance: str = importanceNormal,
                   taskStatus: str = STATUS_NOT_BEGUN,
                 due_date: Optional[datetime] = None,
                   assigned_to_id: Optional[int] = None,
                 createdBy: Optional[int] = None, 
                 estimated_duration: Optional[int] = None,
                 startDate: Optional[datetime] = None, 
                 actualStart: Optional[datetime] = None,

                 actualEnd: Optional[datetime] = None):
        """
        initialize a Task object with all the bells and whistles.

        """
        try:
            self.taskTitle =  title
            self.project_id =   projectId
            self.description =   description

            # check importance value

            if importance not in self.IMPORTANCE_OPTIONS:

                raise ValueError(f"Bad importance! Pick from: {', '.join(self.IMPORTANCE_OPTIONS)}")
            self.importance = importance


            # validate status - gotta be one of the options

            if taskStatus not in self.status_options:

                raise ValueError(f"Invalid status, use: {', '.join(self.status_options)}")
            
            self.status = taskStatus

            # Set the rest

            self.dueDate = due_date

            self.assignedToId = assigned_to_id

            self.created_by_id = createdBy

            self.estimatedDuration = estimated_duration

            self.start_date = startDate

            self.actualStartTime = actualStart

            self.actual_end_datetime = actualEnd

        except Exception as e:

            raise Exception(f"Task init failed i thnik: {str(e)}")
        

    def to_dict(self) -> dict:
        """
        turn task into a dictionary for JSON or whatever.

        Adds a flag for high importance because why not.
        """
        try:
            # build the dict manually for clarity
            task_data = {}

            task_data['id'] = self.id

            task_data['title'] = self.taskTitle

            task_data['description'] = self.description
            task_data['importance'] = self.importance
            task_data['status'] = self.status

            # Format dates if they exist
            task_data['due_date'] = (self.dueDate.strftime('%Y-%m-%d')
                                     
                                   if self.dueDate else None)
            
            task_data['created_at'] = (self.created_at.strftime('%Y-%m-%d %H:%M:%S')
                                       
                                     if self.created_at else None)
            task_data['start_date'] = (self.start_date.strftime('%Y-%m-%d')
                                       
                                     if self.start_date else None)
            
            task_data['actual_start_datetime'] = (self.actualStartTime.strftime('%Y-%m-%d %H:%M:%S')
                                                  
                                               if self.actualStartTime else None)
            
            task_data['actual_end_datetime'] = (self.actual_end_datetime.strftime('%Y-%m-%d %H:%M:%S')
                                             if self.actual_end_datetime else None)

            # more fields
            task_data['project_id'] = self.project_id

            task_data['assigned_to_id'] = self.assignedToId

            task_data['estimated_duration'] = self.estimatedDuration

            task_data['is_high_importance'] = self.importance ==  self.IMPORTANCE_HIGH  # handy flag

            return task_data



        except Exception as e:

            raise Exception(f"Error serializing task: {str(e)}")

    @classmethod

    def create_task(cls, title, project_id, 
                    description=None, 
                    importance=None, 
                    status=None,
                   due_date=None, 
                   assigned_to_id=None,
                     created_by_id=None,
                   estimated_duration=None, 
                   start_date=None):
        """
        create a new task and save it to the DB.
        """
        try:


            from models.database import db

            # defaults if not provided

            importance = importance or cls.importanceNormal
            status = status or cls.STATUS_NOT_BEGUN

            # make new task

            newTask = cls(

                title=title,

                projectId=project_id,

                description=description,

                importance=importance,

                taskStatus=status,

                due_date=due_date,

                assigned_to_id=assigned_to_id,

                createdBy=created_by_id,

                estimated_duration=estimated_duration,

                startDate=start_date,

                actualStart=None,

                actualEnd=None
            )

            # Save it
            db.session.add(newTask)

            db.session.commit()


            return newTask
        except Exception as e:
            raise Exception(f"Task creation bombed: {str(e)}")



    def update(self, title=None,
                description=None,
                  importance=None, 
                  status=None,
               due_date=None,
                 assigned_to_id=None,
                   estimated_duration=None,
                     start_date=None,
               actual_start_datetime=None, 
               actual_end_datetime=None):
        """
        update task fields if provided. Only changes what's passed in.
        """
        try:
            from models.database import db

            # update fields if given

            if title is not None:

                self.taskTitle = title

            if description is not None:
                self.description =   description

            if importance is not None:

                if importance in self.IMPORTANCE_OPTIONS:



                    self.importance = importance

                else:
                    raise ValueError("Bad importance value")


            if status is not None:


                if status in self.status_options:

                    self.status = status
                else:
                    raise ValueError("Invalid status")
            if due_date is not None:

                self.dueDate = due_date

            if assigned_to_id is not None:

                self.assignedToId = assigned_to_id
            if estimated_duration is not None:
                self.estimatedDuration = estimated_duration
            if start_date is not None:
                self.start_date = start_date
            if actual_start_datetime is not None:
                self.actualStartTime = actual_start_datetime

            if actual_end_datetime is not None:
                self.actual_end_datetime = actual_end_datetime


            db.session.commit()

            return self
        except Exception as e:

            raise Exception(f"Update failed: {str(e)}")

    def delete(self):

        """Delete this task and return its project ID."""
        try:
            from models.database import db

            projectId = self.project_id  # Save for return
            db.session.delete(self)
            db.session.commit()
            return projectId
        except Exception as e:
            raise Exception(f"Deletion failed: {str(e)}")
        

    @classmethod
    def getProjectTasks(cls, project_id):
        """
        Get all tasks for a project.
        No sorting, just raw list.
        """
        try:
            tasks = cls.query.filter_by(project_id=project_id).all()
            return tasks
        except Exception as e:
            raise Exception(f"Couldn't fetch tasks: {str(e)}")