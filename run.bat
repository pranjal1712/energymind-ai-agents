@echo off
echo Starting EnergyResearch AI...

start cmd /k "venv\Scripts\python -m uvicorn backend.main:app --reload"
timeout /t 3
start cmd /k "venv\Scripts\streamlit run frontend/app.py"

echo Application started!
echo Backend: http://localhost:8000/docs
echo Frontend: http://localhost:8501
