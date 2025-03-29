# Project Name

#### 💰📊 Expense Tracker – Take Control of Your Finances!

## 📌 Overview
This project is a **user management system** that allows users to **sign up, log in, update their profile, and log out** securely. It utilizes **FastAPI** for the backend and **Streamlit** for the frontend, ensuring a seamless and modern user experience.

## 🚀 Features
- User authentication (signup, login, logout)
- Profile management (update user details)
- Secure API with JWT authentication
- Streamlit-powered frontend for a smooth UI

## 🛠️ Technologies Used
- **Backend:** FastAPI, SQLAlchemy, Pydantic
- **Frontend:** Streamlit
- **Database:** PostgreSQL (or SQLite for development)
- **Authentication:** JWT Tokens

## 📂 Project Structure
```
📦 project-directory
 ┣ 📂 backend
 ┃ ┣ 📜 main.py          # FastAPI application
 ┃ ┣ 📜 models.py        # Database models
 ┃ ┣ 📜 routes.py        # API endpoints
 ┃ ┣ 📜 auth.py          # Authentication logic
 ┃ ┗ 📜 database.py      # Database connection
 ┣ 📂 frontend
 ┃ ┣ 📜 app.py           # Streamlit UI
 ┃ ┗ 📜 components.py    # UI Components
 ┣ 📜 README.md          # Project documentation
 ┣ 📜 requirements.txt   # Dependencies
 ┗ 📜 .env               # Environment variables
```

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Kingflow-23/Expense-Tracker.git
```

### Create a Virtual Environment
```bash
python -m venv .

source ./bin/activate  # On Linux/Mac
.\Scripts\activate  # On Windows 
``` 

### 2️⃣ Install Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3️⃣ Setup Environment Variables
Create a `.env` file and add the required configuration:
```env
DATABASE_URL=postgresql://user:password@localhost/db_name
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4️⃣ Run the Backend
```bash
uvicorn backend.main:app --reload
```

### 5️⃣ Run the Frontend
```bash
streamlit run frontend/app.py
```

## 🎬 Quick Demo
Below is a quick preview of the application in action:

### 🔹 Login Page

![image](https://github.com/user-attachments/assets/e8afb074-50f5-4dc5-975d-0583e44dc1dd)

### 🔹 Profile Update

![image](https://github.com/user-attachments/assets/c777d6f4-2f05-4ea3-b4af-81f0b65b51d6)

### 🔹 Logout
🚪➡️ Click the logout button to securely exit.

## 🔗 API Endpoints
| Method | Endpoint       | Description            |
|--------|--------------|------------------------|
| POST   | /auth/signup | Register a new user    |
| POST   | /auth/login  | Authenticate user      |
| PUT    | /auth/update | Update user profile    |
| GET    | /auth/logout | Logout user            |

## 📜 License
This project is licensed under the MIT License.

## 🙌 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.

---
*Made with ❤️ by [KingFlow-23](https://github.com/Kingflow-23)*

