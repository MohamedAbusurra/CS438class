from models.database import db, init_db
from models.UserManagement.user import User
from models.ProjectManagement.project import Project as projectModel
from models.DocumentFileManagement.file import File
from models.DocumentFileManagement.file_version import FileVersion as file_version
from models.TaskManagement.task import Task
from models.AnalysisandReporting.report import Report
"""
so this the main init file for all model
"""
"""
__all__ controls what gets import with "from models import *"
"""
__all__ =  [
    'db' ,
    'init_db' ,
    'User' ,
    'projectModel' ,
    'File' ,
    'file_version' ,
    'Task' ,
    'Report'

    ]
"""
jast make sure all models are I can use 
them
"""

try :
    all_models = [
        User ,
        projectModel ,
        File ,
        file_version  ,
        Task  ,
        Report
    ]
except ImportError as err:
    raise(f'something broke while importing model {err}')

