from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import hashlib

db = SQLAlchemy()
class User(db.Model,UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    last_seen = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    bio = db.Column(db.String(), nullable=True)  # Add for the bio column, will consider later


    @staticmethod
    def get(user_id):
        return db.session.get(User, int(user_id))
    def set_password(self, password):
        """Method to create a hashed password"""
        self.password = generate_password_hash(password)
    def check_password(self, password):
        """Method to check the hashed password"""
        return check_password_hash(self.password, password)
    
    def gravatar_url(self, size=100, default='retro', rating='g'):
        """Generate a gravatar URL based on the user's email."""
        hash = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        url = f"https://www.gravatar.com/avatar/{hash}?s={size}&d={default}&r={rating}"
        return url
    
def create_bd():
    db.create_all()