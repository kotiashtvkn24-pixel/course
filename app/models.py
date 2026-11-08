import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

_USERNAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]{4,31}$")


class ValidationError(ValueError):
    pass


@dataclass
class Greeting:
    recipient: str
    send_at: datetime
    style: str = "warm"
    text: Optional[str] = None
    repeat: bool = False
    status: str = "pending"
    error: Optional[str] = None
    id: Optional[int] = None


def normalize_username(value: str) -> str:
    cleaned = value.strip().lstrip("@")
    if not _USERNAME.match(cleaned):
        raise ValidationError("Некоректний юзернейм")
    return cleaned.lower()


def next_year(moment: datetime) -> datetime:
    try:
        return moment.replace(year=moment.year + 1)
    except ValueError:
        return moment.replace(year=moment.year + 1, day=28)
