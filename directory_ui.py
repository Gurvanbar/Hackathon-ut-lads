import tkinter as tk
from tkinter import messagebox
from directory import load_directory, add_person, delete_person
from config_settings import DIRECTORY_WINDOW_SIZE, ADD_PERSON_WINDOW_SIZE

def open_directory_window():
    """Open the directory management window"""
    directory = load_directory()
    win = tk.Toplevel()
    win.title("People Directory")
    win.geometry(DIRECTORY_WINDOW_SIZE)
    win.attributes("-topmost", True)

    def refresh():
        win.destroy()
        open_directory_window()

    for person in directory:
        frame = tk.Frame(win, bd=1, relief="solid", padx=5, pady=5)
        frame.pack(fill="x", padx=5, pady=5)

        # Create a sub-frame to control text width
        content_frame = tk.Frame(frame)
        content_frame.pack(side="left", fill="x", expand=True)

        info = f"{person['name']} – {person['position']}\n{person['description']}"
        # wraplength = max width before wrapping
        tk.Label(content_frame, text=info, justify="left", anchor="w", wraplength=280).pack(anchor="w")

        def delete_callback(p=person['name']):
            if messagebox.askyesno("Confirm Delete", f"Delete {p}?"):
                delete_person(p)
                refresh()

        # Delete button visible on the right
        tk.Button(frame, text="Delete", fg="red", command=delete_callback).pack(side="right", padx=5)

    def add_new():
        win.destroy()
        add_person_form(None)

    tk.Button(win, text="Add Person", command=add_new).pack(pady=10)

def add_person_form(parent):
    """Create form to add a new person to the directory"""
    form = tk.Toplevel(parent)
    form.title("Add Person")
    form.geometry(ADD_PERSON_WINDOW_SIZE)

    name_var = tk.StringVar()
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
        form.destroy()
        open_directory_window()  # Refresh view

    tk.Button(form, text="Save", command=submit).pack(pady=10)
