import os
import datetime

from typing import List
from pydantic import BaseModel
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.models.user import User
from app.models.expense import Expense
from app.database.db import SessionLocal
from app.auth.auth import SECRET_KEY, ALGORITHM, get_user_by_username

router = APIRouter(prefix="/expenses", tags=["expenses"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Pydantic schemas for expense requests/responses
class ExpenseCreate(BaseModel):
    amount: float
    category: str
    description: str = None


class ExpenseResponse(BaseModel):
    id: int
    amount: float
    category: str
    description: str = None
    date: str

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
            raise credentials_exception
        # Explicitly check token expiration
        if datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user


@router.post("/", response_model=ExpenseResponse)
def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_expense = Expense(
        amount=expense.amount,
        category=expense.category,
        description=expense.description,
        user_id=current_user.id,
        date=datetime.utcnow(),
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense


@router.get("/", response_model=List[ExpenseResponse])
def get_expenses(
    category: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Expense).filter(Expense.user_id == current_user.id)
    if category:
        query = query.filter(Expense.category == category)
    expenses = query.all()
    return expenses


@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = (
        db.query(Expense)
        .filter(Expense.id == expense_id, Expense.user_id == current_user.id)
        .first()
    )
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
    return {"message": "Expense deleted"}
