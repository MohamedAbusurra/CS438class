from models.database import db
from models.Communication.message import Message
from models.Communication.notification import Notification
from models.UserManagement.user import User
from models.Communication.message_service import MessageService
from models.Communication.notification_service import NotificationService
from models.Communication.email_service import EmailService

# we can import other  models like Project,  for linking later

class CommunicationFacade:
    """
    provides a simplified interface for managing communication in the cmt
    """

    def __init__(self):
        self.message_service = MessageService()
        self.notification_service = NotificationService()
        self.email_service = EmailService()

    def send_message(self, sender_id, recipient_id, content, attachments=None):
        # Simplified interface hiding complex subsystem interactions
        message = self.message_service.create_message(sender_id, recipient_id, content)
        if attachments:
            self.message_service.attach_files(message, attachments)
        self.notification_service.notify_recipient(recipient_id)
        return message

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
            print(f"error {e}")
            return []

    def get_conversation(self,
                          user1_id: int, 
                          user2_id: int, 
                          project_id: int = None) -> list[Message]:
        

        """
        get the conversation messages between two users
        returns:
            a list of Message objects,o by timestamp.
        """
        try:
            query = Message.query.filter(

                ((Message.senderID == user1_id)  & (Message.receiverID == user2_id)) |
                ((Message.senderID == user2_id) &  (Message.receiverID == user1_id))
            )
            if project_id is not None:

                query =   query.filter(Message.projectID == project_id)
            
            messages =  query.order_by(Message.timestamp.asc()).all()
            return messages
        


        except Exception as e:
            print(f"error  {e}")
            return []

    def mark_message_as_read(self,
                             message_id: int) -> bool:
        """
        marks a specific message as read.

        returns:
            True if good, False else.
        """
        try:
            message = Message.query.get(message_id)
            if message:
                message.mark_as_read() 
                db.session.commit() # mark_as_read in Message model doesn't commit
                return True
            

            return False
        except Exception as e:
            print(f"Error marking message as read: {e}")
            db.session.rollback()
            return False

    def mark_notification_as_read(self, notification_id: int) -> bool:
        """
        marks a specific notification as read.
        returns:
            True if successful, False otherwise.
        """
        try:
            notification = Notification.query.get(notification_id)
            if notification:

                return notification.mark_as_read() # This method in Notification model handles commit
            return False
        except Exception as e:
            print(f"error {e}")
            # The mark_as_read in Notification model should handle rollback if it does its own commit
            return False

    def mark_all_user_notifications_as_read(self,
                                             user_id: int) -> int:
        """
        Marks all unread notifications for a specific user as read.

        returns:
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

