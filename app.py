import json
import os
import tkinter as tk
from tkinter import messagebox
import screeninfo
from moteur import generate_mail, get_names_in_prompt
from groq import Groq
import pyperclip
import keyboard
from directory import load_directory, add_person, delete_person, save_directory
import sounddevice as sd
import numpy as np
import wavio as wv
import Levenshtein

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
        try:
            if self.main_window is None or not self.main_window.winfo_exists():
                if self.user:
                    self._create_main_window()
                else:
                    self.create_registration_window()
            else:
                self.main_window.deiconify()
                self.main_window.lift()
        except tk.TclError:
            # Si la fenêtre a été détruite, on la recrée proprement
            self.main_window = None
            self._create_main_window()

            
    def minimize_to_tray(self):
        """Minimize the application to system tray"""
        keyboard.add_hotkey('ctrl+space', detect_audio_and_process, args=([['ctrl', 'space']]))
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


def handle_prompt(prompt_text, overlay=None):
    names = get_names_in_prompt(prompt_text, app.user['selected_provider'])
    name_mapping = {}
    if names:
        directory = load_directory()

        known_names = [person["name"].strip().lower() for person in directory]
        found_names = [name for name in names if name.lower() in known_names]
        missing_names = [name for name in names if name.lower() not in known_names]

        print("Found:", found_names)
        print("Missing:", missing_names)

        for name in missing_names:
            resolved_name = resolve_unknown_name(name, directory)
            if resolved_name:
                name_mapping[name] = resolved_name
                if resolved_name.lower() not in [n.lower() for n in found_names]:
                    found_names.append(resolved_name)


        if found_names:
            for name in found_names:
                name_mapping[name] = name  # identité


        recipients = []
        for name in found_names:
            for person in directory:
                if person["name"].strip().lower() == name.strip().lower():
                    recipients.append(person)
                    break
    else:
        recipients = []
    for original, resolved in name_mapping.items():
        # Remplace sans tenir compte de la casse, et en évitant les conflits
        prompt_text = prompt_text.replace(original, resolved)

    response = generate_mail(prompt_text, provider=app.user['selected_provider'], recipients=recipients)
    pyperclip.copy(response)
    print("Copied:", response)

    if overlay:
        overlay.deiconify()

    messagebox.showinfo("Done", "The mail has been generated and copied.")


def detect_audio_and_process(keys_to_press):
    freq = 44100
    channels = 1
    chunk_duration = 0.1
    chunk_size = int(freq * chunk_duration)

    print("Hold the key to record...")

    all_chunks = []
    stream = sd.InputStream(samplerate=freq, channels=channels)
    stream.start()

    condition = True
    while condition:
        for keys in keys_to_press:
            if not keyboard.is_pressed(keys):
                condition = False
        audio_chunk, _ = stream.read(chunk_size)
        all_chunks.append(audio_chunk)

    stream.stop()
    print("* Done recording")

    recording = np.concatenate(all_chunks, axis=0)
    wv.write("recording1.wav", recording, freq, sampwidth=2)
    filename = os.path.dirname(__file__) + "/recording1.wav"

    client = Groq()
    with open(filename, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(filename, file.read()),
            model="whisper-large-v3-turbo",
            language="en",
            response_format="verbose_json",
        )

    print("Transcript:", transcription.text)
    handle_prompt(transcription.text)

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
    root.geometry("300x250")

    tk.Label(root, text="Your Name:").pack(pady=(20, 5))
    name_entry = tk.Entry(root)
    name_entry.pack()

    tk.Label(root, text="Your Function:").pack(pady=(10, 5))
    function_entry = tk.Entry(root)
    function_entry.pack()

    # Provider selection dropdown
    tk.Label(root, text="Preferred Provider:").pack(pady=(10, 5))
    provider_var = tk.StringVar(value="groq")  # Default provider
    provider_options = ["groq", "ollama", "anythingllm", "genie"]
    tk.OptionMenu(root, provider_var, *provider_options).pack()

    def submit():
        name = name_entry.get().strip()
        function = function_entry.get().strip()
        selected_provider = provider_var.get().strip()

        if name and function:
            data = {
                "name": name,
                "function": function,
                "selected_provider": selected_provider
            }
            with open(USER_DATA_FILE, "w") as file:
                json.dump(data, file)

            messagebox.showinfo("Welcome", f"Thanks {name}! You're registered as a {function}.")
            root.destroy()
            app.user = load_user_data()
            app.show_main_window()
        else:
            messagebox.showwarning("Input Error", "Please fill in all fields.")


    tk.Button(root, text="Submit", command=submit).pack(pady=20)

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
        prompt.destroy()
        handle_prompt(user_input, overlay)

    tk.Button(prompt, text="Submit", command=submit).pack(pady=10)

    def on_close():
        overlay.deiconify()
        prompt.destroy()

    prompt.protocol("WM_DELETE_WINDOW", on_close)


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

        content_frame = tk.Frame(frame)
        content_frame.pack(side="left", fill="x", expand=True)

        info = f"{person['name']} – {person['position']}\n{person['description']}"
        tk.Label(content_frame, text=info, justify="left", anchor="w", wraplength=280).pack(anchor="w")

        btn_frame = tk.Frame(frame)
        btn_frame.pack(side="right")

        tk.Button(btn_frame, text="Edit", command=lambda p=person: edit_person_window(p, refresh)).pack(padx=2, pady=1)
        tk.Button(btn_frame, text="Delete", fg="red", command=lambda p=person['name']: delete_and_refresh(p, win)).pack(padx=2, pady=1)


    def add_new():
        win.destroy()
        add_person_form(None)

    tk.Button(win, text="Add Person", command=add_new).pack(pady=10)

def delete_and_refresh(name, win):
    if messagebox.askyesno("Confirm Delete", f"Delete {name}?"):
        delete_person(name)
        win.destroy()
        open_directory_window()


def edit_person_window(person, refresh_callback=None):
    form = tk.Toplevel()
    form.title(f"Edit {person['name']}")
    form.geometry("300x250")
    form.attributes("-topmost", True)

    name_var = tk.StringVar(value=person["name"])
    pos_var = tk.StringVar(value=person["position"])
    desc_var = tk.StringVar(value=person["description"])

    tk.Label(form, text="Name:").pack()
    tk.Entry(form, textvariable=name_var).pack()

    tk.Label(form, text="Position:").pack()
    tk.Entry(form, textvariable=pos_var).pack()

    tk.Label(form, text="Description:").pack()
    tk.Entry(form, textvariable=desc_var).pack()

    def save_changes():
        directory = load_directory()
        for p in directory:
            if p["name"].strip().lower() == person["name"].strip().lower():
                p["name"] = name_var.get().strip()
                p["position"] = pos_var.get().strip()
                p["description"] = desc_var.get().strip()
                break
        save_directory(directory)
        messagebox.showinfo("Success", f"{p['name']} has been updated.")
        form.destroy()
        if refresh_callback:
            refresh_callback()

    tk.Button(form, text="Save Changes", command=save_changes).pack(pady=10)


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
