from datetime import datetime, timezone, timedelta
import secrets
import traceback
from models.database import db

class AuthToken(db.Model):
    """
    so this isAuthToken class for managing the authentication tokens.
    
    this class do this :
    - email  verification tokens

    - password reset  tokens
    - remember  me  tokens
    
    """
    __tablename__ = 'auth_tokens'  #this  DB table name
    
    # token type constants
    TOKEN_TYPE_VERIFY  = 'verify'

    TOKEN_TYPE_RESET  = 'reset'
    
    # valid token types list
    VALID_TOKEN_TYPES = [ TOKEN_TYPE_VERIFY ,
                
                          TOKEN_TYPE_RESET]
    
    # attributes
    id = db.Column(db.Integer,
                     primary_key=True) 
    user_id = db.Column(db.Integer,
                         db.ForeignKey('users.id'),
                             nullable=False)  
    token_value = db.Column(db.String(100) ,
                               unique=True,
                               nullable=False)  
    token_type =  db.Column(db.String(20),
                            nullable=False) 
    expiry_timestamp =  db.Column(db.DateTime ,
                                  nullable=False)  
    created_at = db.Column(db.DateTime, 
                           default=lambda:  datetime.now(timezone.utc))  
    
    # relationship  for  User model
    user = db.relationship( 'User', 
                           backref= 'auth_tokens')
    
    def __init__( self, user_id ,
                  token_type  , 
                  expiry_hours=24):
        """
        initialize an    AuthToken object

        """
        try:
            # validate input
            if not  user_id:
                raise ValueError( "user id are required")
                
            if not token_type or token_type not in self.VALID_TOKEN_TYPES:
                raise ValueError(f"token type must be one of  :  {', '.join(self.VALID_TOKEN_TYPES)}")
            
            # set the attributes
            self.user_id =   user_id

            # set  the  token type
            self.token_type =   token_type
            
            # generate an secure random token
            self.token_value =   secrets.token_urlsafe(32)
            
            # set the  expiry time
            self.expiry_timestamp = datetime.now(timezone.utc) + timedelta(hours=expiry_hours)
            
        except Exception as e:
            print(f"error creating auth token: {str(e)}")
            traceback.print_exc()
            raise
    
    def is_valid(self):
        """
        check if the token is still valid 
        
        returns:bool
            
        """
        try:
            # check if token has expired
            return datetime.now(timezone.utc) < self.expiry_timestamp
        except Exception as e:
            print(f"error checking token validity: {str(e)}")
            return False
    
    def invalidate(self):
        """
        invalidate the token by setting its expiry to the past.
        
        """
        try:
            self.expiry_timestamp = datetime.now(timezone.utc) - timedelta(seconds=1)
        except Exception as e:
            print(f"error invalidating token: {str(e)}")
    
    @classmethod
    def generate_token(cls, user_id, token_type, expiry_hours=24):
        """
        generate a new token for the  user.
            
        returns:
            str The generated token value
        """
        try:
            # create a new token
            token = cls(user_id,
                         token_type,
                           expiry_hours)
            
            # add the  database
            db.session.add(token)

            db.session.commit()
            return token.token_value
        except Exception as e:
            print(f"error generating token: {str(e)}")
            db.session.rollback()
            return None
    
    @classmethod
    def validate_token(cls, token_value, token_type):
        """
        Validate a token.
          
        returns:
            AuthToken
        """
        try:
            # find the token
            token = cls.query.filter_by(token_value=token_value,
                                         token_type=token_type).first()
            
            # check if token are exists and is an valid
            if token and token.is_valid():
                return token
            
            return None
        except Exception as e:
            print(f"error validating token: {str(e)}")
            return None
