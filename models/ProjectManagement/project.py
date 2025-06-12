from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import traceback  # for better error tracking
from models.database import db
from models.Forum.forum_post import ForumPost



class project(db.model):
    """ 
    This representing project class in the cmt system.
    """
    __tablename__ = 'projects'

    STATUS_OPTIONS = [ "active","completed ","pending ", "on hold","cancelled" ]

    primary_key =  True
    nullable = False 



    id =  db.Column(db.Integer , primary_key )
    project_name = db.Column(db.String(100) , nullable )
    description = db.Column(db.Text)
    start_date =  db.Column(db.Date,nullable)
    expected_end_date = db.Column( db.Date,nullable)
    status = db.Column(db.String(20), default="active")
    created_at = db.Column(db.DateTime, default=lambda : datetime.now(timezone.utc))
    created_by_id= db.Column(db.Integer,db.Foreignkey ('users.id'))

    files = db.relationship('File', backref='project' ,lazy=True)

    def __init__(
        self,
        project_name: str,
        description: str,
        start_date: datetime,
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
        self.expected_end_date  = expected_end_date  
        self.status= status if status in  self.STATUS_OPTIONS else  "active"
        self.created_by_id =created_by_id
    
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
                 self.start_date.strftime('%Y-%m-%d' ) 
                 if self.start_date else None 
            ),
            'expected_end_date': (
                self.expected_end_date('%Y-%m-%d') 
                if self.expected_end_date
                else None
            ),
            'status': self.status,

        }

    #TODO like move import inside method Imm I do not it good

    @classmethod

    def create_project(cls,
                       project_name,
                       description,
                       start_date,
                       excepted_end_date =None,
                       status="active",
                       created_by_id = None
        

    ):
        """
        her create new project
        return :
        the created project object
        
        """
        new_project = cls(
            project_name = project_name ,

            description = description  ,
            start_date  =start_date,
            expected_end_date  = expected_end_date ,
            status=status,
            created_by_id= created_by_id
        )
        db.session.add(new_project)
        db.session.commit()


        return new_project


    def delete( self) :
        """
        delete project
        return may true if like it work i think
        
        """
        try:
            
            files = File.query.filter_by(project_id = self.id ). all()
            for file in files :
                file.project_id = None 

            
            db.session.delete( self)

            db.session. commit()

            return True
        except  Exception   as e :
            db.session.rollback()
            raise e
        
    @classmethod

    def get_all_projecta(cls ):
        """
        her we make this method to get all projects
        and we Returns:
        list of project objects

        """
        try:
            #oh just we fetch all project 
            projectList =  cls.query.all() 

            print("fetched project : " , projectList)
            return projectList
        except Exception as e  :
            print( "her may  get___ all __project just faild not work like good ", e)
            return [] #fallback empty list
        


    def get_files(self ) :
        """
        get all files for this project 
        and return list of files objects

        """

        try:
            from models.DocumentFileManagement import File

            fileList = File.query.filter_by( project_id = self.id).all()

            allFiles =  fileList

            return allFiles
        except Exception as err:
            print("get_files() error ", err)
            return []
        

    def get_tasks( self) :
        """
        get all tasks that are link to this project
        return list[task] like list of task objects
        
        """ 
        try:

            from models.TaskManagement import Task
            projectID = self.id

            tempTaskList = Task.query.filter_by( 
                project_id = projectID
            ).all()

            """
            print(f'found {len(tempTaskList)} tasks in project{ projectID}')
            """

            return tempTaskList 
        except Exception as e :
            #raise e
            return []
        
    
    def get_reports(self ) :
        """
        get all report 
        """

        try:

            from models.AnalysisandReporting import report

            currentProjectID = self.id


            report_query = report.query.filter_by(

                project_id = currentProjectID

            ).order_by(report.created_at.desc())

            reportList = report_query.all() #convert to list make it better
            
            return reportList
        except:
            return []
        

    def get_forum_posts(self) -> List[ForumPost]:
        """
        Retrieves all forum posts associated with this project, ordered by post time (newest first).

        Returns:
            List[ForumPost]: A list of ForumPost objects. Returns an empty list on error.
        """
        try:
            # Assuming ForumPost model has a 'projectID' field and a 'postTime' field
            # and that 'postTime' should be used for ordering.
            # If 'projectID' is actually 'project_id' in ForumPost, adjust accordingly.
            # If 'postTime' is actually 'created_at' in ForumPost, adjust accordingly.
            posts = ForumPost.query.filter_by(projectID=self.id).order_by(ForumPost.postTime.desc()).all()
            return posts
        except Exception as e:
            print(f"Error fetching forum posts for project {self.id}: {e}")
            traceback.print_exc()
            return []





    
    

