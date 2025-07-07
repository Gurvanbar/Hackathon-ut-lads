"""
Utility functions for the Mail Assistant application
"""

import os
import sys
from PIL import Image, ImageDraw
from config_settings import ICON_FILE, TRAY_ICON_SIZE, OVERLAY_COLOR

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def ensure_data_files():
    """Ensure all required data files exist"""
    files_to_check = [
        'directory.json',
        'config.json'
    ]
    
    for file_name in files_to_check:
        if not os.path.exists(file_name):
            if file_name == 'directory.json':
                # Create empty directory file
                import json
                with open(file_name, 'w') as f:
                    json.dump([], f)
            elif file_name == 'config.json':
                # Create default config file
                import json
                default_config = {
                    "theme": "default",
                    "auto_start": False,
                    "notifications": True
                }
                with open(file_name, 'w') as f:
                    json.dump(default_config, f, indent=2)

def setup_application():
    """Setup application environment"""
    ensure_data_files()
