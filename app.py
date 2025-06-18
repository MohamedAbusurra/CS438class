from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
import os
import traceback
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
from models import db, init_db, User, AuthToken, Project, Milestone, File, FileVersion, Task, Report, Message, Notification
from models.Communication.communication_facade import CommunicationFacade
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from utils.notification_facade import NotificationFacade

class CMTApp:
    """
    Main app class for the CMT system with the core functionality.
    implements Singleton pattern for app instance management and
    uses Facade patterns for communication and notification management    """

    _instance = None

    def __new__(cls):
        """implement Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(CMTApp, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """initialize the Flask application with facades."""


        if hasattr(self, 'initialized'):
            return

        self.app = Flask(__name__)

        # configuration for different environments
        self.app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

        # database configuration 
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            # production: Use PostgreSQL from Render
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            self.app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        else:
            # development: Use SQLite
            self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cmt.db'

        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['UPLOAD_FOLDER'] = 'uploads'






        # create uploads directory 
        os.makedirs(self.app.config['UPLOAD_FOLDER'], exist_ok=True)
          # initialize facades - this the must importans desgin pattern we implemetation 
        self.communication_facade = CommunicationFacade()
        self.notification_facade = NotificationFacade()
          # initialize login manager
        self.login_manager = LoginManager()
        self.login_manager.init_app(self.app)
        self.login_manager.login_view = 'login'
        self.login_manager.login_message = 'Please log in to access this page.'

        # set up Flask-Login user loader
        self.setup_login_manager()

        # set up context processors
        self.setup_context_processors()

        # set up routes
        self.setup_routes()



          # create database tables
        with self.app.app_context():
            init_db(self.app)
            db.create_all()

        self.initialized = True





    def setup_login_manager(self):
        """set up Flask-Login """
        @self.login_manager.user_loader
        def load_user(user_id):
            """Load user by ID for the  falsk login."""
            try:
                return db.session.get(User, int(user_id))
            except:
                return None
            




    def setup_context_processors(self):
        """set up template context processors."""
        @self.app.context_processor
        def inject_user():
            """her inject user data and notifications into all templates."""



            try:
                if hasattr(current_user, 'id') and current_user.is_authenticated:
                    # get unread notification count using facade
                    unread_notifications = self.notification_facade.get_unread_notifications(current_user.id)
                    unread_notification_count = len(unread_notifications)

                    # get unread message count using facade
                    unread_messages = self.communication_facade.get_unread_messages(current_user.id)
                    unread_message_count = len(unread_messages)

                    return {
                        'unread_notification_count': unread_notification_count,
                        'unread_message_count': unread_message_count,
                        'recent_notifications': unread_notifications[:5]  # Show last 5
                    }
                else:
                    return {
                        'unread_notification_count': 0,
                        'unread_message_count': 0,
                        'recent_notifications': []
                    }
            except Exception as e:
                print(f"Error in context processor: {e}")
                return {
                    'unread_notification_count': 0,
                    'unread_message_count': 0,
                    'recent_notifications': []
                }
            




    def setup_routes(self):
        """
        sets up all the URL routes for the app.
        """
        try:
            # Health check route for Render
            self.app.add_url_rule('/health',
                                   'health_check',
                                   self.health_check)

            # Main routes
            self.app.add_url_rule('/',
                                   'index',
                                   self.index)
            self.app.add_url_rule('/index',
                                   'home',
                                   self.index)

            # Project routes
            self.app.add_url_rule('/projects',
                                   'view_projects',
                                   self.view_projects)
            self.app.add_url_rule('/create_project',
                                   'create_project',
                                   self.create_project,
                                     methods=['GET', 'POST'])
            self.app.add_url_rule('/project/<int:project_id>',
                                   'project_details',
                                     self.project_details)
            self.app.add_url_rule('/project/<int:project_id>/delete',
                                  'delete_project',
                                  self.delete_project)

            # File routes
            self.app.add_url_rule('/files',
                                   'file_management',
                                   self.file_management)
            self.app.add_url_rule('/upload_file',
                                   'upload_file', self.upload_file,
                                     methods=['POST'])
            self.app.add_url_rule('/file/<int:file_id>/download',
                                   'download_file', self.download_file)
            self.app.add_url_rule('/file/<int:file_id>/delete',
                                  'delete_file', self.delete_file)

            # Task routes
            self.app.add_url_rule('/project/<int:project_id>/tasks',
                                  'view_tasks', self.view_tasks)
            self.app.add_url_rule('/project/<int:project_id>/create_task',
                                   'create_task', self.create_task,
                                     methods=['POST'])
            self.app.add_url_rule('/task/<int:task_id>/edit',
                                  'edit_task', self.edit_task,
                                    methods=['POST'])
            self.app.add_url_rule('/task/<int:task_id>/delete',
                                  'delete_task', self.delete_task)

            # Milestone routes
            self.app.add_url_rule('/project/<int:project_id>/milestones',
                                  'view_milestones', self.view_milestones)
            self.app.add_url_rule('/project/<int:project_id>/create_milestone',
                                  'create_milestone', self.create_milestone,
                                  methods=['POST'])
            self.app.add_url_rule('/milestone/<int:milestone_id>/edit',
                                  'edit_milestone', self.edit_milestone,
                                  methods=['POST'])
            self.app.add_url_rule('/milestone/<int:milestone_id>/delete',
                                  'delete_milestone', self.delete_milestone)
            self.app.add_url_rule('/project/<int:project_id>/progress',
                                  'view_progress', self.view_progress)



            # Report routes
            self.app.add_url_rule('/project/<int:project_id>/reports',
                                   'view_reports', self.view_reports)
            self.app.add_url_rule('/project/<int:project_id>/generate_report',
                                  'generate_report', self.generate_report,
                                    methods=['POST'])

            self.app.add_url_rule('/report/<int:report_id>/download',
                                   'download_report',
                                   self.download_report)
            self.app.add_url_rule('/report/<int:report_id>/status',
                                   'report_status',
                                     self.report_status)            # Message routes
            self.app.add_url_rule('/messages',
                                   'view_messages',
                                   self.view_messages)
            self.app.add_url_rule('/messages/<int:user_id>',
                                   'view_conversation',
                                   self.view_conversation)
            self.app.add_url_rule('/send_message',
                                   'send_message',
                                   self.send_message,
                                   methods=['POST'])
            self.app.add_url_rule('/search_messages',
                                   'search_messages',
                                   self.search_messages,
                                   methods=['GET'])

            # Notification routes
            self.app.add_url_rule('/notifications',
                                   'view_notifications',
                                   self.view_notifications)
            self.app.add_url_rule('/notifications/mark_read/<int:notification_id>',
                                   'mark_notification_read',
                                   self.mark_notification_read)
            self.app.add_url_rule('/notifications/mark_all_read',
                                   'mark_all_notifications_read',
                                   self.mark_all_notifications_read)
            self.app.add_url_rule('/notifications/get_unread',
                                   'get_unread_notifications',
                                   self.get_unread_notifications)
            self.app.add_url_rule('/create_test_notification',
                                   'create_test_notification',
                                   self.create_test_notification,
                                   methods=['GET', 'POST'])

            # User authentication routes
            self.app.add_url_rule('/login',
                                   'login',
                                   self.login,
                                   methods=['GET', 'POST'])
            self.app.add_url_rule('/login',
                                   'login',
                                   self.login,
                                   methods=['GET', 'POST'])
            self.app.add_url_rule('/logout',
                                   'logout',
                                   self.logout)
            self.app.add_url_rule('/register',
                                   'register',
                                   self.register,
                                   methods=['GET', 'POST'])
            self.app.add_url_rule('/verify_email/<token>',
                                   'verify_email',
                                   self.verify_email)
            self.app.add_url_rule('/forgot_password',
                                   'forgot_password',
                                   self.forgot_password,
                                   methods=['GET', 'POST'])
            self.app.add_url_rule('/reset_password/<token>',
                                   'reset_password',
                                   self.reset_password,
                                   methods=['GET', 'POST'])

            # User management routes
            self.app.add_url_rule('/user_management',
                                   'user_management',
                                   self.user_management)
            self.app.add_url_rule('/edit_user/<int:user_id>',
                                   'edit_user',
                                   self.edit_user,
                                   methods=['GET', 'POST'])
            self.app.add_url_rule('/change_user_role/<int:user_id>',
                                   'change_user_role',
                                   self.change_user_role,
                                   methods=['GET'])
            self.app.add_url_rule('/update_user_role/<int:user_id>',
                                   'update_user_role',
                                   self.update_user_role,
                                   methods=['POST'])
            self.app.add_url_rule('/batch_assign_roles',
                                   'batch_assign_roles',
                                   self.batch_assign_roles,
                                   methods=['POST'])
            self.app.add_url_rule('/delete_user/<int:user_id>',
                                   'delete_user',
                                   self.delete_user)

        except Exception as e:
            print(f"error registering routes: {e}")







    def run(self, debug=True):
        """start the Flask app."""
        try:
            self.app.run(debug=debug)

        except Exception as err:

            print(f" app failed to start: {err}")
            raise





    # Route handlers for    Render stuff
    def health_check(self):
        """health check endpoint for Render deployment."""
        try:
            # Simple database connectivity check
            db.session.execute(db.text('SELECT 1'))
            return jsonify({
                'status': 'healthy',
                'message': 'CMT application is running',
                'database': 'connected'
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'message': 'Database connection failed',
                'error': str(e)
            }), 500

    def index(self):
        """redirect to register page for new users or projects for authenticated users."""
        try:
            # If user is authenticated, go to projects; otherwise, go to register
            if current_user.is_authenticated:
                return redirect(url_for('view_projects'))
            else:
                return redirect(url_for('register'))

        except Exception as e:
            flash(f'Error loading homepage: {str(e)}', 'danger')
            return render_template('/errors/403.html')





    @login_required
    def view_projects(self):
        """shows all projects in the system."""
        try:
            projects = Project.query.all()
            project_list = [p.to_dict() for p in projects]

            return render_template('projects.html',
                                  projects=project_list)
        except Exception as e:
            flash(f'Error fetching projects: {str(e)}', 'danger')
            return render_template('errors/403.html')




    @login_required
    def create_project(self):
        """handles project creation. get for form, post for submisson"""
        try:
            if request.method ==  'POST':

                project_name =   request.form.get('project_name')

                project_description =  request.form.get('project_description')

                start_date_str = request.form.get('start_date')

                end_date_str = request.form.get('end_date')


                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else datetime.now(timezone.utc).date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

                # get the current user
                current_user = User.query.first()

                # create new  project
                new_project = Project(

                    project_name=project_name,

                    description=project_description,

                    start_date=start_date,
                    expected_end_date=end_date,
                    status="active",
                    created_by_id=current_user.id if current_user else None
                )

                # Save to DB
                db.session.add(new_project)
                db.session.commit()

                flash('Project created  !', 'success')
                return redirect(url_for('view_projects'))



            return render_template('create_project.html')

        except Exception as e:

            flash(f'Error creating project: {str(e)}', 'danger')

            return  redirect(url_for('view_projects'))
    @login_required
    def project_details(self, project_id):
        """displays the details for the  specific project in the cmt ."""
        try:
            project = Project.query.get(project_id)
            if not project:
                flash('Project not found!', 'danger')
                return redirect(url_for('view_projects'))

            # fetch files, tasks, and milestones
            files = project.get_files()
            tasks = project.get_tasks()
            milestones = project.get_milestones()

            # update milestone progress
            project.update_milestone_progress()

            # get active milestone
            active_milestone = project.get_active_milestone()

            # convert to dicts for template rendering
            file_list = [f.to_dict() for f in files]
            task_list = [t.to_dict() for t in tasks]
            milestone_list = [m.to_dict() for m in milestones]


            return render_template('project.html',
                                  project=project.to_dict(),
                                  files=file_list,
                                  tasks=task_list,
                                  milestones=milestone_list,
                                  active_milestone=active_milestone.to_dict() if active_milestone else None)

        except Exception as e:

            flash(f'Error fetching project details: {str(e)}', 'danger')
            return redirect(url_for('view_projects'))






    @login_required
    def delete_project(self, project_id):
        """delete project route and unlinks its files"""

        try :
            project = Project.query.get(project_id)
            if not project:
                flash('Project not found!', 'danger')
                return redirect(url_for('view_projects'))

            # update files to remove project association
            for file in File.query.filter_by(project_id=project_id).all():
                file.project_id = None

            # delete project
            db.session.delete(project)
            db.session.commit()

            flash(f'Project "{project.project_name}" deleted  !', 'success')
            return redirect(url_for('view_projects'))

        except Exception as e:
            flash(f'Error deleting project: {str(e)}', 'danger')
            return redirect(url_for('view_projects'))
        




    @login_required
    def file_management(self):
        """shows the file management page with all files and projects."""
        try:
            files = File.query.all()
            projects = Project.query.all()
            return render_template('files.html',
                                  files=[f.to_dict() for f in files],
                                  projects=[p.to_dict() for p in projects])
        except Exception as e:

            flash(f'error loading file management:  {str(e)}', 'danger')
            return redirect(url_for('view_projects'))



    @login_required
    def upload_file(self):
        """handles file uploads. Saves to filesystem and DB. """

        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(url_for('file_management'))

        file = request.files['file']

        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(url_for('file_management'))

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(self.app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # get form data
            file_description = request.form.get('file_description', '')
            project_id = request.form.get('project_id')

            # find associated project
            project_id = int(project_id) if project_id and project_id.isdigit() else None

            # determine file type
            file_extension = os.path.splitext(filename)[1][1:].lower()

            # get file size
            file_size = os.path.getsize(file_path)

            # get current user 
            current_user = User.query.first()

            try:
                # create new file
                new_file = File(
                    project_id=project_id,
                    file_name=filename,
                    file_path=file_path,
                    file_size=file_size,
                    file_type=file_extension,
                    uploaded_by_id=current_user.id if current_user else None,
                    description=file_description
                )

                db.session.add(new_file)
                db.session.commit()

                # create initial version
                version = FileVersion(
                    file_id=new_file.id,
                    version_number=1,
                    changed_by_id=current_user.id if current_user else None,
                    version_path=file_path
                )

                db.session.add(version)
                db.session.commit()

                flash('file uploaded !', 'success')

            except ValueError as e:
                # delete the uploaded file if there was an error
                try:
                    os.remove(file_path)
                except:
                    pass

                flash(f'Error uploading file: {str(e)}', 'danger')

        # redirect 
        if project_id:
            return redirect(url_for('project_details', project_id=project_id))
        else:
            return redirect(url_for('file_management'))    @login_required
    def download_file(self, file_id):
        """download file route """

        try:

            file = File.query.get(file_id)
            if not file or not os.path.exists(file.file_path):
                flash('File not found!', 'danger')
                return redirect(url_for('file_management'))

            directory = os.path.dirname(file.file_path)
            filename = os.path.basename(file.file_path)
            return send_from_directory(directory, filename, as_attachment=True)

        except Exception as e:

            flash(f'Error downloading file: {str(e)}' , 'danger' )
            return redirect(url_for('file_management'))




    @login_required
    def delete_file(self, file_id):
        """delete file route ,deletes a file and its versions from DB and filesystem."""

        file = File.query.get(file_id)
        if not file:
            flash('File not found!', 'danger')
            return redirect(url_for('file_management'))

        project_id = file.project_id

        # delete file from filesystem

        try:
            if os.path.exists(file.file_path):
                os.remove(file.file_path)
        except Exception as e:
            print(f"Error deleting file {file.file_path}: {e}")

        # delete associated versions

        for version in file.versions:
            try:
                if os.path.exists(version.version_path) and version.version_path != file.file_path:
                    os.remove(version.version_path)
            except Exception as e:

                print(f"Error deleting version file {version.version_path}: {e}")

        # delete file from database

        db.session.delete(file)
        db.session.commit()

        flash(f'File "{file.file_name}" deleted  !', 'success')

        # redirect
        if project_id:
            return redirect(url_for('project_details', project_id=project_id))
        else:
            return redirect(url_for('file_management'))

    @login_required
    def view_tasks(self, project_id):
        """shows all tasks for a project."""
        try:
            project = Project.query.get(project_id)
            if not project:
                flash('Project not found!', 'danger')
                return redirect(url_for('view_projects'))

            # get project data
            tasks = project.get_tasks()
            milestones = project.get_milestones()

            # get all users for task assignment
            users = User.query.all()

            # convert project to dict and add milestones
            project_dict = project.to_dict()
            project_dict['milestones'] = [m.to_dict() for m in milestones]

            return render_template('task.html',
                                  project=project_dict,
                                  tasks=[t.to_dict() for t in tasks],
                                  users=users)
        except Exception as e:

            flash(f'Error fetching tasks: {str(e)}', 'danger')
            return redirect(url_for('view_projects'))






    @login_required
    def create_task(self, project_id):
        """create a new task route."""
        project = Project.query.get(project_id)
        if not project:
            flash('project not found', 'danger')
            return redirect(url_for('view_projects'))

        # get form data
        title = request.form.get('task_title')
        description = request.form.get('task_description')
        importance = request.form.get('task_importance', Task.IMPORTANCE_NORMAL)
        status = request.form.get('task_status', Task.STATUS_NOT_BEGUN)
        due_date_str = request.form.get('task_due_date')
        assigned_to_id = request.form.get('task_assigned_to_id')
        milestone_id = request.form.get('task_milestone_id')
        estimated_duration_str = request.form.get('task_estimated_duration')
        start_date_str = request.form.get('task_start_date')

        # parse dates
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None

        # parse estimated duration
        estimated_duration = int(estimated_duration_str) if estimated_duration_str and estimated_duration_str.isdigit() else None

        # convert IDs to integers 
        assigned_to_id = int(assigned_to_id) if assigned_to_id and assigned_to_id.isdigit() else None
        milestone_id = int(milestone_id) if milestone_id and milestone_id.isdigit() else None

        # get current user
        current_user = User.query.first()

        # create new task using model method
        try:
            Task.create_task(
                title=title,
                project_id=project_id,
                description=description,
                importance=importance,
                status=status,
                due_date=due_date,
                milestone_id=milestone_id,
                assigned_to_id=assigned_to_id,
                created_by_id=current_user.id if current_user else None,
                estimated_duration=estimated_duration,
                start_date=start_date
            )

            flash('Task created  ', 'success')
        except ValueError as e:
            flash(f'Error creating task: {str(e)}', 'danger')

        return redirect(url_for('view_tasks', project_id=project_id))
    


    @login_required
    def edit_task(self, task_id):
        """edit an existing task route."""
        task = Task.query.get(task_id)
        if not task:
            flash('task not foud', 'danger')
            return redirect(url_for('view_projects'))

        project_id = task.project_id

        # get form data
        title = request.form.get('task_title')
        description = request.form.get('task_description')
        importance = request.form.get('task_importance')
        status = request.form.get('task_status')
        due_date_str = request.form.get('task_due_date')
        assigned_to_id = request.form.get('task_assigned_to_id')
        milestone_id = request.form.get('task_milestone_id')
        estimated_duration_str = request.form.get('task_estimated_duration')
        start_date_str = request.form.get('task_start_date')
        actual_start_str = request.form.get('task_actual_start')
        actual_end_str = request.form.get('task_actual_end')


        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None

        # parse datetime values
        try:
            actual_start_datetime = datetime.strptime(actual_start_str, '%Y-%m-%dT%H:%M') if actual_start_str else None
        except ValueError:
            actual_start_datetime = None

        try:
            actual_end_datetime = datetime.strptime(actual_end_str, '%Y-%m-%dT%H:%M') if actual_end_str else None
        except ValueError:
            actual_end_datetime = None

        # parse estimated duration
        estimated_duration = int(estimated_duration_str) if estimated_duration_str and estimated_duration_str.isdigit() else None

        # convert IDs to integers 
        assigned_to_id = int(assigned_to_id) if assigned_to_id and assigned_to_id.isdigit() else None
        milestone_id = int(milestone_id) if milestone_id and milestone_id.isdigit() else None

        try:
            # update task using model method
            task.update(
                title=title,
                description=description,
                importance=importance,
                status=status,
                due_date=due_date,
                milestone_id=milestone_id,
                assigned_to_id=assigned_to_id,
                estimated_duration=estimated_duration,
                start_date=start_date,
                actual_start_datetime=actual_start_datetime,
                actual_end_datetime=actual_end_datetime
            )
            flash('Task updated  ', 'success')
        except Exception as e:
            flash(f'Error updating task: {str(e)}', 'danger')

        return redirect(url_for('view_tasks', project_id=project_id))

    @login_required
    def delete_task(self, task_id):
        """delete task route."""
        task = Task.query.get(task_id)
        if not task:
            flash('Task not found', 'danger')
            return redirect(url_for('view_projects'))

        # Delete task using model method
        project_id = task.delete()

        flash(f'Task "{task.title}" deleted  ', 'success')
        return redirect(url_for('view_tasks', project_id=project_id))




    @login_required
    def view_milestones(self, project_id):
        """show all milestones for a project."""
        try:
            project = Project.query.get(project_id)
            if not project:
                flash('Project not found', 'danger')
                return redirect(url_for('view_projects'))

            # Get project milestones
            milestones = project.get_milestones()

            # Get all tasks for the project
            tasks = project.get_tasks()

            return render_template('milestones.html',
                                  project=project.to_dict(),
                                  milestones=[m.to_dict() for m in milestones],
                                  tasks=[t.to_dict() for t in tasks])
        except Exception as e:
            flash(f'Error fetching milestones: {str(e)}', 'danger')
            return redirect(url_for('view_projects'))
        



    @login_required
    def create_milestone(self, project_id):
        """create a new milestone route."""
        project = Project.query.get(project_id)
        if not project:
            flash('Project not found!', 'danger')
            return redirect(url_for('view_projects'))

        # get form data
        title = request.form.get('milestone_title')
        description = request.form.get('milestone_description')
        due_date_str = request.form.get('milestone_due_date')

        # parse date
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None

        # create new milestone using model method
        try:
            Milestone.create_milestone(
                title=title,
                project_id=project_id,
                due_date=due_date,
                description=description
            )

            flash('Milestone created', 'success')
        except ValueError as e:
            flash(f'Error creating milestone: {str(e)}', 'danger')

        return redirect(url_for('view_milestones', project_id=project_id))

    @login_required
    def edit_milestone(self, milestone_id):
        """edit an existing milestone route."""
        milestone = Milestone.query.get(milestone_id)
        if not milestone:
            flash('Milestone not found', 'danger')
            return redirect(url_for('view_projects'))

        project_id = milestone.project_id

        # get form data
        title = request.form.get('milestone_title')
        description = request.form.get('milestone_description')
        due_date_str = request.form.get('milestone_due_date')
        status = request.form.get('milestone_status')

        # parse date
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None

        try:
            # update milestone fields
            milestone.title = title if title else milestone.title
            milestone.description = description if description is not None else milestone.description
            milestone.due_date = due_date if due_date else milestone.due_date

            if status and status in Milestone.STATUS_OPTIONS:
                milestone.status = status

            # save changes
            db.session.commit()

            # update completion percentage
            milestone.update_completion()

            flash('Milestone updated  !', 'success')
        except Exception as e:
            flash(f'Error updating milestone: {str(e)}', 'danger')

        return redirect(url_for('view_milestones', project_id=project_id))

    @login_required
    def delete_milestone(self, milestone_id):
        """delete milestone route."""
        milestone = Milestone.query.get(milestone_id)
        if not milestone:
            flash('Milestone not found!', 'danger')
            return redirect(url_for('view_projects'))

        project_id = milestone.project_id

        try:
            # unlink tasks from this milestone
            for task in milestone.tasks:
                task.milestone_id = None

            # delete milestone
            db.session.delete(milestone)
            db.session.commit()

            flash('Milestone deleted  ', 'success')
        except Exception as e:
            flash(f'Error deleting milestone: {str(e)}', 'danger')

        return redirect(url_for('view_milestones', project_id=project_id))




    @login_required
    def view_progress(self, project_id):
        """show project progress dashboard with milestone tracking."""
        try:
            project = Project.query.get(project_id)
            if not project:
                flash('Project not found!', 'danger')
                return redirect(url_for('view_projects'))

            # update milestone progress
            project.update_milestone_progress()

            # get project milestones
            milestones = project.get_milestones()

            # get active milestone
            active_milestone = project.get_active_milestone()

            # get all tasks for the project
            tasks = project.get_tasks()

            # calculate overall project completion
            total_tasks = len(tasks)
            completed_tasks = sum(1 for task in tasks if task.status == Task.STATUS_FINISHED)
            project_completion = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

            return render_template('progress_dashboard.html',
                                  project=project.to_dict(),
                                  milestones=[m.to_dict() for m in milestones],
                                  active_milestone=active_milestone.to_dict() if active_milestone else None,
                                  tasks=[t.to_dict() for t in tasks],
                                  project_completion=project_completion)
        except Exception as e:
            flash(f'Error loading progress dashboard: {str(e)}', 'danger')
            return redirect(url_for('view_projects'))
        



    @login_required
    def view_reports(self, project_id):
        """view reports for a project."""
        project = Project.query.get(project_id)
        if not project:
            flash('Project not found!', 'danger')
            return redirect(url_for('view_projects'))

        # Get all reports for this project using model method
        reports = project.get_reports()

        return render_template('project_reports.html',
                              project=project.to_dict(),

                              reports=[r.to_dict() for r in reports])
    




    @login_required
    def generate_report(self, project_id):
        """generate a new report for a project."""
        project = Project.query.get(project_id)
        if not project:
            flash('project not found', 'danger')
            return redirect(url_for('view_projects'))

        # get current user 
        current_user = User.query.first()

        # get report filters 
        filters = {
            'include_completed_tasks': 'include_completed_tasks' in request.form,
            'include_missed_deadlines': 'include_missed_deadlines' in request.form,
            'include_contributions': 'include_contributions' in request.form,
            'format': request.form.get('report_format', 'pdf')
        }

        # If no filters are selected, include all by default
        if not any([filters['include_completed_tasks'],
                   filters['include_missed_deadlines'],
                   filters['include_contributions']]):
            filters['include_completed_tasks'] = True
            filters['include_missed_deadlines'] = True
            filters['include_contributions'] = True

        try:
            # create new report using model method
            Report.create_report(
                project_id=project_id,
                report_type=Report.TYPE_PERFORMANCE,
                created_by_id=current_user.id if current_user else None,
                filters=filters
            )

            flash('Report generation started. You will be notified when it is ready.', 'success')
        except Exception as e:
            flash(f'Error starting report generation: {str(e)}', 'danger')

        return redirect(url_for('view_reports', project_id=project_id))




    @login_required
    def download_report(self, report_id):
        """download a generated report."""
        report = Report.query.get(report_id)
        if not report:
            flash('Report not found', 'danger')
            return redirect(url_for('view_projects'))

        if report.status != Report.STATUS_COMPLETED:
            flash('Report is not ready for download yet.', 'warning')
            return redirect(url_for('view_reports', project_id=report.project_id))

        if not os.path.exists(report.file_path):
            flash('Report file not found!', 'danger')
            return redirect(url_for('view_reports', project_id=report.project_id))

        directory = os.path.dirname(report.file_path)
        filename = os.path.basename(report.file_path)

        return send_from_directory(directory, filename, as_attachment=True)



    @login_required
    def report_status(self, report_id):
        """get the status of a report generation process."""
        report = Report.query.get(report_id)
        if not report:
            return {'status': 'error', 'message': 'Report not found'}

        # get status using model method
        return report.get_status()




    # message routes handlers
    @login_required
    def view_messages(self):
        """show the messages page with all conversations."""
        try:
            # get current user 
            current_user = User.query.first()

            if not current_user:
                flash('No user found in the system!', 'danger')
                return redirect(url_for('view_projects'))

            # get all users except current user
            users = User.query.filter(User.id != current_user.id).all()

            # get all projects for the dropdown
            projects = Project.query.all()

            # get unread message counts for each user using CommunicationFacade
            unread_counts = {}
            for user in users:
                # use facade to get unread messages instead of direct query
                unread_messages = self.communication_facade.get_unread_messages(current_user.id)
                # count messages from this specific user
                unread_count = sum(1 for msg in unread_messages if msg.senderID == user.id)
                unread_counts[user.id] = unread_count

            return render_template('messages.html',
                                  current_user=current_user,
                                  users=users,
                                  projects=projects,
                                  unread_counts=unread_counts,
                                  selected_user=None,
                                  messages=[])

        except Exception as e:
            flash(f'Error loading messages: {str(e)}', 'danger')
            return redirect(url_for('view_projects'))





    @login_required
    def view_conversation(self, user_id):
        """show conversation with a specific user."""
        try:
            # get current user 
            current_user = User.query.first()

            if not current_user:
                flash('No user found in the system!', 'danger')
                return redirect(url_for('view_projects'))

            # get the selected user
            selected_user = User.query.get(user_id)
            if not selected_user:
                flash('User not found!', 'danger')
                return redirect(url_for('view_messages'))

            # get all users except current user
            users = User.query.filter(User.id != current_user.id).all()

            # get all projects for the dropdown
            projects = Project.query.all()

            # get project_id from query parameter if provided
            project_id = request.args.get('project_id')
            selected_project = None
            if project_id and project_id.isdigit():
                selected_project = Project.query.get(int(project_id))            # get messages between current user and selected user using CommunicationFacade
            
            if selected_project:
                messages = self.communication_facade.get_conversation(
                    current_user.id,
                    selected_user.id,
                    project_id=selected_project.id
                )
            else:
                messages = self.communication_facade.get_conversation(
                    current_user.id,
                    selected_user.id
                )

            # mark messages  read using facade
            for message in messages:
                if message.senderID == selected_user.id and message.receiverID == current_user.id and not message.isRead:
                    self.communication_facade.mark_message_as_read(message.messageID)

            # get unread message counts for each user using CommunicationFacade
            unread_counts = {}
            for user in users:
                # use the  facade to get unread messages instead of direct query
                unread_messages = self.communication_facade.get_unread_messages(current_user.id)
                # count messages from this specific user
                unread_count = sum(1 for msg in unread_messages if msg.senderID == user.id)
                unread_counts[user.id] = unread_count

            return render_template('messages.html',
                                  current_user=current_user,
                                  users=users,
                                  projects=projects,
                                  unread_counts=unread_counts,
                                  selected_user=selected_user,
                                  selected_user_id=selected_user.id,
                                  selected_project=selected_project,
                                  messages=messages)

        except Exception as e:
            flash(f'Error loading conversation: {str(e)}', 'danger')
            return redirect(url_for('view_messages'))
        



    @login_required
    def send_message(self):
        """send a new message using CommunicationFacade"""
        try:
            # get current user 
            current_user = User.query.first()

            if not current_user:
                flash('No user found in the system!', 'danger')
                return redirect(url_for('view_projects'))

            # get form data
            receiver_id = request.form.get('receiver_id')
            content = request.form.get('content')
            project_id = request.form.get('project_id')

            
            if not receiver_id or not receiver_id.isdigit():
                flash('Invalid receiver!', 'danger')
                return redirect(url_for('view_messages'))

            if not content or not content.strip():
                flash('Message cannot be empty!', 'danger')
                return redirect(url_for('view_conversation', user_id=int(receiver_id)))

            # convert id to integers
            receiver_id = int(receiver_id)
            project_id = int(project_id) if project_id and project_id.isdigit() else None

            # send message using CommunicationFacade
            new_message = self.communication_facade.send_direct_message(
                sender_id=current_user.id,
                receiver_id=receiver_id,
                content=content,
                project_id=project_id
            )

            if new_message:
                flash('Message sent  !', 'success')
            else:
                flash('Failed to send message. Please try again.', 'danger')            # Redirect back to the conversation
            if project_id:
                return redirect(url_for('view_conversation', user_id=receiver_id, project_id=project_id))
            else:
                return redirect(url_for('view_conversation', user_id=receiver_id))

        except Exception as e:
            flash(f'Error sending message: {str(e)}', 'danger')
            return redirect(url_for('view_messages'))


    @login_required
    def search_messages(self):
        """search messages by keyword, sender, and date range."""
        try:
            # get current user
            current_user = User.query.first()

            if not current_user:
                flash('No user found in the system!', 'danger')
                return redirect(url_for('view_projects'))

            # get search parameters
            keyword = request.args.get('keyword', '').strip()
            sender_id = request.args.get('sender_id')
            date_from = request.args.get('date_from')
            date_to = request.args.get('date_to')

            
            query = Message.query.filter(
                (Message.senderID == current_user.id) |
                (Message.receiverID == current_user.id)
            )

            if keyword:
                query = query.filter(Message.content.ilike(f'%{keyword}%'))

            if sender_id and sender_id.isdigit():
                sender_id = int(sender_id)
                query = query.filter(Message.senderID == sender_id)

            if date_from:
                try:
                    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
                    query = query.filter(Message.timestamp >= date_from_obj)
                except ValueError:
                    flash('invalid from date format', 'warning')

            if date_to:
                try:
                    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
                    query = query.filter(Message.timestamp <= date_to_obj)
                except ValueError:
                    flash('invalid to date format', 'warning')

            
            messages = query.order_by(Message.timestamp.desc()).all()

            # get all users except current user
            users = User.query.filter(User.id != current_user.id).all()

            # Get all projects for the dropdown
            projects = Project.query.all()            # Get unread message counts for each user using CommunicationFacade
            unread_counts = {}
            for user in users:
                # Use facade to get unread messages instead of direct query
                unread_messages = self.communication_facade.get_unread_messages(current_user.id)
                # Count messages from this specific user
                unread_count = sum(1 for msg in unread_messages if msg.senderID == user.id)
                unread_counts[user.id] = unread_count

            # Prepare search results message
            if messages:
                flash(f'Found {len(messages)} messages matching your search criteria.', 'success')
            else:
                flash('No messages found matching your search keywords.', 'info')

            return render_template('messages.html',
                                  current_user=current_user,
                                  users=users,
                                  projects=projects,
                                  unread_counts=unread_counts,
                                  selected_user=None,
                                  messages=messages,
                                  is_search_result=True,
                                  search_keyword=keyword,
                                  search_sender_id=sender_id,
                                  search_date_from=date_from,
                                  search_date_to=date_to)

        except Exception as e:
            flash(f'Error searching messages: {str(e)}', 'danger')
            return redirect(url_for('view_messages'))



    # User Authentication Routes
    def login(self):
        """handle user login."""
        try:
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')
                remember_me = 'remember_me' in request.form

                # find the user by username
                user = User.query.filter_by(username=username.lower()).first()

                # Check if user exists and password is correct
                if user and user.check_password(password):
                    # Check if email is verified
                    if not user.is_verified:
                        flash('Please verify your email before logging in.', 'warning')
                        return redirect(url_for('login'))

                    # Log the user in
                    login_user(user, remember=remember_me)

                    # Update last login timestamp
                    user.update_last_login()
                    db.session.commit()

                    # set remember me token if requested
                    if remember_me:
                        user.set_remember_me_token()
                        db.session.commit()

                    flash(f'Welcome back, {user.get_full_name()}!', 'success')

                    # Redirect to the page the user was trying to access, or to projects page
                    next_page = request.args.get('next')
                    if next_page:
                        return redirect(next_page)
                    else:
                        return redirect(url_for('view_projects'))
                else:
                    flash('Invalid username or password.', 'danger')
                    return redirect(url_for('login'))

            # GET request - show login form
            return render_template('login.html')

        except Exception as e:
            flash(f'Error during login: {str(e)}', 'danger')
            return redirect(url_for('login'))

    def logout(self):
        """handle user logout."""
        try:
            # Clear remember me token if it exists
            if current_user.is_authenticated:
                current_user.clear_remember_me_token()
                db.session.commit()

            # Log the user out
            logout_user()

            flash('You have been logged out.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            flash(f'Error during logout: {str(e)}', 'danger')
            return redirect(url_for('view_projects'))

    def register(self):
        """handle user registration."""
        try:
            if request.method == 'POST':
                # get form data
                username = request.form.get('username')
                email = request.form.get('email')
                password = request.form.get('password')
                confirm_password = request.form.get('confirm_password')
                first_name = request.form.get('first_name')
                last_name = request.form.get('last_name')

                # check if passwords match
                if password != confirm_password:
                    flash('Passwords do not match.', 'danger')
                    return render_template('register.html')

                # Check if username already exists
                if User.query.filter_by(username=username.lower()).first():
                    flash('Username already exists.', 'danger')
                    return render_template('register.html')

                # Check if email already exists
                if User.query.filter_by(email=email.lower()).first():
                    flash('Email already exists.', 'danger')
                    return render_template('register.html')                # Get role from form - now required for all new registrations
                role = request.form.get('role')

                # Validate role selection
                if not role or role not in User.VALID_ROLES:
                    flash('Please select a valid role.', 'danger')
                    return render_template('register.html')

                # Create new user
                try:
                    new_user = User(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        role=role
                    )
                    db.session.add(new_user)
                    db.session.commit()

                    # Generate verification token
                    token = new_user.generate_verification_token()
                    db.session.commit()

                    # Create verification URL
                    verification_url = url_for('verify_email', token=token, _external=True)

                    # Send verification email using facade
                    self.notification_facade.send_email_verification(new_user, verification_url)

                    # For development, print the token
                    print(f"Verification URL for {email}: {verification_url}")

                    # Since we've modified the User model to auto-verify users in development,
                    # we'll show the registration success page
                    flash('Account created  ! Your account has been automatically verified for development purposes. You can now log in.', 'success')
                    return render_template('register_success.html', username=username, verification_url=verification_url)

                except ValueError as e:
                    flash(f'Error creating account: {str(e)}', 'danger')
                    return render_template('register.html')

            # GET request - show registration form
            return render_template('register.html')

        except Exception as e:
            flash(f'Error during registration: {str(e)}', 'danger')
            traceback.print_exc()  # Print the full traceback for debugging
            return render_template('register.html')
# the email stuff we have try to implement but we knew that it so cmplacated and need a lot of stuff so we stop
    def verify_email(self, token):
        """handle email verification."""
        try:
            # Find the token in the database
            auth_token = AuthToken.query.filter_by(token_value=token, token_type=AuthToken.TOKEN_TYPE_VERIFY).first()

            if not auth_token:
                flash('Invalid verification token.', 'danger')
                return redirect(url_for('login'))

            # Get the user associated with this token
            user = User.query.get(auth_token.user_id)

            if not user:
                flash('User not found.', 'danger')
                return redirect(url_for('login'))

            # Verify the email
            if user.verify_email(token):
                db.session.commit()
                # Show verification success page instead of redirecting to login
                return render_template('verification_success.html')
            else:
                flash('Verification token has expired. Please register again.', 'danger')
                return redirect(url_for('login'))

        except Exception as e:
            flash(f'Error during email verification: {str(e)}', 'danger')
            traceback.print_exc()
            return redirect(url_for('login'))

    def forgot_password(self):
        """handle forgot password requests."""
        try:
            if request.method == 'POST':
                email = request.form.get('email')

                # Find user by email
                user = User.query.filter_by(email=email.lower()).first()

                if user:
                    # Generate password reset token
                    token = user.generate_password_reset_token()
                    db.session.commit()

                    # Create reset URL
                    reset_url = url_for('reset_password', token=token, _external=True)                    # Send password reset email using facade
                    self.notification_facade.send_password_reset(user, reset_url)

                    # For development, print the token
                    print(f"Password reset URL for {email}: {reset_url}")

                    flash('Password reset link has been sent to your email.', 'success')
                else:
                    # Don't reveal that the email doesn't exist
                    flash('If your email is registered, you will receive a password reset link.', 'info')

                return redirect(url_for('login'))

            # GET request - show forgot password form
            return render_template('forgot_password.html')

        except Exception as e:
            flash(f'Error processing forgot password request: {str(e)}', 'danger')
            traceback.print_exc()
            return redirect(url_for('forgot_password'))

    def reset_password(self, token):
        """handle password reset."""
        try:
            if request.method == 'POST':
                password = request.form.get('password')
                confirm_password = request.form.get('confirm_password')

                # Check if passwords match
                if password != confirm_password:
                    flash('Passwords do not match.', 'danger')
                    return redirect(url_for('reset_password', token=token))

                # Find the token in the database
                auth_token = AuthToken.query.filter_by(token_value=token, token_type=AuthToken.TOKEN_TYPE_RESET).first()

                if not auth_token:
                    flash('Invalid reset token.', 'danger')
                    return redirect(url_for('login'))

                # Get the user associated with this token
                user = User.query.get(auth_token.user_id)

                if not user:
                    flash('User not found.', 'danger')
                    return redirect(url_for('login'))

                # Reset the password
                if user.reset_password(token, password):
                    db.session.commit()
                    flash('Password reset  ! You can now log in with your new password.', 'success')
                    return redirect(url_for('login'))
                else:
                    flash('Reset token has expired. Please request a new one.', 'danger')
                    return redirect(url_for('forgot_password'))

            # GET request - show reset password form
            # Check if token is valid
            auth_token = AuthToken.query.filter_by(token_value=token, token_type=AuthToken.TOKEN_TYPE_RESET).first()

            if not auth_token or not auth_token.is_valid():
                flash('Invalid or expired reset token. Please request a new one.', 'danger')
                return redirect(url_for('forgot_password'))

            return render_template('reset_password.html', token=token)

        except Exception as e:
            flash(f'Error resetting password: {str(e)}', 'danger')
            traceback.print_exc()
            return redirect(url_for('login'))    # Notification Routes
        



    @login_required
    def view_notifications(self):
        """view all notifications for the current user"""
        try:
            # get notifications from NotificationFacade
            all_notifications = self.notification_facade.get_user_notifications(current_user.id)
            unread_notifications = self.notification_facade.get_unread_notifications(current_user.id)

            return render_template('notifications.html',
                                 notifications=all_notifications,
                                 unread_count=len(unread_notifications))
        except Exception as e:
            flash(f'Error loading notifications: {str(e)}', 'danger')
            return redirect(url_for('dashboard'))




    @login_required
    def mark_notification_read(self, notification_id):
        """mark a specific notification as read """


        try:
            success = self.notification_facade.mark_notification_read(notification_id, current_user.id)
            if success:
                flash('Notification marked as read.', 'success')
            else:
                flash('Error marking notification as read.', 'danger')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

        return redirect(url_for('view_notifications'))
    




    @login_required
    def mark_all_notifications_read(self):
        """mark all notifications as read for the current user"""
        try:
            success = self.notification_facade.mark_all_notifications_read(current_user.id)
            if success:
                flash('All notifications marked as read.', 'success')
            else:
                flash('Error marking notifications as read.', 'danger')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

        return redirect(url_for('view_notifications'))
    



    @login_required
    def get_unread_notifications(self):
        """JSON endpoint to get unread notification count."""
        try:
            unread_notifications = self.notification_facade.get_unread_notifications(current_user.id)
            return jsonify({
                'success': True,
                'unread_count': len(unread_notifications),
                'notifications': [notif.to_dict() for notif in unread_notifications]
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500




    @login_required
    def create_test_notification(self):
        """create a test notification for testing """
        try:
            success = self.notification_facade.create_custom_notification(
                user_id=current_user.id,
                title="Test Notification",
                content="This is a test notification created"
            )
            if success:
                flash('Test notification created  !', 'success')
            else:
                flash('Error creating test notification.', 'danger')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

        return redirect(url_for('view_notifications'))




    # user management Routes
    @login_required
    def user_management(self):
        """show user management page"""
        try:
            # check if user has permission to manage users
            if not current_user.can_manage_users():
                flash('you  are do not have permission to access this page.', 'danger')
                return redirect(url_for('view_projects'))

            # get all users
            users = User.query.all()

            return render_template('user_management.html', users=users)

        except Exception as e:
            flash(f'Error loading user management: {str(e)}', 'danger')
            return redirect(url_for('view_projects'))
        



    @login_required
    def edit_user(self, user_id):
        """edit user details"""
        try:
            # Check if user has permission to manage users
            if not current_user.can_manage_users():
                flash('you do not have permission to access this page.', 'danger')
                return redirect(url_for('view_projects'))

            # get the user to edit
            user = User.query.get(user_id)

            if not user:
                flash('User not found.', 'danger')
                return redirect(url_for('user_management'))

            if request.method == 'POST':
                # update user details
                user.first_name = request.form.get('first_name')
                user.last_name = request.form.get('last_name')
                user.email = request.form.get('email')

                # update password if provided
                new_password = request.form.get('new_password')
                if new_password:
                    user.set_password(new_password)

                db.session.commit()

                flash('User updated  .', 'success')
                return redirect(url_for('user_management'))

            # GET request 
            return render_template('edit_user.html', user=user)

        except Exception as e:
            flash(f'Error editing user: {str(e)}', 'danger')
            return redirect(url_for('user_management'))
        


    @login_required
    def change_user_role(self, user_id):
        """show form to change user role."""
        try:
            # check if user like  has the  permission to assign roles
            if not current_user.can_assign_roles():
                flash('you do not have permission to assign roles.', 'danger')
                return redirect(url_for('user_management'))

            # get the user to change role
            user = User.query.get(user_id)

            if not user:
                flash('User not found.', 'danger')
                return redirect(url_for('user_management'))

            return render_template('change_user_role.html', user=user)

        except Exception as e:
            flash(f'error loading role change form: {str(e)}', 'danger')
            return redirect(url_for('user_management'))



    @login_required
    def update_user_role(self, user_id):
        """update user role"""
        try:
            # check if user has permission to assign roles
            if not current_user.can_assign_roles():
                flash('you do not have permission to assign roles', 'danger')
                return redirect(url_for('user_management'))

            # get the user to update
            user = User.query.get(user_id)

            if not user:
                flash('User not found.', 'danger')
                return redirect(url_for('user_management'))

            # get the new role
            new_role = request.form.get('role')



            # validate role
            if new_role not in User.VALID_ROLES:
                flash('Invalid role.', 'danger')
                return redirect(url_for('change_user_role', user_id=user_id))

            # check if this is the last admin in the cmt
            if user.role == User.ROLE_ADMIN and  new_role != User.ROLE_ADMIN:
                admin_count = User.query.filter_by(role=User.ROLE_ADMIN).count()
                if admin_count <= 1:
                    flash('cannot change role: this is the last admin', 'danger')
                    return redirect(url_for('change_user_role', user_id=user_id))

            # update the role
            user.role = new_role
            db.session.commit()

            flash(f'Role updated   for {user.get_full_name()}.', 'success')
            return redirect(url_for('user_management'))

        except Exception as e:
            flash(f'Error updating role: {str(e)}', 'danger')
            return redirect(url_for('user_management'))
        



    @login_required
    def batch_assign_roles(self):
        """assign roles to multiple users in one time"""
        try:
            # check if user has permission to assign roles
            if not current_user.can_assign_roles():
                flash('you do not have permission to assign roles.', 'danger')
                return redirect(url_for('user_management'))

            # get the new role
            new_role = request.form.get('role')

            # validate role
            if new_role not in User.VALID_ROLES:
                flash('Invalid role.', 'danger')
                return redirect(url_for('user_management'))

            # get selected users
            selected_users = request.form.getlist('selected_users')

            if not selected_users:
                flash('No users selected.', 'warning')
                return redirect(url_for('user_management'))

            # check if this would remove all admins
            if new_role != User.ROLE_ADMIN:
                admin_ids = [str(user.id) for user in User.query.filter_by(role=User.ROLE_ADMIN).all()]
                if all(admin_id in selected_users for admin_id in admin_ids):
                    flash('cannot change roles: This would remove all administrators.', 'danger')
                    return redirect(url_for('user_management'))

            # update roles
            updated_count = 0
            for user_id in selected_users:
                user = User.query.get(int(user_id))
                if user:
                    user.role = new_role
                    updated_count += 1

            db.session.commit()

            flash(f'Updated roles for {updated_count} users.', 'success')
            return redirect(url_for('user_management'))

        except Exception as e:
            flash(f'Error assigning roles: {str(e)}', 'danger')
            return redirect(url_for('user_management'))




    @login_required
    def delete_user(self, user_id):
        """delete a user"""
        try:
            # check if user has permission to delete users admin only can do this
            if current_user.role != User.ROLE_ADMIN:
                flash('you do not have permission to delete users', 'danger')
                return redirect(url_for('user_management'))

            # get the user to delete
            user = User.query.get(user_id)

            if not user:
                flash('User not found.', 'danger')
                return redirect(url_for('user_management'))

            # sure not  deleting him self
            if user.id == current_user.id:
                flash('You cannot delete your own account.', 'danger')
                return redirect(url_for('user_management'))

            # check if this is the last admin
            if user.role == User.ROLE_ADMIN:
                admin_count = User.query.filter_by(role=User.ROLE_ADMIN).count()
                if admin_count <= 1:
                    flash('Cannot delete: This is the last administrator.', 'danger')
                    return redirect(url_for('user_management'))

            # delete the user
            db.session.delete(user)
            db.session.commit()

            flash('User deleted  .', 'success')
            return redirect(url_for('user_management'))

        except Exception as e:
            flash(f'Error deleting user: {str(e)}', 'danger')
            return redirect(url_for('user_management'))


# create and run the application
if __name__ == '__main__':
    app = CMTApp()
    app.run(debug=True)
