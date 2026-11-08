import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Notification:
    message: str


class Observer(ABC):
    @abstractmethod
    async def notify(self, notification: Notification) -> None:
        ...


class EventBus:
    def __init__(self) -> None:
        self._observers: list[Observer] = []

    def subscribe(self, observer: Observer) -> None:
        self._observers.append(observer)

    async def publish(self, notification: Notification) -> None:
        for observer in self._observers:
            try:
                await observer.notify(notification)
            except Exception:
                log.exception("Observer %s failed", type(observer).__name__)
