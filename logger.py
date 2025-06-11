import logging
from logging.handlers import RotatingFileHandler
import json
import os

# Получаем путь к папке с exe-файлом (или скриптом, если в dev-режиме)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Папка для логов
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Полный путь к лог-файлу
LOG_FILE = os.path.join(LOG_DIR, "user_actions.log")

class JsonLogFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "username": getattr(record, 'username', None),
            "action": getattr(record, 'action', record.getMessage()),
            "extra": getattr(record, 'extra', None),
        }
        return json.dumps(log_entry, ensure_ascii=False)

logger = logging.getLogger("lab_shell")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=5, encoding="utf-8")
    formatter = JsonLogFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def log_action(username, action, extra=None):
    try:
        logger.info(
            "",
            extra={
                "username": username,
                "action": action,
                "extra": extra
            }
        )
    except Exception as e:
        print("LOG ERROR:", e)

def get_logs():
    logs = []
    if not os.path.exists(LOG_FILE):
        return logs
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                logs.append(json.loads(line))
            except Exception:
                continue
    return logs
