from abc import ABC, abstractmethod

from telethon import TelegramClient
from telethon.errors import RPCError


class SendError(Exception):
    pass


class Sender(ABC):
    @abstractmethod
    async def first_name(self, username: str) -> str: ...

    @abstractmethod
    async def send(self, username: str, text: str) -> None: ...


class TelethonSender(Sender):
    def __init__(self, client: TelegramClient) -> None:
        self._client = client

    async def first_name(self, username: str) -> str:
        try:
            entity = await self._client.get_entity(username)
        except (RPCError, ValueError) as exc:
            raise SendError(f"Користувача @{username} не знайдено") from exc
        return getattr(entity, "first_name", None) or username

    async def send(self, username: str, text: str) -> None:
        try:
            await self._client.send_message(username, text)
        except RPCError as exc:
            raise SendError(f"Telegram відхилив повідомлення ({type(exc).__name__})") from exc
