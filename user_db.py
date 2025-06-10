import bcrypt
import json
import os

ALLOWED_APPS_FILE = "allowed_apps.json"

def load_allowed_apps():
    if os.path.exists(ALLOWED_APPS_FILE):
        with open(ALLOWED_APPS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

ALLOWED_APPS = load_allowed_apps()

USERS = {
    "st": {
        "password_hash": bcrypt.hashpw(b"1234", bcrypt.gensalt()).decode(),
        # Список программ теперь общий, хранить в каждом пользователе не нужно
    },
    # ... другие пользователи
}

def verify_user(username, password):
    user = USERS.get(username)
    if not user:
        return False, None
    if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        user_info = dict(user)
        user_info["allowed_apps"] = ALLOWED_APPS
        return True, user_info
    return False, None