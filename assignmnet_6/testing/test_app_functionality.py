"""
Comprehensive tests for main application functionality covering:
- User authentication (signup, login, password reset)
- Project creation with team member assignment
- File upload/download with versioning
- Task management and milestone tracking
- Real-time notifications
"""
import pytest
import tempfile
import os
from datetime import date, timedelta
from flask import url_for
from werkzeug.datastructures import FileStorage
from io import BytesIO

from models.database import db
from models.UserManagement.user import User
from models.UserManagement.auth_token import AuthToken
from models.ProjectManagement.project import Project
from models.ProjectManagement.milestone import Milestone
from models.TaskManagement.task import Task
from models.DocumentFileManagement.file import File
from models.Communication.message import Message
from models.Communication.notification import Notification
from app import CMTApp


@pytest.fixture
def app_instance():
    """create CMT app instance for testing"""
    return CMTApp()


@pytest.fixture
def client(app_instance):
    """create test client"""
    app_instance.app.config['TESTING'] = True
    app_instance.app.config['WTF_CSRF_ENABLED'] = False
    with app_instance.app.test_client() as client:
        with app_instance.app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


def test_disable_all():
    pytest.skip("all tests in this file are  disabled.")


class TestUserAuthentication:
    """test user authentication functionality"""
    
    def test_user_registration_valid_data(self, client):
        """test user registration with valid data"""
        try:
            response = client.post('/register', data={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'Password123',
                'first_name': 'New',
                'last_name': 'User'
            })
            
            # should redirect after successful registration
            assert response.status_code in [200, 302]
            
            # check user was created in database
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'newuser@example.com'
            assert user.check_password('Password123')
            
        except Exception as e:
            pytest.fail(f"user registration test failed: {str(e)}")
    
    def test_user_registration_weak_password(self, client):
        """test user registration with weak password"""
        try:
            response = client.post('/register', data={
                'username': 'weakuser',
                'email': 'weak@example.com',
                'password': 'weak',  # Too weak
                'first_name': 'Weak',
                'last_name': 'User'
            })
            
            # should not create user with weak password
            user = User.query.filter_by(username='weakuser').first()
            assert user is None
            
        except Exception as e:
            # expected to fail with weak password
            assert "password" in str(e).lower() or "weak" in str(e).lower()
    
    def test_user_login_valid_credentials(self, client, fresh_user):
        """test user login """
        try:
            response = client.post('/login', data={
                'username': fresh_user.username,
                'password': 'TestPass123'
            })
            
            # should redirect after successful login
            assert response.status_code in [200, 302]
            
        except Exception as e:
            pytest.fail(f"User login test failed: {str(e)}")
    
    def test_password_reset_token_generation(self, fresh_user):
        """test password reset token generation"""
        try:
            token = AuthToken.generate_token(
                user_id=fresh_user.id,
                token_type=AuthToken.TOKEN_TYPE_RESET,
                expiry_hours=1
            )
            
            assert token is not None
            assert len(token) > 10  # should be a reasonable length
            
            # verify token can be validated
            auth_token = AuthToken.validate_token(token, AuthToken.TOKEN_TYPE_RESET)
            assert auth_token is not None
            assert auth_token.user_id == fresh_user.id
            
        except Exception as e:
            pytest.fail(f"password reset token test failed: {str(e)}")




