
# Covered classes / methods
#      User
#           __init__                 
#          set_password / check_password
#         has_permission
#           can_manage_users
#           can_assign_roles         
#          get_full_name

#      AuthToken
#           generate_token /  validate_token
#           is_valid /  invalidate

from __future__ import annotations

from datetime import timedelta, datetime, timezone
import random
import string

import pytest
from flask import Flask

from models.database import db
from models.UserManagement.user import User             # this  code under test
from models.UserManagement.auth_token import AuthToken  #  this code under test



#  basic Flask + SQLite just for the testing stuff  once for the module

@pytest.fixture(scope="session")
def test_app():
    app = Flask("roles_test")
    app.config["SQLALCHEMY_DATABASE_URI" ] = "sqlite:///:memory:"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS" ] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def _rand_txt(n: int = 6) -> str:

    return "".join(random.choices(string.ascii_lowercase, k=n))


def _make_user(role: str, *, username_prefix: str = "") -> User:
    """
    creates + commits a user with the given role.
    """
    usr = User(
        username=f"{username_prefix}{_rand_txt()}",
        email=f"{_rand_txt()}@example.com",
        password="Passw0rd!",    # valid password like ≥8, 1 digit, 1 uppercase
        role=role,
    )
    db.session.add(usr)

    db.session.commit()
    return usr


@pytest.fixture

def admin_user(test_app):
    with test_app.app_context():
        yield _make_user(User.ROLE_ADMIN, username_prefix="admin_")



@pytest.fixture
def supervisor_user(test_app):
    with test_app.app_context():
        yield _make_user(User.ROLE_SUPERVISOR, username_prefix="sup_")


@pytest.fixture
def team_member(test_app):
    with test_app.app_context():


        yield _make_user(User.ROLE_TEAM_MEMBER, username_prefix="tm_")



def test_user_init_and_password_roundtrip(test_app):
    """__init__, set_password, check_password happy path."""
    with test_app.app_context():
        u = _make_user(User.ROLE_PROJECT_MANAGER)

        assert u.role == User.ROLE_PROJECT_MANAGER
        assert u.check_password("Passw0rd!") is True
        assert u.check_password("wrongPwd") is False


def test_has_permission_hierarchy(admin_user, supervisor_user, team_member):
    """
    has_permission() 
        admin   ≥ all
        supervisor ≥ supervisor / project_manager / team_member
        team_member ≥ team_member
    """
    # admin
    assert admin_user.has_permission(User.ROLE_ADMIN) is True

    assert admin_user.has_permission(User.ROLE_SUPERVISOR) is True

    assert admin_user.has_permission(User.ROLE_TEAM_MEMBER) is True

    # supervisor
    assert supervisor_user.has_permission(User.ROLE_SUPERVISOR) is True

    assert supervisor_user.has_permission(User.ROLE_PROJECT_MANAGER) is True

    assert supervisor_user.has_permission(User.ROLE_ADMIN) is False

    # team member
    assert team_member.has_permission(User.ROLE_TEAM_MEMBER) is True

    assert team_member.has_permission(User.ROLE_PROJECT_MANAGER) is False
    assert team_member.has_permission(User.ROLE_ADMIN) is False


def test_manage_and_assign_flags(admin_user, supervisor_user, team_member):
    """
    can_manage_users()  → admin  or supervisor
    can_assign_roles()  → admin or supervisor 
    """
    # can_manage_users()

    assert admin_user.can_manage_users() is True

    assert supervisor_user.can_manage_users() is True
    assert team_member.can_manage_users() is False

    # can_assign_roles()  
    assert admin_user.can_assign_roles() is True

    assert supervisor_user.can_assign_roles() is False

    assert team_member.can_assign_roles() is False


#  Full-name 
def test_get_full_name_variants(test_app):
    with test_app.app_context():
        u1 = User(                       # first + last
            username="flname1",
            email="f1@example.com",
            password="Passw0rd!",
            first_name="sayf",
            last_name="ammar",
        )
        db.session.add(u1)
        assert u1.get_full_name() == "sayf ammar"

        u2 = User(                       # first only
            username="flname2",
            email="f2@example.com",
            password="Passw0rd!",
            first_name="omer",
        )
        db.session.add(u2)
        assert u2.get_full_name() == "omer"

        u3 = User(                       # no names
            username="flname3",
            email="f3@example.com",
            password="Passw0rd!",
        )
        db.session.add(u3)
        assert u3.get_full_name() == "flname3"


#  AuthToken 
def test_auth_token_lifecycle(test_app, admin_user):
    """
    generate_token  
    validate_token  
    invalidate     
    """
    with test_app.app_context():
        tok_val = AuthToken.generate_token(
            user_id=admin_user.id,
            token_type=AuthToken.TOKEN_TYPE_VERIFY,
            expiry_hours=1,
        )
        assert tok_val is not None

        token = AuthToken.validate_token(tok_val, AuthToken.TOKEN_TYPE_VERIFY)

        assert token is not None

        assert token.is_valid() is True

        token.invalidate()
        db.session.commit()
        assert token.is_valid() is False
        assert AuthToken.validate_token(tok_val, AuthToken.TOKEN_TYPE_VERIFY) is None


#  edge-cases / error paths
def test_bad_password_rejected(test_app):

    """__init__ should reject weak passwords """
    with test_app.app_context():
        with pytest.raises(ValueError):
            User(
                username="weak",
                email="weak@example.com",
                password="weakpwd",  # too short, no caps digit
            )


def test_invalid_role_defaults_to_team_member(test_app):
    """
    unknown role strings default to TEAM_MEMBER inside __init__().
    """
    with test_app.app_context():
        u = User(
            username="school",
            email="wr@example.com",
            password="Passw0rd!",
            role="space_cadet",          # invalid
        )
        assert u.role == User.ROLE_TEAM_MEMBER







