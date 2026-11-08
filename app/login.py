import asyncio

from telethon import TelegramClient

from app.config import get_settings


async def main() -> None:
    settings = get_settings()
    async with TelegramClient(settings.session_path, settings.api_id, settings.api_hash) as client:
        me = await client.get_me()
        print(f"Вхід виконано: {me.first_name}. Сесію збережено.")


if __name__ == "__main__":
    asyncio.run(main())
