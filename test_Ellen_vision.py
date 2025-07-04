import base64
import requests
import time
import threading
from PIL import Image
from io import BytesIO

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def loading_spinner(stop_event):
    while not stop_event.is_set():
        time.sleep(0.2)

def ask_qwen_about_sender(image_path, prompt="Quel est le nom et l'adresse email de l'expéditeur ?"):
    try:
        image_b64 = encode_image(image_path)

        data = {
            "model": "qwen2.5vl:3b",
            "prompt": prompt,
            "images": [image_b64],
            "stream": False
        }

        stop_event = threading.Event()
        spinner_thread = threading.Thread(target=loading_spinner, args=(stop_event,))
        spinner_thread.start()

        response = requests.post("http://localhost:11434/api/generate", json=data)

        stop_event.set()
        spinner_thread.join()

        if response.ok:
            return response.json().get("response", "")
        else:
            return None
    except:
        return None

if __name__ == "__main__":
    result = ask_qwen_about_sender("screenshot_email.png")
    if result:
        print(result)
