"""User model and authentication functionality."""
from dataclasses import dataclass
from typing import Dict, Optional, ClassVar, List
import uuid
import hashlib
import os

@dataclass
class User:
    """Representation of a user in the system."""
    id: str
    username: str
    email: str
    password_hash: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    # In-memory storage for development (would use a database in production)
    _users: ClassVar[Dict[str, 'User']] = {}
    
    @classmethod
    def create(cls, username: str, email: str, password: str, first_name: Optional[str] = None, last_name: Optional[str] = None) -> 'User':
        """Create a new user."""
        # Check if username or email already exists
        for user in cls._users.values():
            if user.username == username:
                raise ValueError("Username already exists")
            if user.email == email:
                raise ValueError("Email already exists")
        
        # Create user ID
        user_id = str(uuid.uuid4())
        
        # Hash password
        password_hash = cls._hash_password(password)
        
        # Create user
        user = cls(
            id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name
        )
        
        # Store user
        cls._users[user_id] = user
        
        return user
    
    @classmethod
    def get_by_id(cls, user_id: str) -> Optional['User']:
        """Get a user by ID."""
        return cls._users.get(user_id)
    
    @classmethod
    def get_by_username(cls, username: str) -> Optional['User']:
        """Get a user by username."""
        for user in cls._users.values():
            if user.username == username:
                return user
        return None
    
    @classmethod
    def get_by_email(cls, email: str) -> Optional['User']:
        """Get a user by email."""
        for user in cls._users.values():
            if user.email == email:
                return user
        return None
    
    @classmethod
    def authenticate(cls, username: str, password: str) -> Optional['User']:
        """Authenticate a user."""
        user = cls.get_by_username(username)
        if not user:
            return None
        
        # Check password
        if cls._verify_password(password, user.password_hash):
            return user
        
        return None
    
    @classmethod
    def list_all(cls) -> List['User']:
        """Get all users."""
        return list(cls._users.values())
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash a password."""
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )
        return salt.hex() + ':' + key.hex()
    
    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against a hash."""
        salt_hex, key_hex = password_hash.split(':')
        salt = bytes.fromhex(salt_hex)
        key = bytes.fromhex(key_hex)
        
        new_key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )
        
        return key == new_key

# Create a couple of test users
User.create("admin", "admin@example.com", "admin123", "Admin", "User")
User.create("user", "user@example.com", "user123", "Test", "User")