import json
import os
import tkinter as tk
from tkinter import messagebox

import Levenshtein
from config_settings import USER_DATA_FILE, REGISTRATION_WINDOW_SIZE
from directory import add_person

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


def resolve_unknown_name(name, directory):
    win = tk.Toplevel()
    win.title(f"Resolve: {name}")
    win.geometry("400x300")
    win.attributes("-topmost", True)

    result = {"choice": None}

    tk.Label(win, text=f"'{name}' not found. Choose or create:", font=("Arial", 12)).pack(pady=10)

    def use_new():
        win.destroy()
        show_create_form(name)
        result["choice"] = name

    def use_existing(selected_name):
        win.destroy()
        result["choice"] = selected_name

    tk.Button(win, text=f"+ Add '{name}' to directory", command=use_new).pack(pady=5)

    # Levenshtein sorting
    matches = sorted(
        directory,
        key=lambda person: Levenshtein.distance(name.lower(), person["name"].lower())
    )[:5]

    tk.Label(win, text="Closest matches:", font=("Arial", 10)).pack(pady=5)
    for match in matches:
        display = f"{match['name']} – {match['position']}"
        tk.Button(win, text=display, command=lambda m=match['name']: use_existing(m)).pack(fill="x", padx=10, pady=2)

    win.wait_window()
    return result["choice"]

def show_create_form(default_name):
    form = tk.Toplevel()
    form.title("Add Person")
    form.geometry("300x250")
    form.attributes("-topmost", True)

    name_var = tk.StringVar(value=default_name)
    pos_var = tk.StringVar()
    desc_var = tk.StringVar()

    tk.Label(form, text="Name:").pack()
    tk.Entry(form, textvariable=name_var).pack()

    tk.Label(form, text="Position:").pack()
    tk.Entry(form, textvariable=pos_var).pack()

    tk.Label(form, text="Description:").pack()
    tk.Entry(form, textvariable=desc_var).pack()

    def submit():
        add_person(name_var.get(), pos_var.get(), desc_var.get())
        messagebox.showinfo("Added", f"{name_var.get()} added to directory.")
        form.destroy()

    tk.Button(form, text="Save", command=submit).pack(pady=10)