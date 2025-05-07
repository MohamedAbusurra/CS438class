from datetime  import  datetime,   timezone
from typing import Optional,   Dict,  Any,  List
import json
from models.database  import  db

class Report(db.Model):
    """
    report class representing a performance report in the system.
    """

    __tablename__ = ' reports ' #this the tavle in the database


    # report types

    TYPE_PERFORMANCE = "performance"

    TYPE_OPTIONS = [ TYPE_PERFORMANCE ]


    # report status
    STATUS_PENDING = "  pending"

    STATUS_GENERATING = " generating "

    STATUS_COMPLETED = " completed"

    STATUS_FAILED = "failed "

    STATUS_OPTIONS = [STATUS_PENDING ,
                      
                       STATUS_GENERATING,

                         STATUS_COMPLETED, 
                         STATUS_FAILED]
    

    id = db.  Column(db.Integer,
                    primary_key=True)
    
    project_id = db. Column(db. Integer,
                            db. ForeignKey(' projects.id '),
                              nullable=False)
    
    report_type = db.  Column(db. String(50),
                             default=TYPE_PERFORMANCE)


    status = db. Column(db. String(20), 
                       default=STATUS_PENDING)
    

    created_by_id = db.Column(db.Integer,
                               db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime, 
                           default=lambda:  datetime. now(timezone.utc))


    completed_at = db. Column(db. DateTime)
    file_path = db.Column(db.String(255))

    progress = db. Column(db. Integer, 
                         default=0)  # progress percentage (0-100)



    # store report filters as JSON
    _filters = db.Column(db.Text)


    # relationships
    project = db.relationship('Project',
                              
                               backref=' reports')
    

    created_by = db.relationship('User', 
                                 

                                 backref=' reports_created',

                                 foreign_keys= [created_by_id])
    

    def __init__( self , 
                 project_id: int,

                 reportType: str = TYPE_PERFORMANCE,

                 created_by_id:  Optional[int] = None ,

                 filters:  Optional[Dict[ str,   Any]] = None):
        
        """
        initialize a    Report object.

        
        """
        try: 
            self.project_id =    project_id
            self.reportType = reportType
            self.created_by_id = created_by_id


            # validate    report type

            if reportType not in self.TYPE_OPTIONS:

            
                 raise ValueError(f"Invalid report type. Must be one of: {', '.join(self.TYPE_OPTIONS)}")


        

            self.status = self.STATUS_PENDING

            self.progress = 0

            # set filters

            if filters:


                self.filters = filters

            else:
            # default filter - include all the  sections



                self.filters = {

                "include_completed_tasks": True,
                "includeMissedDeadlines": True,
                "include_contributions": True,
                "format": "pdf"  # default format
            }
        except Exception as e :
            print(f'report init faild {str(e)}')
            raise

            

    @property


    def filters(self) -> Dict[str, Any]:


        """
        get the filters as a dictionary from JSON string.
        """
        try:
            if not self._filters:
                return {}
            
            if isinstance(self._filters , dict) :
                return self._filters
            
            parsed = json.loads(self._filters)

            return parsed
        except json.JSONDecodeError :
            print("Broken filter json ")
            
            return {}
    

    @filters.setter


    def filters(self, value: Dict[str, Any]):


        """set the filters from a dictionary."""

        if value:

            self._filters = json.dumps(value)

        else:
            self._filters = None


    def update_progress(self, 
                        progress: int):
        

        """update the report generation progress."""


        if 0 <= progress <= 100:

            self.progress = progress
            if progress == 100:
                self.status = self.STATUS_COMPLETED
                self.completed_at = datetime.now(timezone.utc)
        else:

            raise ValueError("progress must be like 0 - 100")
        

    def mark_as_failed(self ):

        """
        mark the report as  failed.
        
        """


        self.status =  self. STATUS_FAILED

        self.completed_at = datetime. now(timezone.utc)


    def to_dict(self) ->   Dict[str, Any]:


        """
        convert report object to dictionary for serialization.


        returns:
        
            dict
        """
        return dict(
            id=self.id,

            project_id=self.project_id,

            report_type=self.report_type,

            status=self.status,
            created_by_id=self.created_by_id,


            created_at=self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,


            completed_at=self.completed_at.strftime('%Y-%m-%d %H:%M:%S') if  self.completed_at else None,

            file_path=self.file_path,

            progress=self.progress,
            
            filters=self.filters
        )

    @classmethod


    def create_report(cls,
                       project_id,
                       report_type=None,
                         created_by_id=None, 
                         filters=None):
        
        """
        create a new report.


        

        returns:
            The created report object
        """
        from models.database import db

        

        # Create new report
        new_report = cls(
            project_id=project_id,
            report_type=report_type or cls.TYPE_PERFORMANCE,
            created_by_id=created_by_id,
            filters=filters
        )

        db.session.add(new_report)
        db.session.commit()

        

        return new_report

    @classmethod

    def get_project_reports(cls,
                             project_id):
        

        """
        get all reports for a project.


        returns:
             list of report objects
        """
        reportList = cls. query.filter_by( project_id =project_id ). order_by(cls. created_at.desc()) .all()

        return reportList

    def get_status(self ):
        """
        get the status of the report.

        returns:
            dict:
        """
        status_info = {
            'status': self.status,

            'progress': self.progress,

            'completed_at': None,

            'file_path': None
        }

        if self.completed_at:
            status_info['completed_at'] = self.completed_at.strftime('%Y-%m-%d %H:%M:%S')

        if self.status == self.STATUS_COMPLETED:
            status_info['file_path'] = self.file_path

        return status_info
