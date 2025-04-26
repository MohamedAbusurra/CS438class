from datetime import datetime , timezone
from typing import Optional
import models.database as db

class FileVersion(db.Model):
    """
    we use file verstion class to track version of the fils in the project
    """
    __tablename__ ='file_version' # table name for the sqlalcemy
    """
    attributes of the class
    Primary key for version table
    """
    id =db. Column(db .Integer ,
                   primary_key= True)
    fileId = db . Column(db . Integer , 
                         db.ForeignKey('files.id'),
                         nullable = False) # links to father file
    version_number= db. Column(db. Integer ,
                               nullable = False)
    changeedById=  db. Column(db. Integer ,
                              db. ForeignKey('users.id'),
                              nullable= False) # links to user who chang the file
    version_path =  db. Column(db .String(255),
                                nullable =False)
    changeTimestamp = db.Column(db.DateTime ,
                                default= lambda : datetime.now(timezone.utc))
    

    
    
    def __init__(self , file_id: int ,
                 version_num : int ,
                 changed_by_id: Optional[int],
                 path: str   ):
        """
        her we set up file version with the given details
        """
        try:
            if file_id is  None:
                raise ValueError('file id can not be none')
            self.fileId = file_id
            self.version_number = version_num
            
            if changed_by_id is None :
                raise ValueError('changed by id can not be none')
            self.changeedById= changed_by_id
            self.version_path  = path
        except ValueError as e:
            raise ValueError(f'somthing brok in the fileversion init {e}')
        
        def to_dict(self) -> dict :
            """
            make file version attributes to dictionary
            returns :
               dict: of the version detils
            """
            try:
                timeStamp_str =None
                if self.changeTimestamp :
                    timeStamp_str= self.changeTimestamp.strftime(
                        '%Y-%m-%d  %H:%M:%S'
                    )#Formate time stamp manully
                version_data={
                    'id' :self.id,
                    'file_id': self.fileId,
                    'version_number':  self.version_number ,
                    'version_path': self.version_path,
                    'changeTimestamp': timeStamp_str
                }
                return version_data
            except Exception as error:
                raise ValueError(f'error in dict data is {error}')

            