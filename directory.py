import json
import os
DIRECTORY_FILE = "directory.json"

def load_directory():
    if not os.path.exists(DIRECTORY_FILE):
        return []
    with open(DIRECTORY_FILE, "r") as f:
        return json.load(f)

print(load_directory())

def save_directory(directory):
    with open(DIRECTORY_FILE, "w") as f:
        json.dump(directory, f, indent=2)

def add_person(name, position, description):
    directory = load_directory()
    directory.append({
        "name": name,
        "position": position,
        "description": description
    })
    save_directory(directory)

def delete_person(name):
    directory = load_directory()
    updated = [p for p in directory if p["name"].lower() != name.lower()]
    save_directory(updated)