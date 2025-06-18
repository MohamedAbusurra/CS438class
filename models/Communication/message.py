# the file path must be this  models\Communication\message.py
from datetime  import datetime,  timezone
from  models.database import  db
from models.UserManagement.user  import  User
from models.ProjectManagement.project import  Project

# TODO: we may change this   later  if model paths change

class Message ( db.Model) :
    """
    represents a message in  the communication in the cmt .
    Each message is link to sender and  receiver and a project.
    """
    __tablename__ = 'messages' #  naming the table of the database

    messageID = db.Column(db.Integer,
                           primary_key=True, autoincrement=True) 
    senderID = db.Column(db.Integer,
                          db.ForeignKey('users.id'), nullable=False) 
    receiverID = db.Column(db.Integer,
                            db.ForeignKey('users.id'), nullable=False)
    projectID = db.Column(db.Integer,
                           db.ForeignKey('projects.id'), nullable=True) 

    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False) 
    isRead = db.Column(db.Boolean, default=False, nullable=False) 

    # Relationships SQLAlchemy understand the links
    # These will allow us to do stuff like `my_message.sender_user` if User model is correctly linked
    sender_user = db.relationship('User',
                                   foreign_keys=[senderID],  backref='sent_messages')
    receiver_user = db.relationship('User',
                                      foreign_keys=[receiverID],   backref='received_messages')
    associated_project = db.relationship('Project',
                                           foreign_keys=[projectID],  backref='project_messages')

    def __init__(self, sender_id: int, 
                 receiver_id: int,  message_content: str
                 , project_id: int = None):
        
        """
        constructor for the a Message class .
        init a new message with sender, receiver, content, and project.

    
        """
        # print(f"  DEBUG : creating message from {sender_id} to {receiver_id} for project {project_id}") # just for  debugging we may  remove it  later
        try:
            if not message_content:

                raise ValueError("message content cannot be empty")

            self.senderID = sender_id
            self.receiverID = receiver_id
            self.content = message_content 
            self.projectID = project_id 
            self.isRead = False 
            

            
        except ValueError as ve:

            print(f"error creating  message: {ve}")
            raise

        except Exception as e:
            # Catch-all for unoned issues
            print(f"An unexpected error occurred during message creation: {e}")
            # TODO: Add more  error handling 
            raise

    def get_content(self) ->  str :
        """
        returns the content of the  message

        returns :
            str like  the message content

        """
        try:
            the_actual_content = self.content
            return the_actual_content
        
        except AttributeError:
            print("error: Message object seems to be missing its content ")
            return "error: Content not available." 
        
        except Exception as e:
            print(f"unexpected error while getting content: {e}")

            # Fallback or re-raise
            return "Error retrieving content."

    def mark_as_read(self) ->  None :
        """
        marks the  message as read.
        sets the isRead flag  to True.
        """
        try:
            # print(f"DEBUG: Marking message {self.messageID} as read.") 
            if self.isRead:

                # print(f"Message {self.messageID} was already read, no change made.") 
                pass 
            else:
                self.isRead = True
                # db.session.add(self)
                # db.session.commit() 
                                 
            # print(f"DEBUG: Message {self.messageID} isRead status: {self.isRead}")
        except Exception as e:
            # what can go wrong here umm 
            print(f"an error occurred while marking message as read: {e}")
            

    # Maybe add a __repr__ for easy  debugging later?
    def __repr__(self):
        return f"<Message messageID={self.messageID} from={self.senderID} to={self.receiverID} read={self.isRead}>"

# if __name__ == '__main__':
#     # This block would require a full Flask app context to work with the db
#     print("This is just a model definition, not runnable on its own like this.")
#     # msg = Message(sender_id=1, receiver_id=2, message_content="Hello there!", project_id=1)
#     # print(msg.get_content())
#     # msg.mark_as_read()