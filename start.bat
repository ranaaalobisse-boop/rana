@echo off
echo =========================================
echo   LUXURY JEWELRY API - START SERVER
echo =========================================
echo.

cd backend

echo Starting server...
echo API will be available at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py
pause
