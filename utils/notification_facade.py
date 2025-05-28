from .email_utils import send_verification_email, send_password_reset_email
from  .notification_utils import (

    create_task_assigned_notification,

    create_deadline_approaching_notification,
    create_notification  # For general/custom in -app notifications
)
from models import Notification, db

class NotificationFacade:
    """
    provides a simplified interface for sending various types of notifications
    """

    def send_email_verification(self,
                                 user,
                                   verification_url):
        """
        sends an email verification link to the user.
        returns:
            bool: True if email was sent successfully, False otherwise.
        """
        return send_verification_email(user, verification_url)

    def send_password_reset(self, user, reset_url):
        """
        Sends a password reset link to the user via email.
        Args:
            user: User object (must have .email attribute).
            reset_url (str): The password reset URL.
        Returns:
            bool: True if email was sent successfully, False otherwise.
        """
        return send_password_reset_email(user, reset_url)

    def notify_task_assigned(self, task, assignee_user):
        """
        Notifies a user that a task has been assigned to them.
        Creates an in-app notification.
        
        returns:
            bool: True if the in-app notification was created successfully.
        """
        # Create in-app notification using the specialized function from notification_utils
        in_app_notif_created = create_task_assigned_notification(
            task_id=task.id,

            assignee_id=assignee_user.id
        )


        return in_app_notif_created is not None

    def notify_deadline_approaching(self, task):
        """
        notifies the assignee of a task that its deadline is approaching.
        Creates an in-app notification.
        returns:
            bool: True if the in-app notification was created successfully.
        """
        # Create in-app notification using the specialized function from notification_utils
        in_app_notif_created = create_deadline_approaching_notification(task_id=task.id)

        

        return in_app_notif_created is not None

    def send_custom_in_app_notification(self, user_id, title, content,
                                        notification_type, # Should be one of Notification.TYPE_* constants
                                        project_id=None, task_id=None, milestone_id=None):
        """
        Sends a custom in-app notification using the generic create_notification function.
        returns:
            bool: True if the notification was created successfully.
        """
        notification = create_notification(
            user_id=user_id,
            title=title,
            notification_type=notification_type, # Pass the constant directly
            content=content,
            project_id=project_id,
            task_id=task_id,
            milestone_id=milestone_id
        )
        return notification is not None

    def get_user_notifications(self, user_id):
        """
        Get all notifications for a user.

        Returns:
            list: List of notification objects.
        """
        try:
            return Notification.query.filter_by(user_id=user_id).order_by(Notification.timestamp.desc()).all()
        except Exception as e:
            print(f"error {e}")
            return []

    def get_unread_notifications(self, user_id):
        """
        Get unread notifications for a user.
        returns:
            list: List of unread notification objects.
        """
        try:
            return Notification.query.filter_by(user_id=user_id, is_read=False).order_by(Notification.timestamp.desc()).all()
        except Exception as e:
            print(f"error {e}")
            return []

    def mark_notification_read(self, notification_id, user_id):
        """
        Mark a specific notification as read.
        returns:
            bool: True if marked successfully.
        """
        try:
            notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
            if notification:
                notification.is_read = True
                db.session.commit()
                return True
            return False
        except Exception as e:
            print(f"error {e}")
            return False

    def mark_all_notifications_read(self, user_id):
        """
        Mark all notifications as read for a user.
        returns:
            bool: True if marked successfully.
        """
        try:
            Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
            db.session.commit()
            return True
        except Exception as e:
            print(f"eror{e}")
            db.session.rollback()
            return False

    def create_custom_notification(self, user_id, title, content=None, notification_type=None):
        """
        create a custom notification.
       
        returns:
            bool: True if created successfully.
        """
        try:
            if notification_type is None:
                notification_type = Notification.TYPE_CUSTOM

            notification = create_notification(
                user_id=user_id,
                title=title,
                content=content,
                notification_type=notification_type
            )
            return notification is not None
        except Exception as e:
            print(f"error {e}")
            return False

