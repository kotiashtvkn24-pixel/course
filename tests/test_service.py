from datetime import datetime, timedelta

import pytest

from app.models import ValidationError

WHEN = datetime(2026, 11, 10, 9, 0)


def test_add_normalizes_and_stores(greetings):
    created = greetings.add(" @Oksana_1 ", WHEN, "warm")
    assert created.recipient == "oksana_1"
    assert greetings.list_all()[0].send_at == WHEN


def test_add_ignores_timezone_info(greetings):
    from datetime import timezone

    created = greetings.add("oksana", WHEN.replace(tzinfo=timezone.utc), "warm")
    assert created.send_at.tzinfo is None


@pytest.mark.parametrize(
    "kwargs",
    [
        {"recipient": "bad name"},
        {"send_at": datetime(2026, 11, 7, 12, 0)},
        {"send_at": datetime(2020, 1, 1)},
        {"style": "nope"},
        {"text": "x" * 1001},
    ],
)
def test_add_validation(greetings, kwargs):
    params = {"recipient": "oksana", "send_at": WHEN, "style": "warm"}
    params.update(kwargs)
    with pytest.raises(ValidationError):
        greetings.add(**params)


def test_blank_text_is_treated_as_missing(greetings):
    assert greetings.add("oksana", WHEN, "warm", "   ").text is None


def test_remove(greetings):
    created = greetings.add("oksana", WHEN, "warm")
    assert greetings.remove(created.id) is True
    assert greetings.remove(created.id) is False


async def test_nothing_is_sent_before_the_time(greetings, sender, clock):
    greetings.add("oksana", WHEN, "warm")
    clock.now = WHEN - timedelta(minutes=1)
    assert await greetings.send_due() == 0
    assert sender.sent == []


async def test_style_text_uses_recipient_first_name(greetings, sender, clock, recorder):
    greetings.add("oksana", WHEN, "short")
    clock.now = WHEN
    assert await greetings.send_due() == 1
    username, text = sender.sent[0]
    assert username == "oksana"
    assert "Оксана" in text
    assert greetings.list_all()[0].status == "sent"
    assert "надіслано" in recorder.messages[0]


async def test_custom_text_is_sent_verbatim(greetings, sender, clock):
    greetings.add("oksana", WHEN, "warm", "Мій власний текст")
    clock.now = WHEN
    await greetings.send_due()
    assert sender.sent == [("oksana", "Мій власний текст")]


async def test_sent_greeting_is_not_resent(greetings, sender, clock):
    greetings.add("oksana", WHEN, "warm")
    clock.now = WHEN
    await greetings.send_due()
    assert await greetings.send_due() == 0
    assert len(sender.sent) == 1


async def test_repeating_greeting_is_rescheduled(greetings, sender, clock):
    greetings.add("oksana", WHEN, "warm", repeat=True)
    clock.now = WHEN
    await greetings.send_due()
    item = greetings.list_all()[0]
    assert item.status == "pending"
    assert item.send_at == datetime(2027, 11, 10, 9, 0)
    assert await greetings.send_due() == 0


async def test_failure_is_recorded_and_reported_once(greetings, sender, clock, recorder):
    greetings.add("oksana", WHEN, "warm")
    sender.failure = "Користувача @oksana не знайдено"
    clock.now = WHEN
    await greetings.send_due()
    item = greetings.list_all()[0]
    assert (item.status, item.error) == ("failed", "Користувача @oksana не знайдено")
    assert "Не вдалося" in recorder.messages[0]
    assert await greetings.send_due() == 0
    assert len(recorder.messages) == 1


async def test_several_due_greetings_are_all_sent(greetings, sender, clock):
    greetings.add("oksana", WHEN, "warm")
    greetings.add("ivan_k", WHEN, "funny")
    clock.now = WHEN
    assert await greetings.send_due() == 2
    assert {u for u, _ in sender.sent} == {"oksana", "ivan_k"}
