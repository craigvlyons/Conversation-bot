"""
Platform-aware configuration system for cross-platform compatibility.
Handles platform detection, path resolution, and platform-specific settings.
"""
import os
import platform
import shutil
from pathlib import Path
from typing import Dict, Optional, Union
import logging

logger = logging.getLogger(__name__)

class PlatformConfig:
    """Manages platform-specific configuration and paths."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.is_windows = self.system == "windows"
        self.is_macos = self.system == "darwin"
        self.is_linux = self.system == "linux"
        self.is_unix = self.is_macos or self.is_linux
        
        # Get project root directory
        self.project_root = self._get_project_root()
        
        # Set up base directories based on platform
        self.base_dir = self._get_base_directory()
        self.data_dir = self._get_data_directory()
        self.cache_dir = self._get_cache_directory()
        
        logger.info(f"Platform detected: {self.system}")
        logger.info(f"Project root: {self.project_root}")
        logger.info(f"Base directory: {self.base_dir}")
    
    def _get_project_root(self) -> Path:
        """Get the project root directory."""
        # Start from this file's directory and go up until we find main.py
        current = Path(__file__).parent
        while current.parent != current:
            if (current / "main.py").exists():
                return current
            current = current.parent
        
        # Fallback to current working directory
        return Path.cwd()
    
    def _get_base_directory(self) -> Path:
        """Get the base directory for the application."""
        # Try environment variable first
        if base_env := os.getenv("CONVO_BOT_BASE_DIR"):
            return Path(base_env)
        
        # Use project root as base directory
        return self.project_root
    
    def _get_data_directory(self) -> Path:
        """Get platform-appropriate data directory."""
        if self.is_windows:
            # Windows: Use APPDATA or project directory
            appdata = os.getenv("APPDATA")
            if appdata:
                return Path(appdata) / "ConversationBot"
            return self.base_dir / "data"
        
        elif self.is_macos:
            # macOS: Use Application Support or project directory
            home = Path.home()
            app_support = home / "Library" / "Application Support" / "ConversationBot"
            if home.exists():
                return app_support
            return self.base_dir / "data"
        
        else:
            # Linux: Use XDG_DATA_HOME or ~/.local/share
            xdg_data = os.getenv("XDG_DATA_HOME")
            if xdg_data:
                return Path(xdg_data) / "conversation-bot"
            return Path.home() / ".local" / "share" / "conversation-bot"
    
    def _get_cache_directory(self) -> Path:
        """Get platform-appropriate cache directory."""
        if self.is_windows:
            # Windows: Use TEMP or project temp
            temp = os.getenv("TEMP")
            if temp:
                return Path(temp) / "ConversationBot"
            return self.base_dir / "temp"
        
        elif self.is_macos:
            # macOS: Use ~/Library/Caches
            home = Path.home()
            cache = home / "Library" / "Caches" / "ConversationBot"
            if home.exists():
                return cache
            return self.base_dir / "temp"
        
        else:
            # Linux: Use XDG_CACHE_HOME or ~/.cache
            xdg_cache = os.getenv("XDG_CACHE_HOME")
            if xdg_cache:
                return Path(xdg_cache) / "conversation-bot"
            return Path.home() / ".cache" / "conversation-bot"
    
    def get_audio_output_path(self) -> Path:
        """Get the audio output file path."""
        audio_dir = self.base_dir / "recording" / "audio_out"
        audio_dir.mkdir(parents=True, exist_ok=True)
        return audio_dir / "output.wav"
    
    def get_kokoro_model_path(self) -> Path:
        """Get the Kokoro TTS model path."""
        return self.base_dir / "Kokoro" / "kokoro-v0_19.pth"
    
    def get_kokoro_voices_dir(self) -> Path:
        """Get the Kokoro voices directory."""
        voices_dir = self.base_dir / "Kokoro" / "voices"
        voices_dir.mkdir(parents=True, exist_ok=True)
        return voices_dir
    
    def get_kokoro_output_dir(self) -> Path:
        """Get the Kokoro audio output directory."""
        output_dir = self.base_dir / "Kokoro" / "audio_out"
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    def get_wake_word_model_paths(self) -> list:
        """Get platform-specific wake word model paths."""
        models = []
        wake_word_dir = self.base_dir / "speech" / "wake_word"
        
        # Platform-specific model files
        if self.is_windows:
            models.append(wake_word_dir / "jarvis" / "Jarvis_en_windows_v3_0_0.ppn")
        elif self.is_macos:
            models.append(wake_word_dir / "jarvis" / "Jarvis_en_mac_v3_0_0.ppn")
        elif self.is_linux:
            models.append(wake_word_dir / "jarvis" / "Jarvis_en_linux_v3_0_0.ppn")
        
        # Generic model as fallback
        generic_model = wake_word_dir / "wake_model" / "jarvis.ppn"
        if generic_model.exists():
            models.append(generic_model)
        
        # Filter to only existing models
        existing_models = [str(model) for model in models if model.exists()]
        
        if not existing_models:
            logger.warning(f"No wake word models found for platform: {self.system}")
            # Return the expected path anyway so the error is clear
            return [str(models[0]) if models else str(wake_word_dir / "jarvis.ppn")]
        
        return existing_models
    
    def get_command_executable(self, command: str) -> str:
        """Get platform-appropriate command executable."""
        if command == "npx":
            if self.is_windows:
                # Try to find npx.cmd first, fall back to npx
                npx_cmd = shutil.which("npx.cmd")
                if npx_cmd:
                    return "npx.cmd"
                npx = shutil.which("npx")
                if npx:
                    return "npx"
                return "npx.cmd"  # Default assumption
            else:
                # Unix systems use npx directly
                return "npx"
        
        return command
    
    def ensure_directory(self, path: Union[str, Path]) -> Path:
        """Ensure a directory exists, creating it if necessary."""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_venv_activation_script(self) -> str:
        """Get the virtual environment activation script path."""
        if self.is_windows:
            return str(self.base_dir / "venv" / "Scripts" / "activate.bat")
        else:
            return str(self.base_dir / "venv" / "bin" / "activate")
    
    def get_python_executable(self) -> str:
        """Get the appropriate Python executable name."""
        if self.is_windows:
            return "python"
        else:
            # Prefer python3 on Unix systems
            if shutil.which("python3"):
                return "python3"
            return "python"
    
    def get_temp_memory_dir(self) -> Path:
        """Get the temporary memory directory."""
        temp_dir = self.base_dir / "temp_memory"
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir

# Global instance
_platform_config: Optional[PlatformConfig] = None

def get_platform_config() -> PlatformConfig:
    """Get the global platform configuration instance."""
    global _platform_config
    if _platform_config is None:
        _platform_config = PlatformConfig()
    return _platform_config

# Convenience functions
def get_audio_output_path() -> str:
    """Get the audio output file path as string."""
    return str(get_platform_config().get_audio_output_path())

def get_kokoro_model_path() -> str:
    """Get the Kokoro model path as string."""
    return str(get_platform_config().get_kokoro_model_path())

def get_kokoro_voices_dir() -> str:
    """Get the Kokoro voices directory as string."""
    return str(get_platform_config().get_kokoro_voices_dir())

def get_kokoro_output_dir() -> str:
    """Get the Kokoro output directory as string."""
    return str(get_platform_config().get_kokoro_output_dir())

def get_wake_word_model_paths() -> list:
    """Get wake word model paths."""
    return get_platform_config().get_wake_word_model_paths()

def is_windows() -> bool:
    """Check if running on Windows."""
    return get_platform_config().is_windows

def is_macos() -> bool:
    """Check if running on macOS."""
    return get_platform_config().is_macos

def is_linux() -> bool:
    """Check if running on Linux."""
    return get_platform_config().is_linux