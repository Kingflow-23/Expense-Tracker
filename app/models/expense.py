from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.db import Base


class Expense(Base):
    """
    The Expense model represents an expense record in the database.
    This model is used to store information related to the expenses incurred by a user.
    Each expense is associated with a specific user, and each expense has details like
    the amount, category, description, and date it was created.

    Attributes:
    - id (int): The unique identifier for the expense.
    - user_id (int): Foreign key that links the expense to the user who created it.
    - amount (float): The amount of money spent in this expense.
    - category (str): The category of the expense (e.g., "Food", "Business", "Entertainment").
    - description (str): An optional text field to provide more details about the expense.
    - date (datetime): The timestamp indicating when the expense was created, defaulting to the current time in UTC.

    Relationships:
    - user (User): A relationship field that connects this expense record to the user who created it.
    """

    # The table name in the database
    __tablename__ = "expenses"

    # The unique identifier for each expense, automatically incremented
    id = Column(Integer, primary_key=True, index=True)

    # The ID of the user associated with this expense (foreign key)
    user_id = Column(Integer, ForeignKey("users.id"))

    # The amount of money spent in this expense
    amount = Column(Float, nullable=False)

    # The category of the expense (e.g., Food, Business, etc.)
    category = Column(String, nullable=False)

    # An optional description of the expense
    description = Column(String, nullable=True)

    # The date when the expense was created, defaulting to the current time in UTC
    date = Column(DateTime, default=datetime.now(timezone.utc))

    # Establishing a relationship with the User model.
    # This allows easy access to the user who created the expense.
    user = relationship("User", back_populates="expenses")

    def __repr__(self):
        """
        A string representation of the Expense instance, used for logging and debugging.
        This will display the essential details of the expense.
        """
        return f"<Expense(id={self.id}, amount={self.amount}, category={self.category}, description={self.description}, date={self.date})>"
