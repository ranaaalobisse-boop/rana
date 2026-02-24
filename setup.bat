@echo off
echo =========================================
echo   LUXURY JEWELRY API - AUTO SETUP
echo =========================================
echo.

:: Step 1: Check Python
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found! Please install Python 3.9+ from python.org
    pause
    exit /b
)
echo Python found!
echo.

:: Step 2: Install Dependencies
echo [2/4] Installing dependencies...
cd backend
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies
    pause
    exit /b
)
echo Dependencies installed!
echo.

:: Step 3: Run Seeder
echo [3/4] Running database seeder...
echo yes | python seeder.py
if %errorlevel% neq 0 (
    echo Seeder failed
    pause
    exit /b
)
echo Database created!
echo.

:: Step 4: Start Server
echo [4/4] Starting server...
echo API will be available at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.
python main.py
pause
