#!/usr/bin/env python3
"""
AI Mail Assistant - Main Application Entry Point

A desktop application for anwering emails at ultra speed.
"""

import threading
from system_tray import app
from user_management import load_user_data, create_registration_window
from utils import setup_application

def main():
    """Main application entry point"""
    # Setup application environment
    setup_application()
    
    # Load user data on startup
    app.user = load_user_data(app)
    
    # Load user preferences if user exists
    if app.user:
        app.load_user_preferences()
    
    # Start the system tray icon in a separate thread
    tray_thread = threading.Thread(target=app.run_tray, daemon=True)
    tray_thread.start()
    
    # Show the main window or registration window initially
    if app.user is None:
        create_registration_window(app)
    else:
        app.show_main_window()

if __name__ == "__main__":
    main()
