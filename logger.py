import json
import os
from datetime import datetime

LOG_FILE = "user_actions.log"


def log_action(username, action):
    log_entry = {
        "username": username,
        "action": action,
        "timestamp": datetime.now().isoformat()
    }

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def get_logs():
    if not os.path.exists(LOG_FILE):
        return []

    with open(LOG_FILE, "r") as f:
        return [json.loads(line) for line in f]
