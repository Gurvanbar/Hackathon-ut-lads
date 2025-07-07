import tkinter as tk
from tkinter import messagebox
import screeninfo
from moteur import generate_mail
import pyperclip
from config_settings import (
    OVERLAY_SIZE, OVERLAY_OFFSET, OVERLAY_ALPHA, OVERLAY_COLOR, PROMPT_WINDOW_SIZE
)

def launch_overlay_app(app):
    """Launch the overlay application"""
    if hasattr(app, 'overlay_window') and app.overlay_window and app.overlay_window.winfo_exists():
        return app.overlay_window
        
    overlay = tk.Tk()
    overlay.overrideredirect(True)  # Borderless
    overlay.attributes("-topmost", True)
    overlay.attributes("-alpha", OVERLAY_ALPHA)

    # Get screen dimensions to position overlay on the bottom right
    screen = screeninfo.get_monitors()[0]
    screen_width = screen.width - 40
    screen_height = int((screen.height) / 5)

    x = screen_width - OVERLAY_SIZE - OVERLAY_OFFSET
    y = screen_height - OVERLAY_SIZE - OVERLAY_OFFSET

    overlay.geometry(f"{OVERLAY_SIZE}x{OVERLAY_SIZE}+{x}+{y}")

    canvas = tk.Canvas(overlay, width=OVERLAY_SIZE, height=OVERLAY_SIZE, highlightthickness=0, bg='white')
    canvas.pack()

    # Draw round green circle
    circle = canvas.create_oval(0, 0, OVERLAY_SIZE, OVERLAY_SIZE, fill=OVERLAY_COLOR, outline="")

    # Close button
    def close_overlay():
        overlay.destroy()
        app.overlay_window = None

    close_btn = tk.Button(overlay, text="x", command=close_overlay, bg=OVERLAY_COLOR, fg="white", bd=0,
                          font=("Arial", 8), relief="flat", highlightthickness=0)
    close_btn.place(x=OVERLAY_SIZE - 15, y=2)

    # Click handler for main circle
    def on_click(event=None):
        overlay.withdraw()
        app.handle_email()
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
    move_btn = tk.Button(overlay, text="✥", bg=OVERLAY_COLOR, fg="white", bd=0,
                         font=("Arial", 8), relief="flat", highlightthickness=0)
    move_btn.place(x=OVERLAY_SIZE - 17, y=OVERLAY_SIZE - 20)

    move_btn.bind("<ButtonPress-1>", start_move)
    move_btn.bind("<B1-Motion>", do_move)

    overlay.mainloop()
    return overlay