class TestProjectManagement:
    """test project management functionality"""
    
    def test_project_creation_with_milestones(self, fresh_user):
        """test creating a project with required milestones"""
        try:
            # create project
            project = Project.create_project(
                project_name="Test Project",
                description="A test project for the unit testing",
                start_date=date.today(),
                expected_end_date=date.today() + timedelta(days=30),
                created_by_id=fresh_user.id
            )
            
            assert project.id is not None
            assert project.project_name == "Test Project"
            assert project.created_by_id == fresh_user.id
            
            # add required milestones
            milestone1 = Milestone.create_milestone(
                title="planning Phase",
                project_id=project.id,
                due_date=date.today() + timedelta(days=10),
                description="complete project planning"
            )
            
            milestone2 = Milestone.create_milestone(
                title="implementation Phase",
                project_id=project.id,
                due_date=date.today() + timedelta(days=20),
                description="implement core features"
            )
            
            assert milestone1.id is not None
            assert milestone2.id is not None
            
            # make sure the  milestones are linked to project
            project_milestones = project.get_milestones()
            assert len(project_milestones) == 2
            
        except Exception as e:
            pytest.fail(f"project creation test failed: {str(e)}")
    
    def test_team_member_assignment(self, fresh_user):
        """test assigning team members to project"""
        try:
            # create additional users
            user2 = User(
                username="teammember1",
                email="team1@example.com",
                password="TeamPass123",
                role=User.ROLE_TEAM_MEMBER
            )
            user3 = User(
                username="projectmgr1",
                email="pm1@example.com",
                password="PMPass123",
                role=User.ROLE_PROJECT_MANAGER
            )
            
            db.session.add_all([user2, user3])
            db.session.commit()
            
            # create project
            project = Project.create_project(
                project_name="Team Project",
                description="Project with team members",
                start_date=date.today(),
                created_by_id=fresh_user.id
            )
            
            # create tasks and assign to team members
            task1 = Task.create_task(
                title="Design Task",
                project_id=project.id,
                description="Design the system",
                assigned_to_id=user2.id,
                created_by_id=fresh_user.id,
                due_date=date.today() + timedelta(days=5)
            )
            
            task2 = Task.create_task(
                title="Management Task",
                project_id=project.id,
                description="Manage the project",
                assigned_to_id=user3.id,
                created_by_id=fresh_user.id,
                due_date=date.today() + timedelta(days=7)
            )
            
            assert task1.assignedToId == user2.id
            assert task2.assignedToId == user3.id
            
            # verify tasks are linked to project
            project_tasks = project.get_tasks()
            assert len(project_tasks) == 2
            
        except Exception as e:
            pytest.fail(f"Team member assignment test failed: {str(e)}")


class TestFileManagement:
    """test file management functionality """
    
    def test_file_upload_docx_format(self, fresh_user):
        """test uploading DOCX file with size validation"""
        try:
            # create a mock DOCX file
            file_content = b"PK\x03\x04" + b"x" * 1000  # Mock DOCX content
            
            file_obj = File(
                project_id=None,
                file_name="test_document.docx",
                file_path="/tmp/test_document.docx",
                file_size=len(file_content),
                file_type=".docx",
                uploaded_by_id=fresh_user.id,
                description="Test document upload"
            )
            
            db.session.add(file_obj)
            db.session.commit()
            
            assert file_obj.id is not None
            assert file_obj.file_type == "docx"
            assert file_obj.file_size == len(file_content)
            assert file_obj.uploaded_by_id == fresh_user.id
            
            # test formatted size display
            formatted_size = file_obj.get_formatted_size()
            assert "KB" in formatted_size or "B" in formatted_size
            
        except Exception as e:
            pytest.fail(f"file upload test failed: {str(e)}")
    
    def test_file_size_limit_validation(self, fresh_user):
        """test file size limit validation 100MB"""
        try:
            # try to create file larger than 100MB
            large_size = 101 * 1024 * 1024  # 101 MB
            
            with pytest.raises(ValueError):
                File(
                    project_id=None,
                    file_name="large_file.docx",
                    file_path="/tmp/large_file.docx",
                    file_size=large_size,
                    file_type=".docx",
                    uploaded_by_id=fresh_user.id
                )
                
        except Exception as e:
            if "size" not in str(e).lower():
                pytest.fail(f"File size validation test failed: {str(e)}")
    
    def test_unsupported_file_type_rejection(self, fresh_user):
        """test rejection of unsupported file types."""
        try:
            with pytest.raises(ValueError):
                File(
                    project_id=None,
                    file_name="malware.exe",
                    file_path="/tmp/malware.exe",
                    file_size=1024,
                    file_type=".exe",
                    uploaded_by_id=fresh_user.id
                )
                
        except Exception as e:
            if "type" not in str(e).lower() and "supported" not in str(e).lower():
                pytest.fail(f"File type validation test failed: {str(e)}")


