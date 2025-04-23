from flask  import Flask,  render_template,  request,  redirect,  url_for, flash,  send_from_directory
import os
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
from models import db, init_db, User, Project, File, FileVersion, Task, Report


class CMTApp:
    
    """
    main app class for the cmt system it have the core functionality
    
    """

    def __init__(self ):

        # Setup the Flask app
        self.app = Flask(__name__ )

        self.app.secret_key = 'super_secret_key_123'  # TODO: we can move this to env var later

        # Init the database
        try:
            init_db(self.app )

        except Exception as err:

            print(f" DB  init failed : {err}")

            raise

        # Setup   upload folder
        
        self. UPLOAD_FOLDER  = 'uploads'

        self.app. config['UPLOAD_FOLDER'] = self. UPLOAD_FOLDER

        os.makedirs(self. app. config['UPLOAD_FOLDER'] , exist_ok=True )  # Make sure folder exists

        # Register all the routes

        self._register_routes()


    def _register_routes(self):
        """Sets up all the URL routes for the app."""

        try:
            # Homepage  routes
            
            self.app.add_url_rule('/', 'index',
                                      self.index )

            self.app.add_url_rule('/index',
                                   'index',
                                   self.index ) 

            # Project -related routes

            self.app.add_url_rule('/projects', 
                                  'view_projects', 
                                  self.view_projects )


            self.app.add_url_rule('/create_project',
                                   'create_project', 
                                   self.create_project,
                                   # Allow both  get  and post  methods
                                   methods=['GET', 'POST'])
            


            self.app.add_url_rule('/project/<int:project_id>',
                                     'project_details',
                                       self.project_details )

            self.app.add_url_rule('/project/<int:project_id>/delete',
                                     'delete_project', 
                                      self.delete_project)

            # File management routes
            self.app.add_url_rule('/files', 
                                  'file_management',
                                    self.file_management)
            

            self.app.add_url_rule('/upload_file', 
                                  
                                  'upload_file', 
                                  self.upload_file,
                                    methods=['POST'])
            self.app.add_url_rule('/file/<int:file_id>/download',
                                   'download_file',
                                     self.download_file)
            self.app.add_url_rule('/file/<int:file_id>/delete',
                                   'delete_file',
                                     self.delete_file)

            # Task routes
            self.app.add_url_rule('/project/<int:project_id>/tasks', 
                                  'view_tasks',
                                    self.view_tasks)
            self.app.add_url_rule('/project/<int:project_id>/create_task',
                                   'create_task', 
                                   self.create_task,
                                    
                                    
                                     methods=['POST'])
            self.app.add_url_rule('/task/<int:task_id>/edit', 
                                  'edit_task',
                                    self.edit_task,
                                      methods=['POST'])
            self.app.add_url_rule('/task/<int:task_id>/delete', 
                                  'delete_task', 
                                  self.delete_task)

            # Report routes

            self.app.add_url_rule('/project/<int:project_id>/reports',
                                   'view_reports', 
                                   
                                   self.view_reports)
            

            self.app.add_url_rule('/project/<int:project_id>/generate_report',
                                   'generate_report',
                                     self.generate_report,
                                       methods=['POST'])


            self.app.add_url_rule('/report/<int:report_id>/download', 
                                  'download_report',
                                    self.download_report )
            
            self.app.add_url_rule('/report/<int:report_id>/status',
                                  
                                   'report_status',
                                     self.report_status)
        except Exception as err:

            print(f"Route registr failed: {err}")  # Should probably log this 
            raise

    def run(self, debug=True ):

        """Start the Flask app."""
        try:
            self.app.run(debug=debug )

        except Exception as err:

            print(f" App failed to start: {err}")
            raise

    # Route handlers


    def index(self ):

        """move  to the projects page."""

        try:
            return redirect(url_for (' view_projects ' ))
        
        except Exception as e:

            flash(f'Error redirecting to projects: {str(e)}',
                   'danger')

            return  render_template('error.html')

    def view_projects(self ):

        """Shows all projects in the system."""

        try:
            projects = Project.query.all()
            project_list = [p.to_dict() for p in projects]  # Convert to dict for template

            return render_template('projects.html',
                                      projects=project_list)
        
        except Exception as e:

            flash(f'Error fetching projects: {str(e)}',
                              'danger')
            
            return redirect ( url_for( ' index'))

    def create_project(self  ):

        """
        handles project creation. get for form, post for submisson.
        """
        try:
            if request.method == 'POST':

                proj_name = request.form.get('project_name' )

                description = request.form.get('project_description' )  # Changed var name for no reason
                startDate = request.form.get('start_date' )

                end_date_str =  request. form. get('end_date ' ) #her we get the end date



                start_date =  datetime. strptime( startDate , '%Y-%m-%d' ). date() if   startDate else  datetime. now(timezone.utc). date()


                end_date =   datetime. strptime( end_date_str, '%Y-%m-%d').  date() if   end_date_str  else    None


                # grab the first user for now 
                curr_user = User.query.first()


                # Create new project instance

                newProject = Project(
                    project_name=proj_name ,

                    description=description ,
                    start_date=start_date ,

                    expected_end_date=end_date ,

                    status="active",
                    created_by_id=curr_user.id if curr_user else None

                )

                # Save to DB

                db.session.add(newProject)

                db.session.commit()  # Commit the transaction

                flash('Project  created succesfully! ', 'success')  # Typo in message, oops


                return  redirect (url_for( 'view_projects' ) )
            

            # Show the form for GET requests

            return render_template('create_project.html')
        
        except Exception as e:

            flash(f'Error creating project: {str(e)}', 'danger')

            return  redirect( url_for ( 'view_projects' ))
        



    def project_details(self, project_id ):

        """
        displays the details for the  specific project in the cmt .
        
        """
        try:
            project = Project. query.  get( project_id )

            if not project:

                flash('Project not found!', 'danger')

                return  redirect( url_for(' view_projects ') )

            # Fetch files and tasks
            files = project.get_files()  # Using model method


            tasks = project.get_tasks()

            # Convert to dicts for template rendering

            file_list = [f.to_dict() for f in files]

            taskList = [t.to_dict() for t in tasks]  # Inconsistent naming, oh well



            return render_template('project.html',
                                  project=project.to_dict(),
                                  files=file_list,
                                  tasks=taskList)
        


        except Exception as e:

            flash(f'Error fetching project details: {str(e)}', 'danger')

            return  redirect( url_for( ' view_projects ' ))

    def delete_project(self, project_id):


        """
        Deletes a project and unlinks its files.
        
        """
        try:

            project =  Project. query. get( project_id )

            if not project:
                flash('Project not found!', 'danger')


                return  redirect ( url_for (' view_projects  ' ))
            

            # Unlink files from this project

            for file in File.query.filter_by(project_id=project_id).all():

                file.project_id = None  # Just set to null for now
                

            # Delete the project
            db.session.delete(project)

            db.session.commit()

            flash(f'Project "{project.project_name}" deleted successfully!', 'success')


            return redirect(url_for('view_projects'))
        
        except Exception as e:
            flash(f'Error deleting project: {str(e)}', 'danger')

            return  redirect ( url_for (' view_projects ') )

    def file_management(self ):

        """
        shows the file management page with all files and projects.
        """
        try:
            all_files = File.query.all()

            all_projects = Project.query.all()

            return render_template('files.html',
                                  files=[f.to_dict() for f in all_files],
                                  projects=[p.to_dict() for p in all_projects])
        except Exception as e:
            
            flash(f'Error loading file management:       {str(e)}', 'danger')

            return redirect (url_for (' index '))

    def upload_file(self ):

        """
        Handles file uploads. Saves to filesystem and DB.
        """
        try:
            if 'file' not in request.files:

                flash('No file part in request!', 'danger')

                return redirect( url_for (' file_management '))

            file = request.files['file']

            if file.filename == '':

                flash('No file selected!', 'danger')
                return  redirect( url_for (' file_management '))
            

            if file:  # We have a file to process


                filename = secure_filename(file.filename)

                filePath = os.path.join(self.app.config['UPLOAD_FOLDER '] , 
                                        filename)  # Mixed naming convention

                file.save(filePath)  # Save to filesystem


                # grab form data
                file_desc = request.form.get('file_description', '' )

                project_id = request. form. get('project_id')

                # convert project id if provided


                proj_id  = int( project_id) if  project_id   and project_id.isdigit()  else  None


                # get file extension and size

                file_ext = os.path.splitext(filename)[1][1:].lower()

                file_size = os.path.getsize(filePath)

                # demo user for now

                currentUser = User.query.first()

                # create new file record

                new_file = File(
                    project_id=proj_id  ,

                    file_name=filename ,

                    file_path=filePath ,

                    file_size=file_size ,  # Store size in bytes
                    file_type=file_ext ,

                    uploaded_by_id=currentUser.id if currentUser else None,

                    description=file_desc
                )



                # save file to DB
                db.session.add(new_file)


                db.session.commit()

                # create initial file version

                version = FileVersion(

                    file_id= new_file.id,

                    version_number=1,  # Start at version 1

                    changed_by_id=currentUser.id if currentUser else None,

                    version_path=filePath
                )
                db.session.add(version)

                db.session.commit()


                flash('File uploaded successfully!', 'success')


            # redirect like  on context

            if proj_id:

                return  redirect (url_for (' project_details ',
                                           
                                            project_id=proj_id ) )
            
            return  redirect (url_for (' file_management ') )
        
        except Exception as e:

            # clean up if something not work good

            if  'filePath'  in locals()  and   os.path.exists( filePath ) :


                os.remove( filePath )

            flash(f'Error uploading file: {str(e)}', 'danger')

            return redirect(url_for('file_management') )
        

    def download_file(self , file_id ):



        """
        downloads a file by id.
        """
        try:
            file = File.query.get(file_id )

            if not file or not os.path.exists(file.file_path):

                flash('File not found!', 'danger')

                return  redirect (url_for (' file_management ') )
            

            directory = os.path.dirname(file.file_path)

            filename = os.path.basename(file.file_path)

            return send_from_directory(directory, filename, as_attachment=True )
        
        except Exception as e:


            flash(f'Error downloading file: {str(e)}' , 'danger' )

            return  redirect (url_for( 'file_management ') )
        

    def delete_file(self, file_id ) :


        """
        deletes a file and its versions from DB and filesystem.

        """
        try:

            file = File.query.get(file_id)
            


            if not file:

                flash('File not found!', 'danger')
                return redirect(url_for('file_management'))
            

            project_id =  file.project_id  # store for redirect


            # delete file from filesystem

            if os.path.exists(file.file_path):

                os.remove(file.file_path)

            # delete versions
            
            for version in file.versions  :

                if os.path.exists(version.version_path) and version.version_path != file.file_path:


                    os.remove(version.version_path)

            # remove from DB


            db.session.delete(file)

            db.session.commit()

            flash(f'File "{file.file_name}" deleted successfully!', 'success' )


            # redirect to page

            if project_id:

                return redirect(url_for(' project_details',
                                         project_id=project_id))
            
            return redirect(url_for(' file_management '))
        
        except Exception as e:

            flash(f'Error deleting file: {str(e)}', 'danger' )

            return redirect (url_for(' file_management'))
        

    def view_tasks(self, 
                   project_id):
        


        """
        shows all tasks for a project.

        """
        try:

            project = Project. query. get( project_id )


            if not project:

                flash('Project not found!', 'danger')

                return redirect(url_for(' view_projects '))

            tasks = project.get_tasks()  # Get tasks using model method


            users = User.query.all()  # For task assignment dropdown


            return render_template('task.html',
                                   
                                  project=project.to_dict(),
                                  tasks=[t.to_dict() for t in tasks],
                                  users=users)
        except Exception as e:

            flash(f'Error fetching tasks: {str(e)}', 'danger')

            return redirect(url_for(' view_projects'))

    def create_task(self, project_id):


        """
        creates a new task for a project.
        
        """
        try:

            project = Project.query.get(project_id)

            if not project:

                flash('Project not found!', 'danger')

                return redirect(url_for('view_projects'))
            

            # extract form data

            taskTitle = request.form. get(' task_title ' )  


            task_desc = request.form. get(' task_description ' )

            importance = request.form. get(' task_importance',
                                            Task.IMPORTANCE_NORMAL)

            status = request.form. get('task_status',
                                        Task.STATUS_NOT_BEGUN)

            due_date_str = request. form. get(' task_due_date')

            assignedTo =   request.form. get(' task_assigned_to_id ')

            est_duration =    request.form.get(' task_estimated_duration ')

            start_date =   request. form. get(' task_start_date ')

          

            dueDate = datetime. strptime(due_date_str, '%Y-%m-%d'). date() if due_date_str else None


            startDate = datetime. strptime(start_date, '%Y-%m-%d'). date() if start_date else None


            
            estimated_duration =  int(est_duration) if  est_duration and est_duration.isdigit() else None

           
            assigned_to_id = int(assignedTo) if assignedTo and  assignedTo.isdigit() else None

            # demo user

            current_user = User. query. first()

            # create task


            Task.create_task(

                title=taskTitle,

                project_id=project_id,

                description=task_desc,

                importance=importance,

                status=status,

                due_date=dueDate,

                assigned_to_id=assigned_to_id,

                created_by_id=current_user.id if current_user else None,

                estimated_duration=estimated_duration,

                start_date=startDate
            )

            flash('Task created successfully!', 'success')

            return redirect(url_for('view_tasks',
                                     project_id=project_id))


        except Exception as e:
            flash(f'Error creating task: {str(e)}', 'danger')
            return redirect (url_for('view_tasks',
                                     project_id=project_id))

    def edit_task(self, task_id):

        """
        updates an existing task.
        """
        try:
            task = Task.query.get(task_id)

            if not task:

                flash('Task not found!', 'danger')

                return redirect(url_for('view_projects'))

            project_id = task.project_id


            # Get form data (this is a lot, maybe refactor later)

            title = request. form. get(' task_title ' )

            description = request.form. get(' task_description ')

            importance = request.form.get(' task_importance ')

            status = request.form.get(' task_status ')

            due_date_str = request.form.get(' task_due_date' )


            assigned_to_id = request.form.get(' task_assigned_to_id ')

            est_duration = request.form.get(' task_estimated_duration ')


            start_date_str = request. form. get('task_start_date ')

            actual_start = request. form. get('task_actual_start  ')


            actual_end = request. form. get(' task_actual_end' )


            
            due_date = datetime. strptime (due_date_str
                                           , '%Y-%m-%d'). date()   if due_date_str else None

            start_date = datetime. strptime (start_date_str
                                             , '%Y-%m-%d').date() if start_date_str else None

           
            actual_start_datetime = datetime. strptime(actual_start
                                                       , '%Y-%m-%dT%H:%M') if actual_start else None
            actual_end_datetime = datetime. strptime(actual_end
                                                     , '%Y-%m-%dT%H:%M') if actual_end else None

           
            estimated_duration  = int(est_duration)  if est_duration and est_duration.isdigit() else None

            

            assigned_to_id = int(assigned_to_id)  if assigned_to_id and assigned_to_id.isdigit() else None

            # update task know

            task.update(
                title= title,

                description= description ,

                importance= importance ,

                status = status ,

                due_date= due_date,

                assigned_to_id= assigned_to_id ,

                estimated_duration= estimated_duration ,

                start_date= start_date ,

                actual_start_datetime  = actual_start_datetime,

                actual_end_datetime=  actual_end_datetime


            )

            flash('Task updated successfully!', 'success')


            return  redirect (url_for (' view_tasks ', 
                                        project_id=project_id))
        
        except Exception as e:

            flash(f'Error updating task: {str(e)}',
                   'danger')

            return redirect(url_for('view_tasks',
                                     project_id=project_id))
        

    def delete_task(self, task_id ):

        """
        deletes a task.
        """
        try:

            task = Task.query.get(task_id )

            if not task:

                flash('Task not found!', 'danger')

                return redirect (url_for (' view_projects '))
            

            project_id = task. delete()  # Delete using model method



            flash(f'Task "{task.title}" deleted successfully!', 'success' )


            return  redirect(url_for(' view_tasks ' ,
                                     project_id=project_id))
        
        except Exception as e:

            flash(f'Error deleting task: {str(e)}', 'danger')
            return  redirect (url_for ('view_projects' ))
        

    def view_reports(self, project_id):

        """
        shows all reports for a project.
        """
        try:

            project = Project.query.get(project_id)

            if not project:

                flash('Project not found!', 'danger')

                return redirect (url_for (' view_projects'))
            
            

            reports = project.get_reports()  # get reports using model method

            return render_template('project_reports.html',
                                   
                                  project=project.to_dict(),

                                  reports=[r.to_dict() for r in reports])
        

        except Exception as e:

            flash(f'Error fetching reports: {str(e)}',
                   'danger')

            return redirect (url_for (' view_projects '))
        
        

    def generate_report(self, project_id):

        """
        starts report generation for a project.
        
        """
        try:

            project = Project.query.get(project_id)

            if not project:

                flash('Project not found!', 'danger')

                return  redirect (url_for(' view_projects '))
            

            current_user  = User.query. first()  # demo user


            # collect report filters


            filters = {

                'include_completed_tasks': 'include_completed_tasks'  in request.form,

                'include_missed_deadlines': 'include_missed_deadlines'   in request.form,

                'include_contributions': 'include_contributions'   in  request.form,

                'format': request.form.get('report_format', 'pdf')

            }


            # default to all if none selected

            if not any(filters.values()):  # This is probably overkill


                filters['include_completed_tasks'] = True

                filters['include_missed_deadlines'] = True

                filters['include_contributions'] = True


            # Create report

            Report.create_report(

                project_id=project_id,

                report_type=Report.TYPE_PERFORMANCE,

                created_by_id=current_user.id if current_user else None,

                filters=filters
            )


            flash('Report generation started. Check back later!', 
                  'success')

            return redirect(url_for('view_reports',
                                    
                                     project_id=project_id))
        
        except Exception as e:

            flash(f'Error generating report: {str(e)}', 'danger')

            return  redirect(url_for(' view_reports',
                                    
                                     project_id=project_id))

    def download_report(self, report_id):


        """
        downloads a generated report.
        """
        try:

            report = Report.query.get(report_id)

            if  not   report:

                flash('Report not found!', 'danger')

                return  redirect (url_for(' view_projects '))
            

            if report.status !=  Report.STATUS_COMPLETED:


                flash('Report not ready yet!', 'warning')

                return  redirect (url_for( ' view_reports', 
                                          project_id=report.project_id ))
            

            if not os.path.exists(report.file_path):

                flash('Report file missing!',
                       'danger')

                return redirect(url_for(' view_reports ',
                
                                         project_id=report.project_id))
            

            directory = os.path.dirname(report.file_path)

            filename = os.path.basename(report.file_path)

            return send_from_directory(directory, filename, as_attachment=True)
        
        except Exception as e:

            flash(f'Error downloading report: {str(e)}', 'danger')

            return redirect (url_for(' view_reports ',
                                     project_id=report.project_id))
        

    def report_status(self, report_id):

        """
        checks the status of a report.
        """
        try:

            report =  Report.query.get(report_id )

            if not report:
                
                return {'status': 'error', 
                        
                        'message': 'Report not found'}
            
            return report.get_status()  # Use model method
        
        except Exception as e:

            return {'status': 'error', 
                    'message': f'Error checking status: {str(e)}'}
        


if __name__ == '__main__':
    app = CMTApp()
    app.run(debug=True)  # Debug mode for dev