from sqlalchemy import Column, Integer, String
from werkzeug.security import generate_password_hash, check_password_hash
from blueprints.models.base_model import Base

class User(Base):
    """
    User class handles application users.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(128), nullable=False, unique=True)
    password = Column(String(128), nullable=False)
    username = Column(String(128), nullable=True)

    def __init__(self, email, password, username):
        """
        Initializes a user object.
        """
        self.email = email
        self.set_password(password)
        self.username = username

    def set_password(self, password):
        """
        Sets the password hash for the user.
        """
        self.password = generate_password_hash(password)  # Store the hash in the password column

    def check_password(self, password):
        """
        Checks if the provided password matches the stored hash.
        """
        return check_password_hash(self.password, password)

    def __repr__(self):
        """
        Returns a string representation of the user object.
        """
        return f'<User(id={self.id}, email={self.email}, username={self.username})>'
