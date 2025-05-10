from datetime import datetime, timezone
import traceback  # this for error tracking help me a lot beffor it I like machine spend a lot time debug
import re  # this are for regex  validation
import secrets  # for generat  tokens
import hashlib  # for simple password hashing 
from models.database import db

# TODO : replace simple hashing with  bcrypt library

class User(db.Model) :
    # this are the Flask-Login integration
    @property
    def is_authenticated(self):
        return True

    @property

    def is_active(self):
        return self.is_verified

    @property

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
    """
    user class for managing team members,
     project managers,
     supervisors, and administrators.

    this class handles:
    - User authentication
    - role-based  permissions
    - Email  verification
    - Password reset  functionality
    - remember  me feature
    """
    __tablename__ = 'users'  # database  table name

    # role constants 
    ROLE_ADMIN = 'administrator'

    ROLE_SUPERVISOR = 'academic_supervisor'

    ROLE_PROJECT_MANAGER = 'project_manager'

    ROLE_TEAM_MEMBER = 'team_member'

    # valid roles list 
    VALID_ROLES = [ROLE_ADMIN,
                    ROLE_SUPERVISOR,
                      ROLE_PROJECT_MANAGER,
                        ROLE_TEAM_MEMBER]

    # attributes
    id = db.Column(db.Integer ,
                    primary_key=True) 
    username   = db.Column(db.String(50) ,
                          unique=True,
                            nullable=False)  
    email =  db.Column(db.String(100) ,
                       unique=True,
                         nullable=False) 
     
    password_hash  = db.Column(db.String(128), 
                              nullable=False)  

    # name field 
    first_name =    db.Column(db.String(50))  
    last_name =   db.Column(db.String(50))  

    # role 
    role = db.Column(db.String(20),
                      default=ROLE_TEAM_MEMBER)  
                      
    is_verified = db.Column(db.Boolean ,
                             default=False)  

    # remember me token
    remember_me_token = db.Column(db.String(100))  

    # timestamps
    created_at = db.Column(db.DateTime ,
                            default=lambda: datetime.now(timezone.utc)) 
     
    last_login =    db.Column(db.DateTime)  # track the last login time

    # Relationships 
    """
    relationships between user table with other tabls
    I just use lazy=True I have stady about it in the documention but
    might switch to selection
    """
    projects_created = db.relationship(
        'Project',  # related model
        backref='creator',  # how the  project refer  back to  the User
        lazy=True,  # this for do not load auto
        foreign_keys='Project.created_by_id'  
    )

    # files uploaded by this user


    files_uploaded = db.relationship(
        'File',
        backref='uploader',

        lazy=True,
        foreign_keys='File.uploaded_by_id'
    )

    # file versions changed by this user

    file_versions = db.relationship(
        'FileVersion',

        backref='changed_by_user',
        lazy=True,

        foreign_keys='FileVersion.changed_by_id'
    )

    # tasks created by this user

    tasks_created = db.relationship(
        'Task',

        backref='creator',
        lazy=True,
        foreign_keys='Task.created_by_id'
    )

    # tasks assigned to this user

    tasks_assigned = db.relationship(
        'Task',
        backref='assignee',
        lazy=True,
        foreign_keys='Task.assignedToId' 
    )



    def __init__(self, username, 
                 email, password , first_name=None

                 , last_name=None,
                   role=None):
        """
        initialize a User object.
        """
        try:
            # validate inputs
            if not username or  len(username) < 3:
                raise ValueError("username must be at  least 3 characters")

            if not email or '@' not in email:
                raise ValueError("valid email  address is required")

            # password must be 8+ chars with  1 number and 1 uppercase
            if not self._is_valid_password(password):
                raise ValueError("password must  8 char and the for less one number and one  uppercase letter")

            # set the attributes
            self.username =    username.lower()  

            self.email =  email.lower()  

            self.first_name  =    first_name  
            self.last_name    =  last_name  

            # hash the password 
            self.set_password(password)

            # set role 
            if role and role in  self.VALID_ROLES:
                self.role =   role
            else: 
                self.role  = self.ROLE_TEAM_MEMBER

            
            self.is_verified = True

            # generate verification token
            self.generate_verification_token()

            # print(f"Created user: {username} <{email}> with the role {self.role}")

        except Exception as e:
            # log the error
            print(f"error creating user: {str(e)}")
            traceback.print_exc()
            # re-raise the exception
            raise ValueError(f"could not create user: {str(e)}")

    def _is_valid_password(self, password):
        """
        Check if a password like the  requirement.
        Returns:
            bool: 
        """
        try:
            if not password or len(password) < 8:
                return False

            
            if not re.search(r'\d', password):
                return False

            
            if not re.search(r'[A-Z]', password):
                return False

            return True
        
        except Exception as e:
            print(f"error validating password: {str(e)}")
            return False

    def set_password(self, password):
        """
        Set a new password for the user.
        Raises:
            ValueError: if the an  password does not  meet requirement
        """
        try:
            if not self._is_valid_password(password):
                raise ValueError("password must be at least 8 char and at lesat like  one number + upper case letter")

            salt = "CMT_salt_value"  
            self.password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        except Exception as e:
            print(f"error setting password: {str(e)}")
            raise

    def check_password(self, password):
        """
        check if the provided password is correct.
        Returns:
            bool: True if correct, False other
        """
        try:
            salt = "CMT_salt_value"  # must match the salt used in set_password method
            hashed = hashlib.sha256((password + salt).encode()).hexdigest()
            return hashed ==  self.password_hash
        except Exception  as e:
            print(f"error checking   password: {str(e)}")
            return False

    def generate_verification_token(self):
        """
        generate a new email verification token.

        Returns:
            str: The generated token
        """
        try:
            from models.UserManagement.auth_token import AuthToken

            token_value = AuthToken.generate_token(
                user_id=self.id,
                token_type=AuthToken.TOKEN_TYPE_VERIFY,
                expiry_hours=24
            )

            return  token_value
        except Exception as e:
            print(f"error  generating  verification token  : {str(e)}")
            traceback.print_exc()
            return None

    def verify_email(self, token_value):
        """
        verify the user email using a token.

        Returns:
            bool: True if  successful, False other
        """
        try:
            from models.UserManagement.auth_token import AuthToken

            token = AuthToken.validate_token(token_value, AuthToken.TOKEN_TYPE_VERIFY)

            if token and token.user_id == self.id:
                self.is_verified = True

                token.invalidate()
                db.session.add(token)

                return True
            return False
        except Exception as e:
            print(f"Error verifying email: {str(e)}")
            traceback.print_exc()
            return False

    def generate_password_reset_token(self):
        """
        generate a new password reset token.

        Returns:
            str: The generated token
        """
        try:
            from models.UserManagement.auth_token import AuthToken

            
            token_value =  AuthToken.generate_token(

                user_id= self.id,
                token_type = AuthToken.TOKEN_TYPE_RESET,
                expiry_hours=1  
            )

            return  token_value
        except Exception  as e:
            print(f"error generating password reset token: {str(e)}")
            traceback.print_exc()
            return  None

    def reset_password(self, token_value, new_password):
        """
        reset the user password using a token.
        returns:
            bool: True if reset are successful, False other
        """
        try:
            from models.UserManagement.auth_token import AuthToken

    
            token = AuthToken.validate_token(token_value,
                                              AuthToken.TOKEN_TYPE_RESET)

            if token and token.user_id == self.id:
                
                self.set_password(new_password)

                
                token.invalidate()
                db.session.add(token)

                return  True
            return  False
        except  Exception as e:
            print(f"error resetting  password: {str(e)}")
            traceback.print_exc()
            return  False

    def set_remember_me_token(self ):


        """
        generate and set a "remember  me" the  token.

        Returns:
            str: The generated token we have made
        """
        try:
            token = secrets.token_urlsafe(32)
            self.remember_me_token = token
            return token
        except Exception as e:
            print(f"error setting remember me   token: {str(e)}")
            return None

    def clear_remember_me_token(self ):


        """
        clear the "remember me" token.
        """
        try:
            self.remember_me_token =  None
        except Exception as e:
            print(f"error clearing  remember  me token: {str(e)}")

    def update_last_login(self ):
        """
        update the last login timestamp to now.
        """
        try:
            self.last_login = datetime.now(timezone.utc)
        except Exception as e:
            print(f"error updating  last  login: {str(e)}")

    def get_full_name(self  ):
        """
        get the user  full name.
        """
        try:
            if self.first_name and self.last_name:
                return f"{self.first_name} {self.last_name}"
            elif self.first_name:
                return self.first_name
            elif self.last_name:
                return self.last_name

            # No name fields 
            return self.username

        except Exception as e:
            # If not work, just return  the username
            print(f"error getting full name: {str(e)}")
            return self.username

    def has_permission(self, required_role):
        """
        check if the user has the right
          permission for a role  restricted action.

        """
        try:
            # admin has all the permissions
            if self.role  == self.ROLE_ADMIN:
                return  True

            # Role like : admin > supervisor > project_manager > team_member
            if required_role ==  self.ROLE_ADMIN:
                return self.role == self.ROLE_ADMIN

            if required_role ==  self.ROLE_SUPERVISOR:
                return self.role in [self.ROLE_ADMIN, self.ROLE_SUPERVISOR]

            if required_role ==  self.ROLE_PROJECT_MANAGER:
                return self.role in [self.ROLE_ADMIN, self.ROLE_SUPERVISOR, self.ROLE_PROJECT_MANAGER]

            # Team member role - everyone has at least this 
            return  True

        except Exception as e:
            print(f"error checking  permissions: {str(e)}")
            return False

    def can_manage_users(self):
        """
        check if the user can manage other users.
        """
        try:
            # Only admins can manage users
            return self.role in  [self.ROLE_ADMIN,
                                   self.ROLE_SUPERVISOR]


        except Exception as  e:
            print(f"error checking user  management permission: {str(e)}")
            return  False

    def can_assign_roles(self):
        """
        check if the user can assign the  roles to other user.

        """
        try:
            
            return self.role == self.ROLE_ADMIN
        except Exception as e:
            print(f"error checking role   assignment  permission: {str(e)}")
            return  False

    def to_dict(self):
        """
        convert user object to dictionary for API/JSON responses.
        returns:
            dict: 
        """
        try:
            return {
                'id': self.id,

                'username': self.username,

                'email' : self.email,
                'first_name' : self.first_name,
                'last_name':  self.last_name,
                'full_name' : self.get_full_name(),
                'role': self.role,
                'is_verified' : self.is_verified,
                'created_at':  self.created_at.isoformat() if self.created_at else None,
                'last_login':   self.last_login.isoformat() if self.last_login else None
            }
        except Exception as  e:
            print(f"error converting user to dict: {str(e)}")
            return {'error': 'Could not convert user to dictionary'}
