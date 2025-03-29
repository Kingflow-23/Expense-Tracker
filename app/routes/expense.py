import logging

from sqlalchemy import func
from pydantic import BaseModel
from jose import JWTError, jwt
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends, HTTPException

from app.models.user import User
from app.models.expense import Expense
from app.database.db import SessionLocal
from app.auth.auth import SECRET_KEY, ALGORITHM, get_user_by_username

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

router = APIRouter(prefix="/expenses", tags=["expenses"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Pydantic schemas for expense requests/responses
class ExpenseCreate(BaseModel):
    amount: float
    category: str
    description: Optional[str] = None


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: int
    amount: float
    category: str
    description: str = None
    date: str  # Expecting a string

    @classmethod
    def from_orm(cls, expense):
        return cls(
            id=expense.id,
            amount=expense.amount,
            category=expense.category,
            description=expense.description,
            date=expense.date.isoformat(),  # Convert datetime to string
        )

    class Config:
        orm_mode = True


# Dependency: get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency: get the current user from the token
def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        exp = payload.get("exp")
        if username is None or exp is None:
            logging.warning("Token payload missing 'sub' or 'exp'.")
            raise credentials_exception
        # Explicitly check token expiration
        if datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            logging.warning("Token for user '%s' has expired.", username)
            raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError as e:
        logging.error("JWT decoding error: %s", e)
        raise credentials_exception
    user = get_user_by_username(db, username)
    if user is None:
        logging.warning("User '%s' not found in database.", username)
        raise credentials_exception
    logging.info("User '%s' authenticated successfully.", username)
    return user


@router.post("/", response_model=ExpenseResponse)
def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logging.info("User '%s' is creating an expense.", current_user.username)
    new_expense = Expense(
        amount=expense.amount,
        category=expense.category,
        description=expense.description,
        user_id=current_user.id,
        date=datetime.now(timezone.utc),
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    logging.info(
        "Expense created with ID %s for user '%s'.",
        new_expense.id,
        current_user.username,
    )
    return ExpenseResponse.from_orm(new_expense)


@router.get("/", response_model=List[ExpenseResponse])
def get_expenses(
    category: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logging.info("User '%s' is retrieving expenses.", current_user.username)
    query = db.query(Expense).filter(Expense.user_id == current_user.id)
    if category:
        logging.info("Filtering expenses by category: %s", category)
        query = query.filter(func.lower(Expense.category) == category.lower())
    expenses = query.all()
    logging.info(
        "Retrieved %d expense(s) for user '%s'.", len(expenses), current_user.username
    )
    return [ExpenseResponse.from_orm(expense) for expense in expenses]


@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logging.info(
        "User '%s' is attempting to delete expense ID %s.",
        current_user.username,
        expense_id,
    )
    expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id, Expense.user_id == current_user.id)
        .first()
    )
    if not expense:
        logging.warning(
            "Expense ID %s not found for user '%s'.", expense_id, current_user.username
        )
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
    logging.info(
        "Expense ID %s deleted for user '%s'.", expense_id, current_user.username
    )
    return {"message": "Expense deleted"}


@router.patch("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    expense_update: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logging.info(
        "User '%s' is attempting to update expense ID %s.",
        current_user.username,
        expense_id,
    )

    expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id, Expense.user_id == current_user.id)
        .first()
    )
    if not expense:
        logging.warning(
            "Expense ID %s not found for user '%s'.", expense_id, current_user.username
        )
        raise HTTPException(status_code=404, detail="Expense not found")

    # Update only the fields provided in the request
    if expense_update.amount is not None:
        expense.amount = expense_update.amount
    if expense_update.category is not None:
        expense.category = expense_update.category
    if expense_update.description is not None:
        expense.description = expense_update.description

    db.commit()
    db.refresh(expense)

    logging.info(
        "Expense ID %s updated for user '%s'.", expense_id, current_user.username
    )
    return ExpenseResponse.from_orm(expense)