class TestCommunication:
    """test communication functionality"""

    def test_direct_messaging_between_users(self, fresh_user):
        """test direct messaging functionality """
        try:
            # create second user
            user2 = User(
                username="receiver",
                email="receiver@example.com",
                password="RecvPass123"
            )
            db.session.add(user2)
            db.session.commit()

            # send message
            message = Message(
                sender_id=fresh_user.id,
                receiver_id=user2.id,
                message_content="Hello, this is a test message!"
            )
            db.session.add(message)
            db.session.commit()

            assert message.messageID is not None
            assert message.get_content() == "Hello, this is a test message!"
            assert message.senderID == fresh_user.id
            assert message.receiverID == user2.id
            assert message.isRead is False

            # test marking as read
            message.mark_as_read()
            db.session.commit()

            # verify message is marked as read
            updated_message = db.session.get(Message, message.messageID)
            assert updated_message.isRead is True

        except Exception as e:
            pytest.fail(f"Direct messaging test failed: {str(e)}")

    def test_message_search_by_keyword(self, fresh_user):
        """Test message search by keyword functionality."""
        try:
            # create second user
            user2 = User(
                username="searcher",
                email="searcher@example.com",
                password="SearchPass123"
            )
            db.session.add(user2)
            db.session.commit()




            # create multiple messages with different content
            messages = [
                Message(sender_id=fresh_user.id, receiver_id=user2.id,
                       message_content="Project deadline approaching"),
                Message(sender_id=fresh_user.id, receiver_id=user2.id,
                       message_content="Meeting scheduled for tomorrow"),
                Message(sender_id=user2.id, receiver_id=fresh_user.id,
                       message_content="Deadline extension requested")
            ]

            db.session.add_all(messages)
            db.session.commit()

            # search for messages containing "deadline"
            search_results = Message.query.filter(
                Message.content.ilike("%deadline%")
            ).all()

            assert len(search_results) == 2
            for msg in search_results:
                assert "deadline" in msg.content.lower()

        except Exception as e:
            pytest.fail(f"message search test failed: {str(e)}")

    def test_message_search_by_sender_name(self, fresh_user):
        """test message search by sender name"""
        try:
            # create second user with specific name
            user2 = User(
                username="omer_ali",
                email="omer@example.com",
                password="omerPass123",
                first_name="omer",
                last_name="ali"
            )
            db.session.add(user2)
            db.session.commit()

            # create messages from different senders
            msg1 = Message(sender_id=fresh_user.id, receiver_id=user2.id,
                          message_content="Message from test user")
            msg2 = Message(sender_id=user2.id, receiver_id=fresh_user.id,
                          message_content="Message from John")

            db.session.add_all([msg1, msg2])
            db.session.commit()

            # search messages by sender username
            john_messages = Message.query.join(User, Message.senderID == User.id).filter(
                User.username == "omer_ali"
            ).all()

            assert len(john_messages) == 1
            assert john_messages[0].senderID == user2.id

        except Exception as e:
            pytest.fail(f"Message search by sender test failed: {str(e)}")


class TestNotifications:
    """test real-time notification functionality"""

    def test_task_assignment_notification(self, fresh_user):
        """test notification creation when task is assigned"""
        try:
            # create project and task
            project = Project.create_project(
                project_name="notification test Project",
                description="Testing notifications",
                start_date=date.today(),
                created_by_id=fresh_user.id
            )

            task = Task.create_task(
                title="Notification Task",
                project_id=project.id,
                description="Task for notification testing",
                assigned_to_id=fresh_user.id,
                created_by_id=fresh_user.id,
                due_date=date.today() + timedelta(days=3)
            )

            # create notification for task assignment
            notification = Notification.create_notification(
                user_id=fresh_user.id,
                title="new Task Assigned",
                content=f"you have been assigned task: {task.taskTitle}",  # Fixed: use taskTitle
                notification_type=Notification.TYPE_TASK_ASSIGNED,
                task_id=task.id,
                project_id=project.id
            )

            assert notification.id is not None
            assert notification.user_id == fresh_user.id
            assert notification.task_id == task.id
            assert notification.project_id == project.id
            assert notification.is_read is False

            # test notification link generation
            link = notification.get_link()
            assert f"/task/{task.id}" in link or f"/project/{project.id}" in link

        except Exception as e:
            pytest.fail(f"Task assignment notification test failed: {str(e)}")

    def test_deadline_approaching_notification(self, fresh_user):
        """test notification for approaching deadlines"""
        try:
            # create project and task with near deadline
            project = Project.create_project(
                project_name="Deadline Test Project",
                description="Testing deadline notifications",
                start_date=date.today(),
                created_by_id=fresh_user.id
            )

            task = Task.create_task(
                title="Urgent Task",
                project_id=project.id,
                description="Task with approaching deadline",
                assigned_to_id=fresh_user.id,
                created_by_id=fresh_user.id,
                due_date=date.today() + timedelta(days=1)  # Due tomorrow
            )

            # create deadline notification
            notification = Notification.create_notification(
                user_id=fresh_user.id,
                title="Deadline Approaching",
                content=f"Task '{task.taskTitle}' is due soon!",  # Fixed: use taskTitle
                notification_type=Notification.TYPE_DEADLINE_APPROACHING,
                task_id=task.id,
                project_id=project.id
            )

            assert notification.id is not None
            assert notification.notification_type == Notification.TYPE_DEADLINE_APPROACHING
            assert "deadline" in notification.title.lower() or "due" in notification.content.lower()

        except Exception as e:
            pytest.fail(f"Deadline notification test failed: {str(e)}")

    def test_notification_mark_all_read(self, fresh_user):
        """test marking all notifications as read"""
        try:
            # create multiple notifications
            notifications = []
            for i in range(3):
                notif = Notification.create_notification(
                    user_id=fresh_user.id,
                    title=f"Test Notification {i+1}",
                    content=f"Content for notification {i+1}"
                )
                notifications.append(notif)

            # verify all are unread
            unread_count = Notification.query.filter_by(
                user_id=fresh_user.id, is_read=False
            ).count()
            assert unread_count == 3

            # mark all as read
            Notification.query.filter_by(user_id=fresh_user.id).update(
                {"is_read": True}
            )
            db.session.commit()

            # verify all are now read
            unread_count = Notification.query.filter_by(
                user_id=fresh_user.id, is_read=False
            ).count()
            assert unread_count == 0

        except Exception as e:
            pytest.fail(f"mark all notifications read test failed: {str(e)}")


