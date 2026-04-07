@echo off
cd /d "%~dp0"
echo Importando backup a Supabase (usa .env)...
".venv\Scripts\python.exe" scripts\import_to_supabase.py
echo.
pause
