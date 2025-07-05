import json
import os
import tkinter as tk
from tkinter import messagebox
import screeninfo
from moteur import generate_mail, detect_audio_and_process
import pyperclip
import keyboard

USER_DATA_FILE = "user_data.json"

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    return None

def save_user_data(name, function):
    data = {
        "name": name,
        "function": function
    }
    with open(USER_DATA_FILE, "w") as file:
        json.dump(data, file)

def submit_form(name_entry, function_entry, root):
    name = name_entry.get().strip()
    function = function_entry.get().strip()
    
    if name and function:
        save_user_data(name, function)
        messagebox.showinfo("Welcome", f"Thanks {name}! You're registered as a {function}.")
        root.destroy()
        user = load_user_data()
        show_main_window(user)
    else:
        messagebox.showwarning("Input Error", "Please fill in both fields.")

def create_registration_window():
    root = tk.Tk()
    root.title("User Registration")
    root.geometry("300x200")

    tk.Label(root, text="Your Name:").pack(pady=(20, 5))
    name_entry = tk.Entry(root)
    name_entry.pack()

    tk.Label(root, text="Your Function:").pack(pady=(10, 5))
    function_entry = tk.Entry(root)
    function_entry.pack()

    submit_btn = tk.Button(root, text="Submit", command=lambda: submit_form(name_entry, function_entry, root))
    submit_btn.pack(pady=20)

    root.mainloop()

#####

def launch_overlay_app(user):
    overlay = tk.Tk()
    overlay.overrideredirect(True)  # Borderless
    overlay.attributes("-topmost", True)
    overlay.attributes("-alpha", 0.7)

    # Get screen dimensions to position overlay on the bottom right
    screen = screeninfo.get_monitors()[0]
    screen_width = screen.width - 40
    screen_height = int((screen.height) / 5)

    overlay_size = 40
    offset = 30
    x = screen_width - overlay_size - offset
    y = screen_height - overlay_size - offset

    overlay.geometry(f"{overlay_size}x{overlay_size}+{x}+{y}")

    canvas = tk.Canvas(overlay, width=overlay_size, height=overlay_size, highlightthickness=0, bg='white')
    canvas.pack()

    # Draw round green circle
    circle = canvas.create_oval(0, 0, overlay_size, overlay_size, fill="#28a745", outline="")

    # Close button
    def close_overlay():
        overlay.destroy()

    close_btn = tk.Button(overlay, text="x", command=close_overlay, bg="#28a745", fg="white", bd=0,
                          font=("Arial", 8), relief="flat", highlightthickness=0)
    close_btn.place(x=overlay_size - 15, y=2)

    # Click handler for main circle
    def on_click(event=None):
        overlay.withdraw()
        prompt_window(overlay, user)

    canvas.tag_bind(circle, "<Button-1>", on_click)

    # Dragging logic bound to the arrow button
    def start_move(event):
        overlay.x = event.x_root
        overlay.y = event.y_root

    def do_move(event):
        dx = event.x_root - overlay.x
        dy = event.y_root - overlay.y
        x = overlay.winfo_x() + dx
        y = overlay.winfo_y() + dy
        overlay.geometry(f"+{x}+{y}")
        overlay.x = event.x_root
        overlay.y = event.y_root

    # Arrow button for dragging
    move_btn = tk.Button(overlay, text="✥", bg="#28a745", fg="white", bd=0,
                         font=("Arial", 8), relief="flat", highlightthickness=0)
    move_btn.place(x=overlay_size - 17, y=overlay_size - 20)

    move_btn.bind("<ButtonPress-1>", start_move)
    move_btn.bind("<B1-Motion>", do_move)

    overlay.mainloop()

def prompt_window(overlay, user):
    prompt = tk.Toplevel()
    prompt.title("Prompt")
    prompt.geometry("400x200")
    prompt.attributes("-topmost", True)

    tk.Label(prompt, text=f"{user['name']}, enter your mail prompt:", font=("Arial", 12)).pack(pady=10)
    entry = tk.Entry(prompt, width=40)
    entry.pack(pady=5)

    def submit():
        user_input = entry.get()
        #ASOKO DESU
        response = generate_mail(user_input)
        prompt.destroy()
        overlay.deiconify()
        messagebox.showinfo("The mail has been generated")
        print(response)
        pyperclip.copy(response)
        

    tk.Button(prompt, text="Submit", command=submit).pack(pady=10)

    def on_close():
        overlay.deiconify()
        prompt.destroy()

    prompt.protocol("WM_DELETE_WINDOW", on_close)


#####

def show_main_window(user):
    root = tk.Tk()
    root.title("Welcome Back")
    root.geometry("300x200")

    greeting = f"Welcome back, {user['name']}!\nRole: {user['function']}"
    tk.Label(root, text=greeting, font=("Arial", 12), pady=10).pack()

    # Button to reset profile
    def reset_profile():
        os.remove(USER_DATA_FILE)
        root.destroy()
        create_registration_window()

    def start_app():
        keyboard.add_hotkey('ctrl+space', detect_audio_and_process, args=([['ctrl', 'space']]))
        root.destroy()
        launch_overlay_app(user)

    tk.Button(root, text="Change Profile", command=reset_profile).pack(pady=10)
    tk.Button(root, text="Start App", command=start_app).pack()

    root.mainloop()

def main():
    user = load_user_data()

    if user is None:
        create_registration_window()
    else:
        show_main_window(user)

if __name__ == "__main__":
    main()
