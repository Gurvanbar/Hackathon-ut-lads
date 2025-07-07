import json
import os
import tkinter as tk
from tkinter import messagebox
import screeninfo
from moteur import generate_mail, detect_audio_and_process
import pyperclip
import keyboard
from directory import load_directory, add_person, delete_person
import pystray
from PIL import Image, ImageDraw
import threading

USER_DATA_FILE = "user_data.json"

class SystemTrayApp:
    def __init__(self):
        self.tray_icon = None
        self.main_window = None
        self.overlay_window = None
        self.user = None
        
    def create_tray_icon(self):
        """Create a system tray icon"""
        # Try to load existing icon file, otherwise create one programmatically
        try:
            if os.path.exists('app_icon.ico'):
                image = Image.open('app_icon.ico')
            else:
                # Create a simple icon image
                image = Image.new('RGB', (64, 64), color=(40, 167, 69))  # Green color
                draw = ImageDraw.Draw(image)
                draw.ellipse([8, 8, 56, 56], fill=(255, 255, 255))  # White circle
                draw.ellipse([16, 16, 48, 48], fill=(40, 167, 69))   # Green center
        except Exception:
            # Fallback to programmatic icon
            image = Image.new('RGB', (32, 32), color=(40, 167, 69))
            draw = ImageDraw.Draw(image)
            draw.ellipse([4, 4, 28, 28], fill=(255, 255, 255))
        
        # Create the menu
        menu_items = [
            pystray.MenuItem("Show App", self.show_main_window),
            pystray.MenuItem("Start Overlay", self.start_overlay),
            pystray.MenuItem("Directory", self.open_directory_window),
            pystray.MenuItem("---", None),  # Separator
            pystray.MenuItem("Exit", self.quit_app)
        ]
        
        self.tray_icon = pystray.Icon("Mail Assistant", image, "Mail Assistant", pystray.Menu(*menu_items))
        
    def show_main_window(self, icon=None, item=None):
        """Show the main application window"""
        if self.main_window is None or not self.main_window.winfo_exists():
            if self.user:
                self._create_main_window()
            else:
                self.create_registration_window()
        else:
            self.main_window.deiconify()
            self.main_window.lift()
            
    def minimize_to_tray(self):
        """Minimize the application to system tray"""
        if self.main_window:
            self.main_window.withdraw()
            
    def start_overlay(self, icon=None, item=None):
        """Start the overlay application"""
        if self.user:
            keyboard.add_hotkey('ctrl+space', detect_audio_and_process, args=([['ctrl', 'space']]))
            if self.main_window:
                self.main_window.withdraw()
            self.launch_overlay_app()
        else:
            messagebox.showwarning("No User", "Please register first!")
            
    def quit_app(self, icon=None, item=None):
        """Quit the application completely"""
        if self.tray_icon:
            self.tray_icon.stop()
        if self.main_window:
            self.main_window.quit()
        if self.overlay_window:
            self.overlay_window.quit()
        os._exit(0)
        
    def run_tray(self):
        """Run the system tray icon"""
        self.create_tray_icon()
        self.tray_icon.run()

    def _create_main_window(self):
        """Create the main application window"""
        root = tk.Tk()
        root.title("Welcome Back")
        root.geometry("300x200")
        root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        greeting = f"Welcome back, {self.user['name']}!\nRole: {self.user['function']}"
        tk.Label(root, text=greeting, font=("Arial", 12), pady=10).pack()

        # Button to reset profile
        def reset_profile():
            os.remove(USER_DATA_FILE)
            root.destroy()
            self.user = None
            self.create_registration_window()

        def start_app():
            keyboard.add_hotkey('ctrl+space', detect_audio_and_process, args=([['ctrl', 'space']]))
            root.withdraw()
            self.launch_overlay_app()

        tk.Button(root, text="Open Directory", command=open_directory_window).pack(pady=5)
        tk.Button(root, text="Edit Profile", command=reset_profile).pack(pady=10)
        tk.Button(root, text="Start App", command=start_app).pack()
        tk.Button(root, text="Minimize to Tray", command=self.minimize_to_tray).pack(pady=5)

        self.main_window = root
        root.mainloop()
        
    def create_registration_window(self):
        """Create the registration window"""
        create_registration_window()
        
    def launch_overlay_app(self):
        """Launch the overlay application"""
        launch_overlay_app()
        
    def open_directory_window(self, icon=None, item=None):
        """Open the directory window"""
        open_directory_window()

