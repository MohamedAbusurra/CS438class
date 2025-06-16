import pytest
from datetime import datetime
from models.Forum import ForumPost, ForumReply
from models.UserManagement import User
from models.ProjectManagement import Project
from models.database import db


@pytest.fixture(scope='function')
def new_user():
    user = User(username="testuser", email="test@example.com")
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture(scope='function')
def new_project():
    project = Project(name="Test Project")
    db.session.add(project)
    db.session.commit()
    return project

@pytest.fixture(scope='function')
def clean_db():
    db.drop_all()
    db.create_all()
    yield
    db.session.remove()
    db.drop_all()


@pytest.mark.usefixtures("clean_db")
class TestForumPost:

    def test_valid_post_creation(self, new_user):
        post = ForumPost(user_id=new_user.id, title="Valid Title", content="Some content")
        db.session.add(post)
        db.session.commit()
        assert post.postID is not None
        assert post.title == "Valid Title"

    @pytest.mark.parametrize("title,content", [
        ("", "Some content"),
        ("   ", "Some content"),
        ("Valid Title", ""),
        ("Valid Title", "   ")
    ])
    def test_invalid_post_creation(self, new_user, title, content):
        with pytest.raises(ValueError):
            ForumPost(user_id=new_user.id, title=title, content=content)

    def test_optional_project_id(self, new_user):
        post = ForumPost(user_id=new_user.id, title="Test", content="Content", project_id=None)
        db.session.add(post)
        db.session.commit()
        assert post.projectID is None

    def test_post_with_project(self, new_user, new_project):
        post = ForumPost(user_id=new_user.id, title="Title", content="Content", project_id=new_project.id)
        db.session.add(post)
        db.session.commit()
        assert post.projectID == new_project.id
        assert post.associated_project == new_project

    def test_get_reply_count(self, new_user):
        post = ForumPost(user_id=new_user.id, title="Title", content="Content")
        db.session.add(post)
        db.session.commit()

        reply = ForumReply(post_id=post.postID, user_id=new_user.id, content="Reply content")
        db.session.add(reply)
        db.session.commit()

        assert post.get_reply_count() == 1

    def test_repr_format(self, new_user):
        post = ForumPost(user_id=new_user.id, title="Hello", content="World")
        db.session.add(post)
        db.session.commit()
        assert repr(post).startswith("<ForumPost postID=")


@pytest.mark.usefixtures("clean_db")
class TestForumReply:

    def test_valid_reply_creation(self, new_user):
        post = ForumPost(user_id=new_user.id, title="Post", content="Content")
        db.session.add(post)
        db.session.commit()

        reply = ForumReply(post_id=post.postID, user_id=new_user.id, content="A reply")
        db.session.add(reply)
        db.session.commit()

        assert reply.replyID is not None
        assert reply.postID == post.postID
        assert reply.author == new_user

    @pytest.mark.parametrize("content", ["", "   "])
    def test_invalid_reply_creation(self, new_user, content):
        post = ForumPost(user_id=new_user.id, title="Post", content="Content")
        db.session.add(post)
        db.session.commit()

        with pytest.raises(ValueError):
            ForumReply(post_id=post.postID, user_id=new_user.id, content=content)

    def test_reply_repr(self, new_user):
        post = ForumPost(user_id=new_user.id, title="Post", content="Content")
        db.session.add(post)
        db.session.commit()

        reply = ForumReply(post_id=post.postID, user_id=new_user.id, content="Test reply")
        db.session.add(reply)
        db.session.commit()

        assert repr(reply).startswith("<ForumReply replyID=")