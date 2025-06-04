import bcrypt

# Пример базы (в будущем заменим на SQLite)
USERS = {
    "student1": {
        "password_hash": bcrypt.hashpw(b"1234", bcrypt.gensalt()).decode(),
        "home_path": "C:/lab_students/student1",
        "allowed_apps": ["notepad", "calc"]  # exe-имена
    }
}

def verify_user(username, password):
    user = USERS.get(username)
    if not user:
        return False, None

    if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return True, user
    return False, None
