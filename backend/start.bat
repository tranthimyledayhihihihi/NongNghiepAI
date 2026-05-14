@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
echo [AgriAI] Khoi dong backend tai http://127.0.0.1:5000 ...
venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 5000 --reload
