"""
Configuration settings for the Mail Assistant application
"""

import os

# File paths
USER_DATA_FILE = "user_data.json"
DIRECTORY_FILE = "directory.json"
CONFIG_FILE = "config.json"
ICON_FILE = "app_icon.ico"

# UI Settings
OVERLAY_SIZE = 40
OVERLAY_OFFSET = 30
OVERLAY_ALPHA = 0.7
OVERLAY_COLOR = "#28a745"  # Green color

# Window sizes
MAIN_WINDOW_SIZE = "300x200"
REGISTRATION_WINDOW_SIZE = "300x200"
DIRECTORY_WINDOW_SIZE = "400x400"
PROMPT_WINDOW_SIZE = "400x200"
ADD_PERSON_WINDOW_SIZE = "300x250"

# Application info
APP_NAME = "Mail Assistant"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Desktop application with system tray integration for managing mail generation and directory contacts"

# Keyboard shortcuts
MAIN_HOTKEY = 'ctrl+space'

# Clipboard mode settings
DEFAULT_CLIPBOARD_MODE = False  # False = manual UI, True = auto clipboard

# System tray icon settings
TRAY_ICON_SIZE = (64, 64)
TRAY_ICON_FALLBACK_SIZE = (32, 32)

def get_absolute_path(filename):
    """Get absolute path for a file in the application directory"""
    return os.path.abspath(filename)

def file_exists(filename):
    """Check if a file exists in the application directory"""
    return os.path.exists(get_absolute_path(filename))
