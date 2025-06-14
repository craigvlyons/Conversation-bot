@echo off
echo Starting Conversation Bot...

REM Get the directory where this batch file is located
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv" (
    echo Virtual environment not found. Creating one...
    python -m .venv venv
    echo Virtual environment created.
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if requirements need to be installed (simple check)
python -c "import PyQt6, torch, pvporcupine" 2>nul
if errorlevel 1 (
    echo Installing requirements...
    pip install -r requirements.txt
)

REM Check for environment variables
if "%GEMINI_KEY%"=="" if "%OPENAI_KEY%"=="" (
    echo Warning: No AI API keys found in environment variables.
    echo Please set GEMINI_KEY and/or OPENAI_KEY in your .env file or environment.
)

if "%PRORCUPINE_KEY%"=="" (
    echo Warning: PRORCUPINE_KEY not found. Wake word detection may not work.
)

REM Check for eSpeak NG
if "%PHONEMIZER_ESPEAK_LIBRARY%"=="" (
    echo Warning: eSpeak NG not configured. Please set environment variables:
    echo   PHONEMIZER_ESPEAK_LIBRARY=C:\Program Files\eSpeak NG\libespeak-ng.dll
    echo   PHONEMIZER_ESPEAK_PATH=C:\Program Files\eSpeak NG\espeak-ng.exe
)

REM Run the application
echo Launching Conversation Bot...
echo ==================================================
python main.py

pause
