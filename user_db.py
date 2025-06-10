import bcrypt

# Пример базы (в будущем заменим на SQLite)
USERS = {
    "student1": {
        "password_hash": bcrypt.hashpw(b"1234", bcrypt.gensalt()).decode(),

        "allowed_apps": ["notepad", "calc"]
    },

    "dias": {
        "password_hash": bcrypt.hashpw(b"loh", bcrypt.gensalt()).decode(),

        "allowed_apps": ["notepad", "calc", r"C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\devenv.exe"]
    },

    "talip": {
        "password_hash": bcrypt.hashpw(b"kot", bcrypt.gensalt()).decode(),

        "allowed_apps": ["notepad", "calc"]
    }
}

def verify_user(username, password):
    user = USERS.get(username)
    if not user:
        return False, None

    if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return True, user
    return False, None
