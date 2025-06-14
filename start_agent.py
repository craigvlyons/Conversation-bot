#!/usr/bin/env python3
"""
Universal cross-platform launcher for Conversation Bot.
This script detects the platform and sets up the environment appropriately.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def get_script_directory():
    """Get the directory where this script is located."""
    return Path(__file__).parent.absolute()


def setup_virtual_environment():
    """Set up and activate virtual environment."""
    script_dir = get_script_directory()
    venv_dir = script_dir / "venv"
    
    # Determine Python executable
    python_cmd = "python3" if platform.system() != "Windows" else "python"
    if not subprocess.run([python_cmd, "--version"], capture_output=True).returncode == 0:
        python_cmd = "python"
    
    print(f"Using Python command: {python_cmd}")
    
    # Create virtual environment if it doesn't exist
    if not venv_dir.exists():
        print("Virtual environment not found. Creating one...")
        result = subprocess.run([python_cmd, "-m", "venv", str(venv_dir)])
        if result.returncode != 0:
            print("Failed to create virtual environment.")
            return False
        print("Virtual environment created.")
    
    # Determine activation script and Python executable in venv
    if platform.system() == "Windows":
        venv_python = venv_dir / "Scripts" / "python.exe"
        pip_cmd = str(venv_dir / "Scripts" / "pip.exe")
    else:
        venv_python = venv_dir / "bin" / "python"
        pip_cmd = str(venv_dir / "bin" / "pip")
    
    return str(venv_python), pip_cmd


def install_requirements(pip_cmd):
    """Install requirements if needed."""
    script_dir = get_script_directory()
    requirements_file = script_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print("Warning: requirements.txt not found.")
        return True
    
    # Check if we need to install requirements
    # Simple check: if some key packages are missing
    try:
        import PyQt6
        import torch
        import pvporcupine
        print("Key packages already installed.")
        return True
    except ImportError:
        print("Installing requirements...")
        result = subprocess.run([pip_cmd, "install", "-r", str(requirements_file)])
        return result.returncode == 0


def check_environment_variables():
    """Check for required environment variables."""
    required_vars = {
        "GEMINI_KEY": "Gemini AI API key",
        "OPENAI_KEY": "OpenAI API key", 
        "PRORCUPINE_KEY": "Picovoice Porcupine key for wake word detection"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"  - {var}: {description}")
    
    if missing_vars:
        print("\nWarning: Missing environment variables:")
        print("\n".join(missing_vars))
        print("\nPlease set these in your .env file or system environment.")
        print("The application may not work properly without them.\n")
    
    return len(missing_vars) == 0


def check_platform_requirements():
    """Check platform-specific requirements."""
    system = platform.system()
    
    if system == "Windows":
        print("Platform: Windows")
        # Check for eSpeak NG
        espeak_lib = os.getenv("PHONEMIZER_ESPEAK_LIBRARY")
        espeak_path = os.getenv("PHONEMIZER_ESPEAK_PATH")
        
        if not espeak_lib or not espeak_path:
            print("Warning: eSpeak NG paths not configured.")
            print("Please install eSpeak NG and set environment variables:")
            print("  PHONEMIZER_ESPEAK_LIBRARY=C:\\Program Files\\eSpeak NG\\libespeak-ng.dll")
            print("  PHONEMIZER_ESPEAK_PATH=C:\\Program Files\\eSpeak NG\\espeak-ng.exe")
    
    elif system == "Darwin":
        print("Platform: macOS")
        # Check if espeak is available via Homebrew
        result = subprocess.run(["which", "espeak"], capture_output=True)
        if result.returncode != 0:
            print("Warning: espeak not found. Install with: brew install espeak")
    
    elif system == "Linux":
        print("Platform: Linux")
        # Check if espeak is available
        result = subprocess.run(["which", "espeak"], capture_output=True)
        if result.returncode != 0:
            print("Warning: espeak not found. Install with your package manager (e.g., sudo apt install espeak)")
    
    else:
        print(f"Platform: {system} (may not be fully supported)")


def run_application(python_cmd):
    """Run the main application."""
    script_dir = get_script_directory()
    main_script = script_dir / "main.py"
    
    if not main_script.exists():
        print("Error: main.py not found!")
        return False
    
    print("Launching Conversation Bot...")
    print("=" * 50)
    
    # Change to script directory
    os.chdir(script_dir)
    
    # Run the application
    try:
        result = subprocess.run([python_cmd, str(main_script)])
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
        return True
    except Exception as e:
        print(f"Error running application: {e}")
        return False


def main():
    """Main launcher function."""
    print("Conversation Bot Launcher")
    print("=" * 30)
    
    # Check platform requirements
    check_platform_requirements()
    print()
    
    # Set up virtual environment
    venv_result = setup_virtual_environment()
    if not venv_result:
        print("Failed to set up virtual environment.")
        input("Press Enter to exit...")
        return 1
    
    venv_python, pip_cmd = venv_result
    
    # Install requirements
    if not install_requirements(pip_cmd):
        print("Failed to install requirements.")
        input("Press Enter to exit...")
        return 1
    
    # Check environment variables
    check_environment_variables()
    
    # Run the application
    success = run_application(venv_python)
    
    if not success:
        print("\nApplication exited with an error.")
        input("Press Enter to exit...")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())