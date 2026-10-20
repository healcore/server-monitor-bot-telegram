"""
Telegram-бот для мониторинга сервера: CPU, RAM, диск, доступность сервисов.

Запуск:
    python bot.py
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message

from config import settings
from monitor import get_system_metrics, ping_host

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("server-monitor-bot")

router = Router()


def format_status() -> str:
    cpu, mem, disk = get_system_metrics(settings.disk_path)
    lines = [
        "📊 <b>Статус сервера</b>",
        f"CPU:  {cpu:.1f}%",
        f"RAM:  {mem:.1f}%",
        f"Disk: {disk:.1f}%",
    ]
    if settings.monitored_hosts:
        lines.append("")
        lines.append("<b>Сервисы:</b>")
        for host in settings.monitored_hosts:
            ok = ping_host(host)
            mark = "🟢" if ok else "🔴"
            lines.append(f"{mark} {host}")
    return "\n".join(lines)


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я слежу за состоянием сервера.\n\n"
        "Команды:\n"
        "/status — текущие метрики\n"
        "/help — список команд"
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "/status — CPU, RAM, диск и доступность отслеживаемых сервисов"
    )


@router.message(Command("status"))
async def cmd_status(message: Message) -> None:
    await message.answer(format_status(), parse_mode="HTML")


async def alert_loop(bot: Bot) -> None:
    """Фоновая задача: раз в check_interval секунд проверяет пороги и шлёт алерты."""
    is_alerting = {"cpu": False, "mem": False, "disk": False}
    unreachable_hosts: set[str] = set()

    while True:
        try:
            cpu, mem, disk = get_system_metrics(settings.disk_path)
            checks = {
                "cpu": (cpu, settings.cpu_threshold, "CPU"),
                "mem": (mem, settings.mem_threshold, "RAM"),
                "disk": (disk, settings.disk_threshold, "Диск"),
            }

            for key, (value, threshold, label) in checks.items():
                if value >= threshold and not is_alerting[key]:
                    await bot.send_message(
                        settings.chat_id,
                        f"⚠️ {label} превысил порог: {value:.1f}% (порог {threshold:.0f}%)",
                    )
                    is_alerting[key] = True
                elif value < threshold and is_alerting[key]:
                    await bot.send_message(
                        settings.chat_id,
                        f"✅ {label} вернулся в норму: {value:.1f}%",
                    )
                    is_alerting[key] = False

            for host in settings.monitored_hosts:
                reachable = ping_host(host)
                if not reachable and host not in unreachable_hosts:
                    await bot.send_message(settings.chat_id, f"🔴 {host} недоступен!")
                    unreachable_hosts.add(host)
                elif reachable and host in unreachable_hosts:
                    await bot.send_message(settings.chat_id, f"🟢 {host} снова доступен")
                    unreachable_hosts.discard(host)

        except Exception:
            logger.exception("Ошибка в цикле проверки метрик")

        await asyncio.sleep(settings.check_interval)


async def main() -> None:
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN не задан. Проверьте файл .env")
    if not settings.chat_id:
        logger.warning("CHAT_ID не задан — фоновые алерты отправляться не будут")

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    dp.include_router(router)

    asyncio.create_task(alert_loop(bot))

    logger.info("Бот запущен, интервал проверки: %s сек.", settings.check_interval)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
