"""
shared fixtures; makes models importable and wires an in-memory DB.
"""
from pathlib import Path
import os

import pytest
from flask import Flask

# make src/ importable 
ROOT = Path(__file__).resolve().parents[2]  # go up to CS438class directory
if str(ROOT) not in os.sys.path:
    os.sys.path.insert(0, str(ROOT))

#  DB + app 
from models.database import db  # noqa: E402
from models.UserManagement.user import User  # noqa: E402


@pytest.fixture(scope="session")
def test_app():
    """lightweight Flask app using SQLite :memory:."""
    app = Flask("cmt_test")
    app.config.update(
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        TESTING=True,
    )
    db.init_app(app)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def fresh_user(test_app):
    """create a fresh user for testing."""
    with test_app.app_context():
        import random
        import string
        rand_suffix = ''.join(random.choices(string.ascii_lowercase, k=6))
        user = User(
            username=f"testuser_{rand_suffix}",
            email=f"test_{rand_suffix}@example.com",
            password="TestPass123",
            first_name="Test",
            last_name="User"
        )
        db.session.add(user)
        db.session.commit()
        # Refresh the user to avoid detached instance errors
        db.session.refresh(user)
        return user


@pytest.fixture
def other_user(test_app):
    """create another user for testing interactions."""
    with test_app.app_context():
        import random
        import string
        rand_suffix = ''.join(random.choices(string.ascii_lowercase, k=6))
        user = User(
            username=f"otheruser_{rand_suffix}",
            email=f"other_{rand_suffix}@example.com",
            password="TestPass123",
            first_name="Other",
            last_name="User"
        )
        db.session.add(user)
        db.session.commit()
        # Refresh the user to avoid detached instance errors
        db.session.refresh(user)
        return user