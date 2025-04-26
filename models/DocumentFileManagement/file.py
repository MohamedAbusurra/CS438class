from datetime import datetime,timezone
from typing import Optional
import  models.database as db


class File(db.Model):
    """
    File class representing files in the CMT system
    
    """
    """
    table name for sqlalchemy
    """
    __tablename__ = "files"

    
    """
    sporrted files in the cmt for know
    """
    SUPPORTED_TYPES  = ["docx",
                        "pdf" ,
                        "txt" ,
                        "png", 
                        "jpg" ,
                        "jpeg"]
    
    
    """
    Column definiton
    Primary key
    
    """
    id =db.Column(db.Integer, primary_key= True)

    """
    realtionship foreign key
    """  
    projectId = db.Column(db.Integer , db. ForeignKey('project.id')
                          ,nullable=False)
    uploadedBy = db.Column(db. Integer,db.ForeignKey('user.id')
                           ,nullable=False)
    """
    the file details
    """
    fileName =  db. Column( db. String(255 ),
                           nullable= False)#file name
    file_path = db. Column(db.String(255),
                            nullable =False)#file link on disk
    fileSize = db. Column( db.Integer ,
                           nullable=False) #file size
    file_type = db. Column(db. String(20) ,
                          nullable=False) #file type like docx or pdf etc


    description =db. Column(db. Text,
                            nullable=True) #file text content we need 
    
    uploadDate = db.Column(db.DateTime ,
                           default =lambda: datetime. now(timezone. utc))
    currentVersion = db.Column(db.Integer,
                                default=1)

    versions = db.relationship(
        'FileVersion' ,
         backref='file' ,
         lazy=True ,
         cascade = "all, delete-orphan") 
     
    

    def __init__(self ,project_id : Optional[int],
                 file_name: str, file_path : str ,
                 file_size : int , file_type : str, 
                 upload_by_id : Optional[int ] , 
                 description : Optional[str ]=  None):
        
        """
        Init file objects 
        """
        try:
             
            if project_id is None:
                raise ValueError('project id con not be none') 
            self.projectId = project_id

            self.fileName= file_name
            self.filePath =file_path



            if file_size > 100*1024*1024:
                raise ValueError('file to large')
            self.fileSize = file_size 

            normalizType= self._fileTypeTolowerNodot(file_type)
            if normalizType not in self.SUPPORTED_TYPES:
                   raise ValueError(f'UnsupportedFile: {normalizType}')
            self.file_type  = normalizType
            
            if upload_by_id is None:
                raise ValueError('uploaded by id can not be none')
            self.uploadedBy =  upload_by_id
            self.description= description
    
        except Exception as e:
              raise Exception(f'error creat file object is : {e}')
        
        
    

    def _fileTypeTolowerNodot(self ,file_type: str ) -> str:
        """
        clean file type
        """
        try:
            if not file_type:
                raise ValueError('file type can not be empty')
            return file_type.lower().replace('.' , '')
        except Exception as e :
            raise ValueError(f'the error  is : {e}')

     

    def getFormattedSize(self) -> str:
        """
        Format file size they can easy to read
        """
        try:
            size = self.fileSize
            if size < 1024:
                return f'{size} B '
            elif size < 1024*1024 :
                return f'{ round ( size /1024, 2)} KB'
            else:
                return f'{round( size/( 1024*1024),2 )} MB'
        except Exception as e:
            raise ValueError(f'the error is : {e}')
    
    def to_dict(self) -> dict:
        """
        her we convert file object to dictionary
        return: dict
        """
        try:
            result={
                'id' : self.id ,
                'projectId' :self.projectId,
                'fileName': self.fileName,
                'filePath': self.filePath,
                'fileSize' :   self.fileSize,
                'formatted_size' : self.get_formatted_size(),
                'fileType' :self.fileType,
                'description' :  self.description,
                'uploadedBy' :self. uploadedBy ,
                'uploadDate': self. uploadDate. strftime('%Y-%m-%d  %H:%M:%S' )
                 if self.upload_date
                 else None,
                'currentVersion' :  self.currentVersion
            }
            return  result
        except  Exception as  e:
            raise ValueError(f'the error for convert to dict is :   {e}')
        