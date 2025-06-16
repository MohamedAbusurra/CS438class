import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
import hashlib

class User:
    ROLE_ADMIN = 'administrator'
    ROLE_TEAM_MEMBER = 'team_member'
    VALID_ROLES = [ROLE_ADMIN, ROLE_TEAM_MEMBER]

    def __init__(self, username, email, password, first_name=None, last_name=None, role=None):
        if not username or len(username) < 3:
            raise ValueError("username must be at least 3 characters")
        if not email or '@' not in email:
            raise ValueError("valid email address is required")
        if not self._is_valid_password(password):
            raise ValueError("password must 8 char and the for less one number and one uppercase letter")

        self.username = username.lower()
        self.email = email.lower()
        self.first_name = first_name
        self.last_name = last_name
        self.role = role if role in self.VALID_ROLES else self.ROLE_TEAM_MEMBER
        self.is_verified = True
        self.set_password(password)

    def _is_valid_password(self, password):
        import re
        if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'\d', password):
            return False
        return True

    def set_password(self, password):
        if not self._is_valid_password(password):
            raise ValueError("password must be strong")
        salt = "CMT_salt_value"
        self.password_hash = hashlib.sha256((password + salt).encode()).hexdigest()

    def check_password(self, password):
        salt = "CMT_salt_value"
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        return hashed == self.password_hash

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "role": self.role,
            "full_name": self.get_full_name(),
            "is_verified": self.is_verified
        }

    def has_permission(self, required_role):
        if self.role == self.ROLE_ADMIN:
            return True
        return self.role == required_role

    def can_assign_roles(self):
        return self.role == self.ROLE_ADMIN


@pytest.mark.parametrize("username", ["u", "", None])
def test_signup_invalid_username(username):
    with pytest.raises(ValueError, match="username"):
        User(username=username, email="test@example.com", password="Valid123")

@pytest.mark.parametrize("email", ["bademail", "", None])
def test_signup_invalid_email(email):
    with pytest.raises(ValueError, match="email"):
        User(username="validuser", email=email, password="Valid123")

@pytest.mark.parametrize("password", ["short", "lowercase123", "ALLCAPS123", "NoNumbers", ""])
def test_signup_invalid_password(password):
    with pytest.raises(ValueError, match="password"):
        User(username="validuser", email="test@example.com", password=password)

def test_signup_valid():
    user = User("TestUser", "user@example.com", "StrongPass1", "First", "Last", "administrator")
    assert user.username == "testuser"
    assert user.email == "user@example.com"
    assert user.is_verified is True
    assert user.role == User.ROLE_ADMIN
    assert user.check_password("StrongPass1") is True

def test_password_check_and_set():
    user = User("checkuser", "check@example.com", "Check1234")
    assert user.check_password("Check1234") is True
    assert user.check_password("wrongpass") is False

def test_user_to_dict():
    user = User("dictuser", "dict@example.com", "Dict1234", "Dict", "User")
    result = user.to_dict()
    assert result["username"] == "dictuser"
    assert result["full_name"] == "Dict User"
    assert result["is_verified"]

def test_permission_check():
    admin = User("admin", "a@example.com", "Admin1234", role="administrator")
    member = User("member", "m@example.com", "Member1234", role="team_member")
    assert admin.has_permission("team_member") is True
    assert member.has_permission("team_member") is True
    assert member.has_permission("administrator") is False

def test_assign_roles():
    admin = User("admin", "admin@example.com", "Admin1234", role="administrator")
    member = User("member", "mem@example.com", "Mem1234", role="team_member")
    assert admin.can_assign_roles() is True
    assert member.can_assign_roles() is False