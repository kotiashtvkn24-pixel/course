
import asyncio
from datetime import datetime
from typing import Callable, Optional
from zoneinfo import ZoneInfo

from app.events import EventBus, Notification
from app.models import Greeting, ValidationError, next_year, normalize_username
from app.sender import Sender, SendError
from app.storage import GreetingRepository
from app.styles import StyleFactory

MAX_TEXT_LENGTH = 1000
KYIV = ZoneInfo("Europe/Kyiv")


class GreetingService:
    def __init__(
        self,
        repo: GreetingRepository,
        factory: StyleFactory,
        sender: Sender,
        bus: EventBus,
        clock: Callable[[], datetime],
        pause: float = 3.0,
    ) -> None:
        self._repo = repo
        self._factory = factory
        self._sender = sender
        self._bus = bus
        self._clock = clock
        self._pause = pause

    def add(
        self,
        recipient: str,
        send_at: datetime,
        style: str,
        text: Optional[str] = None,
        repeat: bool = False,
    ) -> Greeting:
        handle = normalize_username(recipient)

        if send_at.tzinfo is not None:
            send_at = send_at.astimezone(KYIV)

        send_at = send_at.replace(
            tzinfo=None,
            microsecond=0
        )

        if send_at <= self._clock():
            raise ValidationError("Час відправки має бути в майбутньому")

        if not self._factory.has(style):
            raise ValidationError("Невідомий стиль привітання")

        text = (text or "").strip() or None

        if text and len(text) > MAX_TEXT_LENGTH:
            raise ValidationError("Текст задовгий")

        return self._repo.add(
            Greeting(handle, send_at, style, text, repeat)
        )

    def list_all(self) -> list[Greeting]:
        return self._repo.list_all()

    def remove(self, greeting_id: int) -> bool:
        return self._repo.delete(greeting_id)

    async def send_due(self) -> int:
        due = self._repo.due(self._clock())

        for index, greeting in enumerate(due):
            if index:
                await asyncio.sleep(self._pause)

            await self._deliver(greeting)

        return len(due)

    async def _deliver(self, greeting: Greeting) -> None:
        try:
            name = await self._sender.first_name(greeting.recipient)

            text = (
                greeting.text
                or self._factory.create(greeting.style).compose(name)
            )

            await self._sender.send(greeting.recipient, text)

        except SendError as exc:
            greeting.status = "failed"
            greeting.error = str(exc)

            message = (
                f"⚠️ Не вдалося надіслати @{greeting.recipient}: {exc}"
            )

        else:
            if greeting.repeat:
                greeting.send_at = next_year(greeting.send_at)
            else:
                greeting.status = "sent"

            message = (
                f"✅ Привітання для @{greeting.recipient} надіслано"
            )

        self._repo.update(greeting)
        await self._bus.publish(Notification(message))
