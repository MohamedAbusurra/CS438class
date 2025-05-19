# forum post model
from datetime import datetime, timezone
from models.database import db
from models.UserManagement.user import User
from models.ProjectManagement.project import Project

class ForumPost(db.Model):
    __tablename__ = 'forum_posts'

    postID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userID = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    projectID = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)

    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    postTime = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


    # Relationships
    author = db.relationship('User', foreign_keys=[userID], backref=db.backref('forum_posts', lazy=True))
    associated_project = db.relationship('Project', foreign_keys=[projectID], backref=db.backref('project_forum_posts', lazy=True))
    
    replies = db.relationship('ForumReply', backref='parent_post', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, user_id: int, title: str, content: str, project_id: int = None):
        if not title or not title.strip():
            raise ValueError("Post title cannot be empty.")
        if not content or not content.strip():
            raise ValueError("Post content cannot be empty.")

        self.userID = user_id
        self.title = title
        self.content = content
        self.projectID = project_id

    def __repr__(self):
        return f"<ForumPost postID={self.postID} title='{self.title}' authorID={self.userID}>"

    def get_reply_count(self) -> int:
        try:
            return self.replies.count()
        except Exception as e:
            print(f"Error counting replies for post {self.postID}: {e}") 
            return 0