class TestUserRoleManagement:
    """test user role management"""

    def test_role_assignment_and_permissions(self):
        """test user role assignment and permission checking"""
        try:
            # create users with different roles
            admin = User(
                username="admin_user",
                email="admin@example.com",
                password="AdminPass123",
                role=User.ROLE_ADMIN
            )

            supervisor = User(
                username= "supervisor_user",
                email= "supervisor@example.com",
                password="SuperPass123",
                role=User.ROLE_SUPERVISOR
            )

            project_manager = User(
                username=  "pm_user",
                email="pm@example.com",
                password=  "PMPass123",
                role=User.ROLE_PROJECT_MANAGER
            )

            team_member = User(
                username="team_user",

                email="team@example.com",
                password= "TeamPass123",
                role=User.ROLE_TEAM_MEMBER
            )

            db.session.add_all([admin, supervisor, project_manager, team_member])
            db.session.commit()

            # test role assignments
            assert admin.role == User.ROLE_ADMIN
            assert supervisor.role == User.ROLE_SUPERVISOR
            assert project_manager.role == User.ROLE_PROJECT_MANAGER
            assert team_member.role == User.ROLE_TEAM_MEMBER

            # test permission hierarchy
            assert admin.has_permission(User.ROLE_ADMIN) is True
            assert admin.has_permission(User.ROLE_SUPERVISOR) is True
            assert admin.has_permission(User.ROLE_PROJECT_MANAGER) is True
            assert admin.has_permission(User.ROLE_TEAM_MEMBER) is True

            assert supervisor.has_permission(User.ROLE_ADMIN) is False
            assert supervisor.has_permission(User.ROLE_SUPERVISOR) is True
            assert supervisor.has_permission(User.ROLE_PROJECT_MANAGER) is True
            assert supervisor.has_permission(User.ROLE_TEAM_MEMBER) is True

            assert team_member.has_permission(User.ROLE_ADMIN) is False
            assert team_member.has_permission(User.ROLE_SUPERVISOR) is False
            assert team_member.has_permission(User.ROLE_TEAM_MEMBER) is True

            # Test management permissions
            assert admin.can_manage_users() is True
            assert supervisor.can_manage_users() is True
            assert team_member.can_manage_users() is False

        except Exception as e:
            pytest.fail(f"Role management test failed: {str(e)}")


