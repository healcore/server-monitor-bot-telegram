"""
Сбор системных метрик и проверка доступности хостов.
"""
import platform
import subprocess
from typing import Tuple

import psutil


def get_system_metrics(disk_path: str = "/") -> Tuple[float, float, float]:
    """Возвращает (cpu_percent, memory_percent, disk_percent)."""
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage(disk_path).percent
    return cpu, memory, disk


def ping_host(host: str, timeout: int = 2) -> bool:
    """Проверяет доступность хоста через системную команду ping (кроссплатформенно)."""
    is_windows = platform.system().lower() == "windows"
    count_flag = "-n" if is_windows else "-c"
    timeout_flag = "-w" if is_windows else "-W"
    timeout_value = str(timeout * 1000) if is_windows else str(timeout)

    try:
        result = subprocess.run(
            ["ping", count_flag, "1", timeout_flag, timeout_value, host],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout + 2,
        )
        return result.returncode == 0
    except Exception:
        return False
