from models.database import db
from models.Communication.message import Message
from models.Communication.notification import Notification
from models.UserManagement.user import User
# we can import other  models like Project,  for linking later

class CommunicationFacade:
    """
    provides a simplified interface for managing communication in the cmt
    """

    def send_direct_message(self,
                            sender_id:    int,
                            receiver_id:   int,
                            content:  str, 
                            project_id: int = None)  -> Message   | None:
        """
        creates and saves a direct  message.


        returns:
            the created Message object or None 
        """
        try:
            # basic valid
            if not all([sender_id,  receiver_id,  content]):
                raise ValueError("Sender id, Receiver id you need to give them to me.")
            
            # Ensure users exist (optional, DB foreign keys should handle this)
            # sender = User.query.get(sender_id)
            # receiver = User.query.get(receiver_id)
            # if not sender or not receiver:
            #     raise ValueError("Invalid sender or receiver ID.")

            message =    Message(
                sender_id =sender_id,
                receiver_id =receiver_id,
                message_content  =content,
                project_id=  project_id
            )


            db.session.add(message)

            db.session.commit()
            return message
        
        except ValueError as ve:
            print(f"valueError in send_direct_message  :   {ve}")
            # db.session.rollback() # not import  if commit fails 
            return None
        except Exception as e:
            print(f"error sending direct   message: {e}")
            db.session.rollback()
            return None

    def create_system_notification(self, 
                                   user_id: int,
                                    title: str,
                                    notification_type: str,
                                    content: str = None, 
                                   project_id: int = None,
                                    task_id: int = None,
                                    milestone_id: int = None) -> Notification | None:
        """
        creates and saves a system notification using the Notification model class method.

        returns:
            the created Notification object or None 
        """
        try:
            # The Notification.create_notification  method like handles the  validation and DB session
            notification = Notification.create_notification(
                user_id=user_id,

                title=title,


                notification_type=notification_type,
                content=content,
                project_id=project_id,

                task_id=task_id,
                milestone_id=milestone_id
            )
            return notification
        except Exception as e:
            # The create_notification method in Notification model like prints errors 
            print(f"error {e}")

            return None

    def get_unread_messages(self, user_id: int) -> list[Message]:
        """
        Retrieves all unread messages for a specific user.

        returns:
            a list  unread Message objects .
        """
        try:
            
            # user = User.query.get(user_id)


            # if not user:
            #     raise ValueError("invalid user id.")

            unread_messages =   Message.query.filter_by(receiverID   =user_id  , isRead=False).order_by(Message.timestamp.desc()).all()
            return unread_messages
        

        except ValueError as ve:
            print(f"error {ve}")
            return []
        except Exception as e:

            print(f"error  {e}")
            return []

    def get_unread_notifications(self, user_id: int) -> list[Notification]:
        """
        Retrieves all unread notifications for a specific user.
        returns:
            a list unread notification objects.
        """
        try:
            unread_notifications  =   Notification.query.filter_by(user_id  =user_id  ,   is_read=False).order_by(Notification.timestamp.desc()).all()
            return unread_notifications
        
        except ValueError as ve: # Should not occur with current query
            print(f"eroor {ve}")
            return []
        except Exception as e:
            print(f"rrror  {e}")
            return []

    def get_all_user_notifications(self, user_id: int,
                                    include_read: bool = True,
                                      limit: int = 100) -> list[Notification]:
        """
        retrieves notifications for a user.
        returns:
            a list  Notification objects.
        """
        try:
            query = Notification.query.filter_by(user_id=user_id)
            if not include_read:
                query = query.filter_by(is_read=False)
            
            notifications = query.order_by(Notification.timestamp.desc()).limit(limit).all()
            return notifications
        except Exception as e:
            print(f"Error retrieving all user notifications: {e}")
            return []

    def get_conversation(self, user1_id: int, user2_id: int, project_id: int = None) -> list[Message]:
        """
        Retrieves the conversation messages between two users, optionally filtered by project.

        Args:
            user1_id: The ID of the first user.
            user2_id: The ID of the second user.
            project_id: Optional ID of the project to filter messages by.

        Returns:
            A list of Message objects, ordered by timestamp.
        """
        try:
            query = Message.query.filter(
                ((Message.senderID == user1_id) & (Message.receiverID == user2_id)) |
                ((Message.senderID == user2_id) & (Message.receiverID == user1_id))
            )
            if project_id is not None:
                query = query.filter(Message.projectID == project_id)
            
            messages = query.order_by(Message.timestamp.asc()).all()
            return messages
        except Exception as e:
            print(f"Error retrieving conversation: {e}")
            return []

    def mark_message_as_read(self, message_id: int) -> bool:
        """
        Marks a specific message as read.

        Args:
            message_id: The ID of the message to mark as read.

        Returns:
            True if successful, False otherwise.
        """
        try:
            message = Message.query.get(message_id)
            if message:
                message.mark_as_read() # This method in Message model should handle commit
                db.session.commit() # mark_as_read in Message model doesn't commit, so we do it here.
                return True
            return False
        except Exception as e:
            print(f"Error marking message as read: {e}")
            db.session.rollback()
            return False

    def mark_notification_as_read(self, notification_id: int) -> bool:
        """
        Marks a specific notification as read.

        Args:
            notification_id: The ID of the notification to mark as read.

        Returns:
            True if successful, False otherwise.
        """
        try:
            notification = Notification.query.get(notification_id)
            if notification:
                return notification.mark_as_read() # This method in Notification model handles commit
            return False
        except Exception as e:
            print(f"Error marking notification as read: {e}")
            # The mark_as_read in Notification model should handle rollback if it does its own commit
            return False

    def mark_all_user_notifications_as_read(self, user_id: int) -> int:
        """
        Marks all unread notifications for a specific user as read.

        Args:
            user_id: The ID of the user whose notifications are to be marked as read.

        Returns:
            The number of notifications marked as read.
        """
        count = 0
        try:
            unread_notifications = Notification.query.filter_by(user_id=user_id, is_read=False).all()
            if not unread_notifications:
                return 0
            
            for notification in unread_notifications:
                notification.is_read = True
                db.session.add(notification) # Add to session for batch commit
            db.session.commit()
            count = len(unread_notifications)
            return count
        except Exception as e:
            print(f"Error marking all user notifications as read: {e}")
            db.session.rollback()
            return 0

