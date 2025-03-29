from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.db import Base


class User(Base):
    """
    The User model represents a registered user in the system. It stores personal details, authentication
    credentials, and optional profile information.

    Attributes:
    ----------
    - id (int): Unique identifier for each user.
    - username (str): A unique name chosen by the user for identification.
    - email (str): A unique email address associated with the user.
    - hashed_password (str): Securely stored password (hashed).
    - phone_number (str, optional): Contact number of the user.
    - address (str, optional): User's residential address.
    - favorite_sport (str, optional): The user's favorite sport.
    - favorite_animal (str, optional): The user's favorite animal.
    - relationship_status (str, optional): User's relationship status.
    - occupation (str, optional): The user's profession or job title.
    - bio (str, optional): A short personal bio or description.
    - profile_picture_url (str, optional): URL of the user's profile picture.
    - expenses (list of Expense): A collection of expenses associated with the user.

    Relationships:
    -------------
    - expenses (Expense): One-to-many relationship, allowing the user to track their expenses.

    Methods:
    -------
    - __repr__(): Returns a string representation of the user object for debugging/logging.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Optional user details
    phone_number = Column(String, nullable=True)
    address = Column(String, nullable=True)
    favorite_sport = Column(String, nullable=True)
    favorite_animal = Column(String, nullable=True)
    relationship_status = Column(String, nullable=True)
    occupation = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    profile_picture_url = Column(String, nullable=True)

    # Relationship with expenses
    expenses = relationship("Expense", back_populates="user")

    def __repr__(self):
        """Returns a string representation of the User instance, useful for debugging and logging."""
        return (
            f"<User(id={self.id}, username={self.username}, email={self.email}, "
            f"phone={self.phone_number}, address={self.address}, favorite_sport={self.favorite_sport}, "
            f"occupation={self.occupation})>"
        )
