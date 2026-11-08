
import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import uvicorn
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telethon import TelegramClient

from app.bot import TelegramNotifier, build_router
from app.config import get_settings
from app.events import EventBus
from app.sender import TelethonSender
from app.service import GreetingService
from app.storage import SqliteGreetingRepository, connect
from app.styles import default_factory
from app.web import create_app


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    settings = get_settings()
    tz = ZoneInfo("Europe/Kyiv")

    def now() -> datetime:
        return datetime.now(tz).replace(tzinfo=None, microsecond=0)

    client = TelegramClient(
        settings.session_path,
        settings.api_id,
        settings.api_hash
    )

    await client.connect()

    if not await client.is_user_authorized():
        raise SystemExit(
            "Акаунт не авторизовано. Спершу виконайте: python -m app.login"
        )

    bot = Bot(settings.bot_token)
    bus = EventBus()
    bus.subscribe(TelegramNotifier(bot, settings.owner_id))

    factory = default_factory()
    repo = SqliteGreetingRepository(connect(settings.db_path))

    greetings = GreetingService(
        repo,
        factory,
        TelethonSender(client),
        bus,
        now
    )

    dispatcher = Dispatcher()
    dispatcher.include_router(
        build_router(settings.owner_id, settings.webapp_url)
    )

    scheduler = AsyncIOScheduler(timezone=tz)
    scheduler.add_job(
        greetings.send_due,
        "interval",
        seconds=30
    )
    scheduler.start()

    api = create_app(
        settings.bot_token,
        settings.owner_id,
        greetings,
        factory
    )

    server = uvicorn.Server(
        uvicorn.Config(
            api,
            host=settings.host,
            port=settings.port
        )
    )

    try:
        await asyncio.gather(
            dispatcher.start_polling(bot),
            server.serve()
        )
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