# Example Usage (for testing purposes, typically not here)
# if __name__ == '__main__':
#     # This would require a Flask app context
#     # from flask import Flask
#     # app = Flask(__name__)
#     # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Or your actual DB URI
#     # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     # db.init_app(app)
#     # with app.app_context():
#     #     db.create_all() # Create tables if they don't exist

#     #     # Create dummy users (ensure User model is defined and imported)
#     #     user1 = User(username='user1', email='user1@example.com', password='password')
#     #     user2 = User(username='user2', email='user2@example.com', password='password')
#     #     db.session.add_all([user1, user2])
#     #     db.session.commit()

#     #     facade = CommunicationFacade()
        
#     #     # Test sending a message
#     #     msg = facade.send_direct_message(sender_id=user1.id, receiver_id=user2.id, content="Hello from facade!")
#     #     if msg:
#     #         print(f"Message sent: {msg.id} - {msg.content}")
#     #     else:
#     #         print("Failed to send message.")

#     #     # Test creating a notification
#     #     notif = facade.create_system_notification(user_id=user1.id, title="Test Notification", notification_type=Notification.TYPE_CUSTOM, content="This is a test from facade.")
#     #     if notif:
#     #         print(f"Notification created: {notif.id} - {notif.title}")
#     #     else:
#     #         print("Failed to create notification.")

#     #     # Test retrieving unread messages
#     #     unread_msgs = facade.get_unread_messages(user_id=user2.id)
#     #     print(f"User {user2.id} has {len(unread_msgs)} unread messages.")
#     #     for m in unread_msgs:
#     #         print(f"  Msg ID {m.messageID}: {m.content}")
#     #         facade.mark_message_as_read(m.messageID)
#     #         print(f"  Msg ID {m.messageID} marked as read.")
        
#     #     # Test retrieving unread notifications
#     #     unread_notifs = facade.get_unread_notifications(user_id=user1.id)
#     #     print(f"User {user1.id} has {len(unread_notifs)} unread notifications.")
#     #     for n in unread_notifs:
#     #         print(f"  Notif ID {n.id}: {n.title}")
#     #         facade.mark_notification_as_read(n.id)
#     #         print(f"  Notif ID {n.id} marked as read.")
            
#     #     db.session.remove()
#     #     db.drop_all()
