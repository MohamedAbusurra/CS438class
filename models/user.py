from datetime import datetime , timezone
import models.database as db


"""
TODO : I will work in this later for know just for test
"""
class User(db.model):
    """
    this User class we use it to handle team in the project

    """

    __tablename__='users' # this table name in the sqlalchemy

    """
    her the attribute for this class
    """
    id db. Column(db. Integer,
                   primary_key = True)
    username= db.Column(db.String(50) ,
                         unique=True ,
                         nullable=False )
    
    email =db. Column(db. String( 100) ,
                    unique=True  ,
                    nullable =False)
    firstName= db. Column(db.String(50 ) )
    lastName =db.Column(db. String( 50))
    createdAt = db .Column(db .DateTime , default=datetime.now(timezone.utc))
    updatedAt = db.Column(db.DateTime ,
                           default=lambda : datetime.now(timezone.utc))
    """
    relationships between user table with other tabls
    I just use lazy=True I have stady about it in the documention but 
    might switch to selection  
    """

    projectsCreated= db.relationship('Project',backref='creator',
                                    lazy=True ,
                                     foreign_keys ='Project.created_by_id' )
    files_uploaded = db. relationship('File' ,backref='uploader', 
                                      lazy=True ,
                                      Foreign_keys = 'File.uploadedBy')
    fileVerstions= db. relationship( 'FileVersion', backref ='changer',
                                    lazy=True ,
                                    Foreign_keys = 'FileVersion.changedBy')
    tasksCreated = db.relationship('Task' , backref='creator' ,
                                   lazy=True ,
                                   Foreign_keys  ='Task.created_by_id' )
    
    tasks_assigned = db.relationship('Task' , backref = 'assignee' , 
                                     lazy = True , 
                                    foreign_keys = ' Task.assigned_to_id'  )

    """
    init object for the user class
    """          
    def __init__(self , username, 
                 email , firstName= None 
                 , lastName = None ):
        """
        her we will sets up new users to the system
        """
        if username is None or email is None :
            raise ValueError('you need to input username and email !')
        
        self.username  = username
        self.firstName  = firstName
        self.lastName   = lastName
        self.email =  email

    """
    her the simple methodesfor the user class for know later we will add more I hope do that
    """
    def getFullName(self ):
        """
        this methods will return the full name or user name if there no name 
        """
        try:
            if self.firstName and self.lastName :
                return f'{self.firstName } {self.lastName}'
            elif self.firstName:
                return self.firstName
            elif self.lastName :
                return self.lastName
            return self.username 
        except Exception as error:
            print(f'error in getFullName {error}')
            return self.username 
                        
