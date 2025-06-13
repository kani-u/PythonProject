import bcrypt

USERS = {
    "st": {
        "password_hash": bcrypt.hashpw(b"1234", bcrypt.gensalt()).decode(),
    },
}

def verify_user(username, password):
    user = USERS.get(username)
    if not user:
        return False, None
    if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return True, {}  # Возвращаем пустой словарь для user_info
    return False, None