class TestMilestoneTracking:
    """test milestone tracking and progress monitoring"""

    def test_milestone_progress_calculation(self, fresh_user):
        """test milestone progress calculation based on tasks"""
        try:
            # create project and milestone
            project = Project.create_project(
                project_name="Progress Test Project",
                description="Testing milestone progress",
                start_date=date.today(),
                created_by_id=fresh_user.id
            )

            milestone = Milestone.create_milestone(
                title="Test Milestone",
                project_id=project.id,
                due_date=date.today() + timedelta(days=10),
                description="Milestone for progress testing"
            )

            # create tasks for the milestone
            task1 = Task.create_task(
                title="Task 1",
                project_id=project.id,
                description="First task",
                milestone_id=milestone.id,  # Link to milestone
                status=Task.STATUS_FINISHED,  # Fixed: use correct constant
                created_by_id=fresh_user.id
            )

            task2 = Task.create_task(
                title="Task 2",
                project_id=project.id,
                description="Second task",
                milestone_id=milestone.id,  # Link to milestone
                status=Task.statusInProgress,  # Fixed: use correct constant
                created_by_id=fresh_user.id
            )

            task3 = Task.create_task(
                title="Task 3",
                project_id=project.id,
                description="Third task",
                milestone_id=milestone.id,  # Link to milestone
                status=Task.STATUS_NOT_BEGUN,
                created_by_id=fresh_user.id
            )

            # update milestone completion
            completion_percentage = milestone.update_completion()

            # should be approximately 33% (1 out of 3 tasks completed)
            assert 30 <= completion_percentage <= 40

            # update project milestone progress
            project.update_milestone_progress()

        except Exception as e:
            pytest.fail(f"Milestone progress test failed: {str(e)}")



    def test_real_time_progress_monitoring(self, fresh_user):
        """test real-time progress  when task status changes"""
        try:
            # create project and milestone
            project = Project.create_project(
                project_name="Real-time Test Project",
                description="Testing real-time updates",
                start_date=date.today(),
                created_by_id=fresh_user.id
            )

            milestone = Milestone.create_milestone(
                title="Real-time Milestone",
                project_id=project.id,
                due_date=date.today() + timedelta(days=15)
            )

            # create task
            task = Task.create_task(
                title="Dynamic Task",
                project_id=project.id,
                description="Task for real-time testing",
                milestone_id=milestone.id,  # Link to milestone
                status=Task.STATUS_NOT_BEGUN,
                created_by_id=fresh_user.id
            )

            # initial progress should be like 0%
            initial_progress = milestone.update_completion()
            assert initial_progress == 0.0

            # change task status to in progress
            task.status = Task.statusInProgress  # Fixed: use correct constant
            db.session.commit()

            # progress should still be 0% 
            in_progress_completion = milestone.update_completion()
            assert in_progress_completion == 0.0

            # Change task status to completed
            task.status = Task.STATUS_FINISHED  # Fixed: use correct constant
            db.session.commit()

            # progress should now be 100%
            completed_progress = milestone.update_completion()
            assert completed_progress == 100.0

        except Exception as e:
            pytest.fail(f"real-time progress monitoring test failed: {str(e)}")


class TestUserModelDirect:
    """direct unit tests for User model methods """
    def test_user_password_methods(self, test_app):
        with test_app.app_context():
            user = User(username="coveruser", email="cover@example.com", password="InitPass123")
            db.session.add(user)
            db.session.commit()
            # set_password and check_password
            user.set_password("NewPass123")
            assert user.check_password("NewPass123")
            assert not user.check_password("WrongPass")

    def test_user_get_full_name_and_id(self, test_app):
        with test_app.app_context():
            user = User(username="fulluser", email="full@example.com", password="TestPass123", first_name="First", last_name="Last")
            db.session.add(user)
            db.session.commit()
            assert user.get_full_name() == "First Last"
            assert user.get_id() == str(user.id)

    def test_user_permission_methods(self, test_app):
        with test_app.app_context():
            user = User(username="adminuser", email="admin@example.com", password="TestPass123", role=User.ROLE_ADMIN)
            db.session.add(user)
            db.session.commit()
            assert user.has_permission(User.ROLE_ADMIN)
            assert user.can_manage_users()
            assert user.can_assign_roles()

    def test_user_token_and_reset_methods(self, test_app):
        with test_app.app_context():
            user = User(username="tokenuser", email="token@example.com", password="TestPass123")
            db.session.add(user)
            db.session.commit()
            token = user.generate_verification_token()
            assert token is not None
            assert user.verify_email(token)
            reset_token = user.generate_password_reset_token()
            assert reset_token is not None
            assert user.reset_password(reset_token, "ResetPass123")
            assert user.check_password("ResetPass123")

    def test_user_misc_methods(self, test_app):
        with test_app.app_context():
            user = User(username="miscuser", email="misc@example.com", password="TestPass123")
            db.session.add(user)
            db.session.commit()
            user.set_remember_me_token()
            user.clear_remember_me_token()
            user.update_last_login()
            d = user.to_dict()
            assert isinstance(d, dict)
            assert d["username"] == "miscuser"