# Global instance
app = SystemTrayApp()

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
        app.user = load_user_data()
        app._create_main_window()
    else:
        messagebox.showwarning("Input Error", "Please fill in both fields.")

def create_registration_window():
    root = tk.Tk()
    root.title("User Registration")
    root.geometry("300x200")
    root.protocol("WM_DELETE_WINDOW", app.minimize_to_tray)

    tk.Label(root, text="Your Name:").pack(pady=(20, 5))
    name_entry = tk.Entry(root)
    name_entry.pack()

    tk.Label(root, text="Your Function:").pack(pady=(10, 5))
    function_entry = tk.Entry(root)
    function_entry.pack()

    submit_btn = tk.Button(root, text="Submit", command=lambda: submit_form(name_entry, function_entry, root))
    submit_btn.pack(pady=20)

    app.main_window = root
    root.mainloop()

#####

def launch_overlay_app():
    if app.overlay_window and app.overlay_window.winfo_exists():
        return
        
    overlay = tk.Tk()
    app.overlay_window = overlay
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
        app.overlay_window = None

    close_btn = tk.Button(overlay, text="x", command=close_overlay, bg="#28a745", fg="white", bd=0,
                          font=("Arial", 8), relief="flat", highlightthickness=0)
    close_btn.place(x=overlay_size - 15, y=2)

    # Click handler for main circle
    def on_click(event=None):
        overlay.withdraw()
        prompt_window(overlay)

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

def prompt_window(overlay):
    prompt = tk.Toplevel()
    prompt.title("Prompt")
    prompt.geometry("400x200")
    prompt.attributes("-topmost", True)

    tk.Label(prompt, text=f"{app.user['name']}, enter your mail prompt:", font=("Arial", 12)).pack(pady=10)
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

def open_directory_window():
    directory = load_directory()
    win = tk.Toplevel()
    win.title("People Directory")
    win.geometry("400x400")
    win.attributes("-topmost", True)

    def refresh():
        win.destroy()
        open_directory_window()

    for person in directory:
        frame = tk.Frame(win, bd=1, relief="solid", padx=5, pady=5)
        frame.pack(fill="x", padx=5, pady=5)

        # Créer une sous-frame pour contrôler largeur du texte
        content_frame = tk.Frame(frame)
        content_frame.pack(side="left", fill="x", expand=True)

        info = f"{person['name']} – {person['position']}\n{person['description']}"
        # wraplength = max width before wrapping
        tk.Label(content_frame, text=info, justify="left", anchor="w", wraplength=280).pack(anchor="w")

        def delete_callback(p=person['name']):
            if messagebox.askyesno("Confirm Delete", f"Delete {p}?"):
                delete_person(p)
                refresh()

        # Bouton delete visible à droite
        tk.Button(frame, text="Delete", fg="red", command=delete_callback).pack(side="right", padx=5)

    def add_new():
        win.destroy()
        add_person_form(None)

    tk.Button(win, text="Add Person", command=add_new).pack(pady=10)


def add_person_form(parent):
    form = tk.Toplevel(parent)
    form.title("Add Person")
    form.geometry("300x250")

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



def main():
    # Load user data on startup
    app.user = load_user_data()
    
    # Start the system tray icon in a separate thread
    tray_thread = threading.Thread(target=app.run_tray, daemon=True)
    tray_thread.start()
    
    # Show the main window or registration window initially
    if app.user is None:
        app.create_registration_window()
    else:
        app.show_main_window()

if __name__ == "__main__":
    main()
