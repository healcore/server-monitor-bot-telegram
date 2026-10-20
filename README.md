# Server Monitor Bot

Telegram-бот для мониторинга состояния сервера: CPU, RAM, диск и доступность сервисов. Присылает алерты при превышении пороговых значений и когда сервис становится недоступен.

## Возможности

- `/status` — текущие метрики по запросу
- Фоновая проверка раз в N секунд с алертами при превышении/восстановлении порогов
- Проверка доступности хостов/сервисов через ping
- Настраивается полностью через `.env`, без хардкода
- Готов к запуску как systemd-сервис

## Стек

Python 3.10+, aiogram 3.x, psutil, python-dotenv

## Установка

```bash
git clone <ссылка-на-репозиторий>
cd server-monitor-bot
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Заполните `.env`:
- `BOT_TOKEN` — получить у [@BotFather](https://t.me/BotFather)
- `CHAT_ID` — узнать через [@userinfobot](https://t.me/userinfobot) или API бота

## Запуск

```bash
python bot.py
```

## Запуск как systemd-сервис (Linux)

```bash
sudo cp server-monitor-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now server-monitor-bot
sudo systemctl status server-monitor-bot
```

## Архитектура

```
Telegram API <──polling──> bot.py ──> monitor.py (psutil, ping)
                              │
                              └──> alert_loop() — фоновая проверка порогов
```

## Безопасность

- Файл `.env` с реальным токеном добавлен в `.gitignore` — не коммитьте его в репозиторий.
- Токен бота даёт полный контроль над ботом — при компрометации сразу отзовите его через @BotFather (`/revoke`) и выпустите новый.

## Что можно добавить

- Хранение истории метрик (SQLite) и график за период
- Веб-дашборд (Flask/FastAPI)
- Docker-образ для развёртывания в один шаг
