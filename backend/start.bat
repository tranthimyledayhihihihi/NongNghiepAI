@echo off
setlocal

REM Backend startup script (FastAPI/Uvicorn)
REM Assumes current working directory is repo root (e:/CDNNLT/CuoiKy/NongNghiepAI)

REM Use utf-8 to avoid Vietnamese encoding issues in console
chcp 65001 >nul

REM Ensure we can import "app" package from backend/app
set "PYTHONPATH=%~dp0"

REM Load environment variables from backend/.env if present
if exist "%~dp0\.env" (
  set "ENV_FILE=%~dp0\.env"
) else (
  set "ENV_FILE="
)

REM Start server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info

endlocal
