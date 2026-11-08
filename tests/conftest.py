from datetime import datetime

import pytest

from app.events import EventBus, Notification, Observer
from app.sender import Sender, SendError
from app.service import GreetingService
from app.storage import SqliteGreetingRepository, connect
from app.styles import default_factory

START = datetime(2026, 11, 7, 12, 0)


class FakeSender(Sender):
    def __init__(self):
        self.sent: list[tuple[str, str]] = []
        self.failure: str | None = None

    async def first_name(self, username):
        if self.failure:
            raise SendError(self.failure)
        return "Оксана"

    async def send(self, username, text):
        if self.failure:
            raise SendError(self.failure)
        self.sent.append((username, text))


class Recorder(Observer):
    def __init__(self):
        self.messages: list[str] = []

    async def notify(self, notification: Notification):
        self.messages.append(notification.message)


class Clock:
    def __init__(self):
        self.now = START

    def __call__(self):
        return self.now


@pytest.fixture
def conn():
    connection = connect(":memory:")
    yield connection
    connection.close()


@pytest.fixture
def repo(conn):
    return SqliteGreetingRepository(conn)


@pytest.fixture
def factory():
    return default_factory()


@pytest.fixture
def sender():
    return FakeSender()


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def recorder():
    return Recorder()


@pytest.fixture
def greetings(repo, factory, sender, clock, recorder):
    bus = EventBus()
    bus.subscribe(recorder)
    return GreetingService(repo, factory, sender, bus, clock, pause=0)
