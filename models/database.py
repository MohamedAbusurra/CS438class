from datetime import datetime, timezone
from flask_aqlalchemy import SQLAlchemy
import os # we nee it to save the file to upload dir
"""
set up our database conncetion
""" 
db= SQLALchemy() #init the sqlalchemy object

def initDB(app):
    """
    Sets up the database for our CMT and we need to  binds the app
    to sqlalchemy and creat tabls
    """
    try:
        #config some stuff for sqlite
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cmt.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False #we do not need this for know
        """
        we use this method from sqlalchemy 
        for creat all tables
        """
        db .init_app(app)
        with app.app_context():
            db.creat_all()
            from models.user import User
            if not User.query.first(): #if there no user 
                createSampleData()
    
    except Exception as err:
        raise(f'we have error init the db {err}')
    
def createSampleData():
    """
    we will make simple data for test the cmt 
    """
    try:
        from models.user import User
        from models.project import Project
        from models.task import Task
        from datetime import datetime , timedelta


        admin_user = User(
            username= 'admin' ,
            email= 'admin@cmt.com' ,
            firstName = 'sayf' ,
            lastName ='ammar'

        )

        db.session.add(admin_user)
        db.session.commit()

        startDate = datetime.now().date()
        end_date =  (datetime.now() + timedelta(days = 30 )).date()

        doFlask = Project(
            project_name = 'cs438LearnFlask' ,
            description = 'You need to learn flask' ,
            start_date =startDate ,
            expected_end_date = end_date ,
            status = 'active' ,
            created_by = admin_user.id 

        )
        db.session.add(doFlask)
        db.session.commit()


        """
        add task just for test 
        """
        task_one = Task(

            title="learn how to write with PEP8", 
            project_id=doFlask.id ,
            description="make the code eazy to read and reailbe." ,
            importance=Task.IMPORTANCE_HIGH , 
            status=Task.STATUS_NOT_BEGUN ,
            due_date=(datetime.now() +  timedelta(days=7)).date() ,
            assigned_to_id = admin_user.id ,
            created_by_id = admin_user.id ,
            estimated_duration = 8 ,  
            start_date = datetime.now().date() ,
            actual_start_datetime = None ,
            actual_end_datetime = None
        )

        db.session.add(task_one)
        db.session.commit()


        uploadDir = 'uploads'
        os.makedirs(uploadDir ,exist_ok = True )

        print('simple data al;l set')
    
    except Exception as err:
        print(f'simple date are broke : {err}')
        db.session.rollback() # for undo any mess
        raise
    




