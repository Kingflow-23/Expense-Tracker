from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.db import Base

class User(Base):
    """
    The User model represents a user in the database. It stores information such as the user's
    unique identifier, username, email, and hashed password. The User model also has a one-to-many
    relationship with the Expense model, meaning a user can have multiple expenses associated with them.

    Attributes:
    - id (int): The unique identifier for each user.
    - username (str): A unique string representing the user's chosen name.
    - email (str): A unique string representing the user's email address.
    - hashed_password (str): The hashed version of the user's password.
    - expenses (list of Expense): A list of Expense objects associated with this user. This relationship
      is established through the `expenses` relationship, defined in the Expense model.

    Relationships:
    - expenses (Expense): A one-to-many relationship, allowing access to all expenses created by this user.
    """
    
    # The table name in the database
    __tablename__ = "users"

    # The unique identifier for each user, automatically incremented
    id = Column(Integer, primary_key=True, index=True)

    # The unique username for the user. It must be unique and cannot be null.
    username = Column(String, unique=True, index=True, nullable=False)

    # The unique email for the user. It must be unique and cannot be null.
    email = Column(String, unique=True, index=True, nullable=False)

    # The hashed password of the user. This field is required for authentication.
    hashed_password = Column(String, nullable=False)

    # A one-to-many relationship with the Expense model. 
    # This allows us to access all expenses related to this user.
    expenses = relationship("Expense", back_populates="user")

    def __repr__(self):
        """
        A string representation of the User instance, useful for debugging and logging.
        This will display the essential details of the user (id, username, and email).
        """
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
