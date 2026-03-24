@echo off
REM PrepEdge AI - Windows Setup Script

echo.
echo PrepEdge AI - Setup Script
echo ==============================
echo.

REM Setup Backend
echo Setting up Backend...
cd backend

REM Check Python
python --version >nul 2>&1 || (
    echo Python not found. Please install Python 3.10+
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt -q

REM Create .env file
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo [OK] Created .env file - Please update with your credentials
) else (
    echo .env file already exists
)

echo [OK] Backend setup complete
echo.

REM Setup Frontend
echo Setting up Frontend...
cd ..\frontend

REM Install npm dependencies
echo Installing Node dependencies...
call npm install -q

REM Create .env.local file
if not exist .env.local (
    echo Creating .env.local file...
    (
        echo NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
    ) > .env.local
    echo [OK] Created .env.local file
) else (
    echo .env.local file already exists
)

echo [OK] Frontend setup complete
echo.

REM Summary
echo ==============================
echo [OK] Setup Complete!
echo ==============================
echo.
echo Next steps:
echo.
echo 1. Backend:
echo    cd backend
echo    venv\Scripts\activate
echo    python main.py
echo.
echo 2. Frontend (in another terminal):
echo    cd frontend
echo    npm run dev
echo.
echo 3. Open http://localhost:3000 in your browser
echo.
