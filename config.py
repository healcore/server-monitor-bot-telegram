"""
Загрузка конфигурации бота из переменных окружения / .env файла.
"""
import os
from dataclasses import dataclass, field
from typing import List

from dotenv import load_dotenv

load_dotenv()


def _get_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def _get_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


@dataclass
class Settings:
    bot_token: str = os.getenv("BOT_TOKEN", "")
    chat_id: str = os.getenv("CHAT_ID", "")
    check_interval: int = _get_int("CHECK_INTERVAL", 300)
    cpu_threshold: float = _get_float("CPU_THRESHOLD", 85.0)
    mem_threshold: float = _get_float("MEM_THRESHOLD", 85.0)
    disk_threshold: float = _get_float("DISK_THRESHOLD", 90.0)
    disk_path: str = os.getenv("DISK_PATH", "/")
    monitored_hosts: List[str] = field(
        default_factory=lambda: [
            h.strip() for h in os.getenv("MONITORED_HOSTS", "").split(",") if h.strip()
        ]
    )


settings = Settings()
