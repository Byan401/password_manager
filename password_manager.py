import json
import os
import sys
from cryptography.fernet import Fernet

# --- Generate / Load encryption key ---
KEY_FILE = "secret.key"
DATA_FILE = "passwords.json"

def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return key

fernet = Fernet(load_key())

# --- Save password ---
def save_password(service, username, password):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {}

    data[service] = {
        "username": username,
        "password": fernet.encrypt(password.encode()).decode()
    }

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print(f"✅ Saved password for {service}")

# --- Get password ---
def get_password(service):
    if not os.path.exists(DATA_FILE):
        print("❌ No passwords saved yet.")
        return

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    if service in data:
        username = data[service]["username"]
        password = fernet.decrypt(data[service]["password"].encode()).decode()
        print(f"🔑 {service} → {username} / {password}")
    else:
        print(f"❌ No entry found for {service}")

# --- CLI Interface ---
if len(sys.argv) < 2:
    print("Usage:")
    print("  add <service> <username> <password>")
    print("  get <service>")
    sys.exit(1)

command = sys.argv[1].lower()

if command == "add" and len(sys.argv) == 5:
    _, _, service, username, password = sys.argv
    save_password(service, username, password)

elif command == "get" and len(sys.argv) == 3:
    _, _, service = sys.argv
    get_password(service)

else:
    print("❌ Invalid command or arguments.")
