from app.events import EventBus, Notification, Observer

MESSAGE = Notification("hi")


class Broken(Observer):
    async def notify(self, notification):
        raise RuntimeError("boom")


async def test_every_observer_is_notified(recorder):
    second = type(recorder)()
    bus = EventBus()
    bus.subscribe(recorder)
    bus.subscribe(second)
    await bus.publish(MESSAGE)
    assert recorder.messages == ["hi"]
    assert second.messages == ["hi"]


async def test_failing_observer_does_not_stop_others(recorder):
    bus = EventBus()
    bus.subscribe(Broken())
    bus.subscribe(recorder)
    await bus.publish(MESSAGE)
    assert recorder.messages == ["hi"]
