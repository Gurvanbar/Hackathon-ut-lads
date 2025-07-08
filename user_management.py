import json
import os
import tkinter as tk
from tkinter import messagebox
from config_settings import USER_DATA_FILE, REGISTRATION_WINDOW_SIZE

def load_user_data(app):
    """Load user data from file"""
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    else:
        create_registration_window(app)
    return None

def save_user_data(name, function):
    """Save user data to file"""
    data = {
        "name": name,
        "function": function
    }
    with open(USER_DATA_FILE, "w") as file:
        json.dump(data, file)

def submit_form(name_entry, function_entry, root, app):
    """Handle form submission for user registration"""
    name = name_entry.get().strip()
    function = function_entry.get().strip()
    
    if name and function:
        save_user_data(name, function)
        messagebox.showinfo("Welcome", f"Thanks {name}! You're registered as a {function}.")
        root.destroy()
        app.user = load_user_data()
        app._create_main_window()
    else:
        messagebox.showwarning("Input Error", "Please fill in both fields.")

def create_registration_window(app):
    """Create the user registration window"""
    root = tk.Tk()
    root.title("User Registration")
    root.geometry(REGISTRATION_WINDOW_SIZE)
    root.protocol("WM_DELETE_WINDOW", app.minimize_to_tray)

    tk.Label(root, text="Your Name:").pack(pady=(20, 5))
    name_entry = tk.Entry(root)
    name_entry.pack()

    tk.Label(root, text="Your Function:").pack(pady=(10, 5))
    function_entry = tk.Entry(root)
    function_entry.pack()

    submit_btn = tk.Button(root, text="Submit", 
                          command=lambda: submit_form(name_entry, function_entry, root, app))
    submit_btn.pack(pady=20)

    app.main_window = root
    root.mainloop()
