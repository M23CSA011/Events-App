# Event management Web App

## Tech Stack

- **Backend:** FastAPI
- **Database:** PostgreSQL
- **Frontend:** NiceGUI
- **Authentication:** JWT

## Features

- User and Admin Signup/Login
- Event Creation, Updating, and Deletion for Admins
- Event Registration and Unregistration for Users
- Viewing Registered Events

## Prerequisites

Ensure you have the following installed on your computer:

- Git
- Python
- VS Code
- PostgreSQL

## Setup Instructions

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/M23CSA011/Events-App.git
   ```

2. **Create a `.env` File:**
   Create a `.env` file in the root directory of the project with the following information:

   ```env
   DATABASE_HOSTNAME=
   DATABASE_PORT= 
   DATABASE_PASSWORD= 
   DATABASE_NAME=
   DATABASE_USERNAME= 
   SECRET_KEY= 
   ALGORITHM=
   ACCESS_TOKEN_EXPIRE_MINUTES=
   ```

3. **Install Dependencies:**
   Navigate to the project directory and run:
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup:**
   Once connected to the database, run the following commands to create the necessary tables:
   ```bash
   alembic revision --autogenerate -m "Create Tables"
   alembic upgrade head
   ```

5. **Running the Application:**
   Open two terminals:

   - **Terminal 1:** To run the backend:
     ```bash
     uvicorn app.main:app --reload
     ```

   - **Terminal 2:** To run the frontend:
     ```bash
     python app\NiceGui\all.py
     ```

The application will start running on your localhost.

## Demo Video

Check out the demo video showcasing the main features of the app:[ [video]](https://drive.google.com/file/d/1EjxmUkbPkgHNOMwHWQAftekcT9_xVQgp/view?usp=sharing)

## Feedback and Contributions

Your feedback is valuable! Please feel free to open issues or pull requests if you have suggestions or improvements.
