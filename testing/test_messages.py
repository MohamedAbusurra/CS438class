"""
Covers  user story and every public method in
models.Communication.message.Message:

     __init__          
     get_content
     mark_as_read
     __repr__          
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import random
import string

import pytest

from models.database import db

from models.Communication.message import Message
from models.UserManagement.user import User



@pytest.fixture
def other_user(test_app) -> User:
    """second committed user so we can test the  sender vs the  receiver queries"""
    with test_app.app_context():

        user = User(
            username=f"other_{_rand_txt()}",
            email=f"{_rand_txt()}@example.com",
            password="TestPass123",  # passwod  must 8+ chars, 1 number, 1 uppercase
        )
        db.session.add(user)

        db.session.commit()

        return user


def _rand_txt(n: int = 6) -> str:

    return "".join(random.choices (string.ascii_lowercase, k=n))



def test_message_creation_and_fields(test_app, fresh_user, other_user):
    """
     two users
    like when   a message is created with empty content
    then  the row get defaults.
    """
    with test_app.app_context():
        # Ensure users are in the current session
        db.session.add(fresh_user)
        db.session.add(other_user)
        db.session.commit()

        msg = Message(
            sender_id=fresh_user.id,
            receiver_id=other_user.id,
            message_content="cs438",
        )
        db.session.add(msg)
        db.session.commit()

        assert msg.messageID is not None
        assert msg.isRead is False                # default
        # Handle timezone comparison properly
        now_utc = datetime.now(timezone.utc)
        if msg.timestamp.tzinfo is None:
            # If timestamp is naive, compare with naive datetime
            assert msg.timestamp <= datetime.now()
        else:
            # If timestamp is timezone-aware, compare with timezone-aware datetime
            assert msg.timestamp <= now_utc
        assert msg.get_content() == "cs438"
        assert str(msg) is not None


def test_message_empty_content_raises(test_app,  fresh_user,  other_user):
    """constructor must not enbeled  an empty string or false content """
    with test_app.app_context():
        # Ensure users are in the current session
        db.session.add(fresh_user)
        db.session.add(other_user)
        db.session.commit()

        with pytest.raises(ValueError):
            Message(
                sender_id=fresh_user.id,
                receiver_id=other_user.id,
                message_content="",
            )


def test_mark_as_read_flag_changes(test_app, fresh_user, other_user):

    """mark_as_read() flips the flag – verify via query void-method check"""
    with test_app.app_context():
        # Ensure users are in the current session
        db.session.add(fresh_user)
        db.session.add(other_user)
        db.session.commit()

        msg = Message(
            sender_id=fresh_user.id,
            receiver_id=other_user.id,
            message_content="read me",
        )
        db.session.add(msg)
        db.session.commit()

        assert msg.isRead is False
        msg.mark_as_read()
        db.session.commit()

        refetched = db.session.get(Message, msg.messageID)
        assert refetched.isRead is True




#  Search 

def _seed_messages(sender: User, receiver: User):
    """create three  messages for search scenaruo ."""
    # Ensure users are in session
    db.session.add(sender)
    db.session.add(receiver)
    db.session.commit()

    msgs = [
        Message(sender_id=sender.id, receiver_id=receiver.id,
                message_content="school"),
        Message(sender_id=sender.id, receiver_id=receiver.id,
                message_content="mango", ),
        Message(sender_id=receiver.id, receiver_id=sender.id,
                message_content="phone"),
    ]
    db.session.add_all(msgs)
    db.session.commit()
    return msgs


def test_search_by_keyword(test_app, fresh_user, other_user):
    with test_app.app_context():
        _seed_messages(fresh_user, other_user)
        hits = (Message.query
                .filter(Message.content.ilike("%mango%"))
                .all())
        assert len(hits) == 1
        assert "mango" in hits[0].content  


def test_search_by_date_range(test_app, fresh_user, other_user):
    with test_app.app_context():
        # make sure user  are in the current session
        db.session.add(fresh_user)
        db.session.add(other_user)
        db.session.commit()

        old_msg = Message(
            sender_id=fresh_user.id,
            receiver_id=other_user.id,
            message_content="old message",
        )
        old_msg.timestamp = datetime.now(timezone.utc) - timedelta(days=2)
        db.session.add(old_msg)
        db.session.commit()

        _seed_messages(fresh_user, other_user)

        date_from = datetime.now(timezone.utc) - timedelta(days=1)

        recent_only = (Message.query
                       .filter(Message.timestamp >= date_from)
                       .all())

        # Handle timezone comparison properly
        for m in recent_only:
            if m.timestamp.tzinfo is None:
                # Convert timezone-aware date_from to naive for comparison
                date_from_naive = date_from.replace(tzinfo=None)
                assert m.timestamp >= date_from_naive
            else:
                assert m.timestamp >= date_from

        assert old_msg not in recent_only


def test_search_by_sender_name(test_app, fresh_user, other_user):
    """
    join against user to filter by sender name
    """
    with test_app.app_context():
        _seed_messages(fresh_user, other_user)

        hits = (Message.query
                .join(User, Message.senderID == User.id)
                .filter(User.username == fresh_user.username)
                .all())
        assert {h.senderID for h in hits} == {fresh_user.id}
