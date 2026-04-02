@echo off
echo Starting Night Vision Surveillance Backend...
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run the backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
