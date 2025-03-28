from fastapi import FastAPI

from app.routes import auth, expense
from app.database.db import engine, Base

# Create all tables in the database (if they don’t exist)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Tracker API")

# Include the authentication and expense routers
app.include_router(auth.router)
app.include_router(expense.router)


@app.get("/")
def root():
    return {"message": "Welcome to the Expense Tracker API"}
