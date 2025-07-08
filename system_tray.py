import json
import os
import tkinter as tk
from tkinter import messagebox
import pyautogui
import pystray
from PIL import Image, ImageDraw
import threading
import keyboard
import pyperclip
from moteur import detect_audio_and_process, generate_mail
from user_management import load_user_data, create_registration_window
from overlay import launch_overlay_app
from directory_ui import open_directory_window
from config_settings import (
    USER_DATA_FILE, ICON_FILE, APP_NAME, MAIN_WINDOW_SIZE,
    TRAY_ICON_SIZE, TRAY_ICON_FALLBACK_SIZE, OVERLAY_COLOR, MAIN_HOTKEY,
    DEFAULT_CLIPBOARD_MODE
)

class SystemTrayApp:
    def __init__(self):
        self.tray_icon = None
        self.main_window = None
        self.overlay_window = None
        self.user = None
        self.clipboard_mode = DEFAULT_CLIPBOARD_MODE  # Default mode
        self.selected_provider = None  # Selected LLM provider
        
    def create_tray_icon(self):
        """Create a system tray icon"""
        # Try to load existing icon file, otherwise create one programmatically
        try:
            if os.path.exists(ICON_FILE):
                image = Image.open(ICON_FILE)
            else:
                # Create a simple icon image
                image = Image.new('RGB', TRAY_ICON_SIZE, color=(40, 167, 69))  # Green color
                draw = ImageDraw.Draw(image)
                draw.ellipse([8, 8, 56, 56], fill=(255, 255, 255))  # White circle
                draw.ellipse([16, 16, 48, 48], fill=(40, 167, 69))   # Green center
        except Exception:
            # Fallback to programmatic icon
            image = Image.new('RGB', TRAY_ICON_FALLBACK_SIZE, color=(40, 167, 69))
            draw = ImageDraw.Draw(image)
            draw.ellipse([4, 4, 28, 28], fill=(255, 255, 255))
        
        # Create the menu
        menu_items = [
            pystray.MenuItem("Show App", self.show_main_window),
            pystray.MenuItem("Select LLM Provider", self.show_provider_selection),
            pystray.MenuItem("Start Overlay", self.start_overlay),
            pystray.MenuItem("Directory", self.open_directory_window),
            pystray.MenuItem("---", None),  # Separator
            pystray.MenuItem("Exit", self.quit_app)
        ]
        
        self.tray_icon = pystray.Icon(APP_NAME, image, APP_NAME, pystray.Menu(*menu_items))
        
    def show_main_window(self, icon=None, item=None):
        """Show the main application window"""
        if self.main_window is None or not self.main_window.winfo_exists():
            if self.user:
                self.load_user_preferences()  # Load preferences before creating window
                self._create_main_window()
            else:
                create_registration_window(self)
        else:
            self.main_window.deiconify()
            self.main_window.lift()
            
    def minimize_to_tray(self):
        """Minimize the application to system tray"""
        if self.main_window:
            self.main_window.withdraw()
    
    def handle_email(self):
        """Handle email processing"""
        if self.clipboard_mode == True:
            # Auto-read from clipboard
            content = self.copy_selected_content()
            if content is None:
                messagebox.showwarning("Empty Clipboard", "No content found in clipboard!")
                return
            text = detect_audio_and_process(provider=self.selected_provider)
            if text is None:
                messagebox.showerror("Error", "Failed to process audio content!")
                return
            result = generate_mail(email_received=content, provider=self.selected_provider, i_want_to_respond=text)
            if result is None:
                messagebox.showerror("Error", "Failed to generate email response!")
                return
            pyperclip.copy(result)
            pyautogui.hotkey("ctrl", "v")

        else:
            # Open manual input window
            self.open_manual_input_window()
            return

            
    def start_overlay(self, icon=None, item=None):
        """Start the overlay application"""
        if self.user:
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
        print("Starting system tray icon...")
        self.create_tray_icon()
        self.tray_icon.run()

    def _create_main_window(self):
        """Create the main application window"""
        root = tk.Tk()
        root.title("Welcome Back")
        root.geometry("350x500")
        root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        # Load user preferences
        self.load_user_preferences()

        greeting = f"Welcome back, {self.user['name']}!\nRole: {self.user['function']}"
        tk.Label(root, text=greeting, font=("Arial", 12), pady=10).pack()

        # Clipboard mode toggle
        clipboard_frame = tk.Frame(root)
        clipboard_frame.pack(pady=10)
        
        tk.Label(clipboard_frame, text="Email Processing Mode:", font=("Arial", 10, "bold")).pack()
        
        self.clipboard_mode_var = tk.BooleanVar(value=self.clipboard_mode)
        
        def toggle_clipboard_mode():
            self.clipboard_mode = self.clipboard_mode_var.get()
            self.save_user_preferences()
        
        tk.Checkbutton(
            clipboard_frame, 
            text="Auto-read from clipboard (when unchecked, opens manual input window)",
            variable=self.clipboard_mode_var,
            command=toggle_clipboard_mode,
            wraplength=300
        ).pack()

        # Button to reset profile
        def reset_profile():
            os.remove(USER_DATA_FILE)
            root.destroy()
            self.user = None
            create_registration_window(self)
            
        keyboard.add_hotkey(MAIN_HOTKEY, self.handle_email)

        tk.Button(root, text="Minimize to Tray", command=self.minimize_to_tray).pack(pady=5)
        if DEFAULT_CLIPBOARD_MODE:
            tk.Button(root, text=f"Start App (shortcut is {MAIN_HOTKEY})", command=self.handle_email).pack()
        # tk.Button(root, text="Test Email Processing", command=test_clipboard_mode).pack(pady=5)
        tk.Button(root, text="LLM Provider", command=self.show_provider_selection).pack(pady=5)
        tk.Button(root, text="Open Directory", command=self.open_directory_window).pack(pady=5)
        tk.Button(root, text="Edit Profile", command=reset_profile).pack(pady=10)

        self.main_window = root
        root.mainloop()
        
    def launch_overlay_app(self):
        """Launch the overlay application"""
        self.overlay_window = launch_overlay_app(self)
    def show_provider_selection(self, icon=None, item=None):
        """Show a window to select LLM provider"""
        provider_window = tk.Toplevel(self.main_window if self.main_window else None)
        provider_window.title("Select LLM Provider")
        provider_window.geometry("500x450")
        provider_window.attributes("-topmost", True)

        tk.Label(provider_window, text="Choose your LLM Provider:", font=("Arial", 14, "bold")).pack(pady=20)

        # Load current selection
        current_provider = self.selected_provider or "ollama"
        provider_var = tk.StringVar(value=current_provider)

        providers = [
            ("Groq (Online, Best)", "groq"),
            ("Ollama (CPU/GPU, 3rd party, Local)", "ollama"),
            ("AnythingLLM (NPU, 3rd party, Local)", "anythingllm"),
            ("Genie (NPU, Qualcomm, Slow, Local)", "genie")
        ]

        for display_name, provider_id in providers:
            tk.Radiobutton(
                provider_window,
                text=display_name,
                variable=provider_var,
                value=provider_id,
                font=("Arial", 12),
                anchor="w",
                padx=50
            ).pack(pady=5, anchor=tk.W)

        def apply_selection():
            self.selected_provider = provider_var.get()
            self.save_user_preferences()
            messagebox.showinfo("Success", f"Provider set to: {provider_var.get().capitalize()}")
            provider_window.destroy()
        
        button_frame = tk.Frame(provider_window)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Apply", command=apply_selection, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=provider_window.destroy, width=10).pack(side=tk.LEFT, padx=5)
        
        provider_window.mainloop()

    def open_directory_window(self, icon=None, item=None):
        """Open the directory window"""
        open_directory_window()

    def load_user_preferences(self):
        """Load user preferences including clipboard mode and selected provider"""
        if self.user and 'clipboard_mode' in self.user:
            self.clipboard_mode = self.user['clipboard_mode']
        else:
            self.clipboard_mode = DEFAULT_CLIPBOARD_MODE
            
        if self.user and 'selected_provider' in self.user:
            self.selected_provider = self.user['selected_provider']
        else:
            self.selected_provider = "ollama"  # Default provider

    def save_user_preferences(self):
        """Save user preferences including clipboard mode and selected provider"""
        if self.user:
            self.user['clipboard_mode'] = self.clipboard_mode
            self.user['selected_provider'] = self.selected_provider
            with open(USER_DATA_FILE, 'w') as f:
                json.dump(self.user, f, indent=2)

    def copy_selected_content(self):
        """Copy the content from clipboard and returns it"""
        try:
            # pyautogui.hotkey("ctrl", "c")
            clipboard_content = pyperclip.paste()
            if not clipboard_content.strip():
                messagebox.showwarning("Empty Clipboard", "No content found in clipboard!")
                return
            
            return clipboard_content
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process clipboard content: {str(e)}")
            return None

    def open_manual_input_window(self):
        """Open a window for manual email input and processing"""
        input_window = tk.Toplevel(self.main_window)
        input_window.title("Manual Email Input")
        input_window.geometry("600x800")
        input_window.attributes("-topmost", True)
        
        # Provider selection section
        provider_frame = tk.Frame(input_window)
        provider_frame.pack(pady=10, fill=tk.X, padx=20)
        
        # Input section
        tk.Label(input_window, text="Paste your email content here:", font=("Arial", 12)).pack(pady=10)
        
        input_text = tk.Text(input_window, width=60, height=8, wrap=tk.WORD)
        input_text.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        # Audio input section
        audio_frame = tk.Frame(input_window)
        audio_frame.pack(pady=10, fill=tk.X, padx=20)
        tk.Label(audio_frame, text="Then audio record what you want to answer to the person in your own terms:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)

        recorded_text = tk.StringVar(value="")
        stop_flag = threading.Event()
        recording_thread = None

        status_label = tk.Label(audio_frame, text="⏺️ Idle", font=("Arial", 12))
        status_label.pack(side=tk.LEFT, padx=5)

        def start_recording():
            nonlocal recording_thread, stop_flag
            
            if recording_thread and recording_thread.is_alive():
                return
                
            # Reset stop flag
            stop_flag.clear()
            
            status_label.config(text="🎙️ Recording...")
            record_button.config(state=tk.DISABLED)
            stop_button.config(state=tk.NORMAL)
            
            def record():
                try:
                    text = detect_audio_and_process(provider=self.selected_provider, stop_flag=stop_flag)
                    
                    # Update UI in main thread
                    def update_ui():
                        recorded_text.set(text if text else "")
                        status_label.config(text="✅ Done" if text else "⚠️ No input")
                        record_button.config(state=tk.NORMAL)
                        stop_button.config(state=tk.DISABLED)
                    
                    input_window.after(0, update_ui)
                    
                except Exception as e:
                    def update_ui_error():
                        status_label.config(text="❌ Error")
                        record_button.config(state=tk.NORMAL)
                        stop_button.config(state=tk.DISABLED)
                        print(f"Recording error: {e}")
                    
                    input_window.after(0, update_ui_error)
            
            # Start recording in a thread
            recording_thread = threading.Thread(target=record, daemon=True)
            recording_thread.start()

        def stop_recording():
            nonlocal stop_flag
            
            if recording_thread and recording_thread.is_alive():
                stop_flag.set()
                status_label.config(text="⏹️ Stopping...")
                stop_button.config(state=tk.DISABLED)

        record_button = tk.Button(audio_frame, text="Record Audio", command=start_recording)
        record_button.pack(side=tk.LEFT, padx=5)
        stop_button = tk.Button(audio_frame, text="Stop", command=stop_recording, state=tk.DISABLED)
        stop_button.pack(side=tk.LEFT, padx=5)
        
        # Output section
        tk.Label(input_window, text="Generated response:", font=("Arial", 12)).pack(pady=(10,5))
        
        output_text = tk.Text(input_window, width=60, height=8, wrap=tk.WORD, state=tk.DISABLED)
        output_text.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        def process_input():
            content = input_text.get("1.0", tk.END).strip()
            if not content:
                messagebox.showwarning("Empty Input", "Please enter some content!")
                return
            
            try:
                response = generate_mail(email_received=content, provider=self.selected_provider, i_want_to_respond=recorded_text.get())
                
                # Display response
                output_text.config(state=tk.NORMAL)
                output_text.delete("1.0", tk.END)
                output_text.insert("1.0", response)
                output_text.config(state=tk.DISABLED)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate response: {str(e)}")
        
        def copy_response():
            response = output_text.get("1.0", tk.END).strip()
            if response:
                pyperclip.copy(response)
                messagebox.showinfo("Copied", "Response copied to clipboard!")
            else:
                messagebox.showwarning("No Response", "No response to copy!")
        
        # Cleanup function for window close
        def on_window_close():
            if recording_thread and recording_thread.is_alive():
                stop_flag.set()
            input_window.destroy()
        
        input_window.protocol("WM_DELETE_WINDOW", on_window_close)
        
        # Buttons
        button_frame = tk.Frame(input_window)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Generate Response", command=process_input).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Copy Response", command=copy_response).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close", command=on_window_close).pack(side=tk.LEFT, padx=5)


# Create the app instance for import
app = SystemTrayApp()
