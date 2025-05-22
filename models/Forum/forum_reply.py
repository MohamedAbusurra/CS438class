# forum reply for forum posting model
from datetime import datetime, timezone
from models.database import db
from models.UserManagement.user import User


class ForumReply(db.Model):
    __tablename__ = 'forum_replies'

    replyID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    postID = db.Column(db.Integer, db.ForeignKey('forum_posts.postID'), nullable=False)
    userID = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    content = db.Column(db.Text, nullable=False)
    replyTime = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    author = db.relationship('User', foreign_keys=[userID], backref=db.backref('forum_replies', lazy=True))


    def __init__(self, post_id: int, user_id: int, content: str):
        if not content or not content.strip():
            raise ValueError("Reply content cannot be empty.")

        self.postID = post_id
        self.userID = user_id
        self.content = content

    def __repr__(self):
        return f"<ForumReply replyID={self.replyID} postID={self.postID} authorID={self.userID}>"