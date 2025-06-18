class MessageService:
    def create_message(self, sender_id, recipient_id, content):
        
        from models.Communication.message import Message
        from models.database import db
        message = Message(sender_id=sender_id, receiver_id=recipient_id, message_content=content)
        db.session.add(message)
        db.session.commit()
        return message

    def attach_files(self, message, attachments):
        
        pass
