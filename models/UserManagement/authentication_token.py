from datetime import datetime, timezone, timedelta
import secrets
import traceback
from models.database import db

class AuthToken(db.Model):
   
    __tablename__ = 'auth_tokens'  # DB table name
    
    # Token type constants
    TOKEN_TYPE_VERIFY = 'verify'
    TOKEN_TYPE_RESET = 'reset'
    
    # Valid token types list 
    VALID_TOKEN_TYPES = [TOKEN_TYPE_VERIFY, TOKEN_TYPE_RESET]
    
    # Basic token attributes
    id = db.Column(db.Integer, primary_key=True)  # primary key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # user this token belongs to
    token_value = db.Column(db.String(100), unique=True, nullable=False)  # the actual token
    token_type = db.Column(db.String(20), nullable=False)  # type of token (verify, reset)
    expiry_timestamp = db.Column(db.DateTime, nullable=False)  # when the token expires
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # when token was created
    
    # Relationship to User model
    user = db.relationship('User', backref='auth_tokens')
    
    def __init__(self, user_id, token_type, expiry_hours=24):
        
        try:
            # Validate inputs
            if not user_id:
                raise ValueError("User ID is required")
                
            if not token_type or token_type not in self.VALID_TOKEN_TYPES:
                raise ValueError(f"Token type must be one of: {', '.join(self.VALID_TOKEN_TYPES)}")
            
            # Set the attributes
            self.user_id = user_id
            self.token_type = token_type
            
            # Generate a secure random token
            self.token_value = secrets.token_urlsafe(32)
            
            # Set expiry time
            self.expiry_timestamp = datetime.now(timezone.utc) + timedelta(hours=expiry_hours)
            
        except Exception as e:
            print(f"Error creating auth token: {str(e)}")
            traceback.print_exc()
            raise
    
    def is_valid(self):
       
        try:
            # Check if token has expired
            return datetime.now(timezone.utc) < self.expiry_timestamp
        except Exception as e:
            print(f"Error checking token validity: {str(e)}")
            return False
    
    def invalidate(self):
        
        try:
            self.expiry_timestamp = datetime.now(timezone.utc) - timedelta(seconds=1)
        except Exception as e:
            print(f"Error invalidating token: {str(e)}")
    
    @classmethod
    def generate_token(cls, user_id, token_type, expiry_hours=24):
        
        try:
            # Create a new token
            token = cls(user_id, token_type, expiry_hours)
            
            # Add to database
            db.session.add(token)
            db.session.commit()
            
            return token.token_value
        except Exception as e:
            print(f"Error generating token: {str(e)}")
            db.session.rollback()
            return None
    
    @classmethod
    def validate_token(cls, token_value, token_type):
        
        try:
            # Find the token
            token = cls.query.filter_by(token_value=token_value, token_type=token_type).first()
            
            # Check if token exists and is valid
            if token and token.is_valid():
                return token
            
            return None
        except Exception as e:
            print(f"Error validating token: {str(e)}")
            return None
