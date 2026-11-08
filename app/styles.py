from abc import ABC, abstractmethod

from app.models import ValidationError


class Style(ABC):
    key: str
    title: str

    @abstractmethod
    def compose(self, name: str) -> str:
        ...


class Warm(Style):
    key = "warm"
    title = "Тепле"

    def compose(self, name: str) -> str:
        return f"{name}, з днем народження! Бажаю здоров'я, щастя і щоб усе вдавалося легко 🎂"


class Formal(Style):
    key = "formal"
    title = "Офіційне"

    def compose(self, name: str) -> str:
        return f"Шановний(-а) {name}! Щиро вітаю з днем народження. Зичу здоров'я та успіхів."


class Funny(Style):
    key = "funny"
    title = "Жартівливе"

    def compose(self, name: str) -> str:
        return f"{name}, з днем народження! Нехай гроші водяться, а дедлайни обходять стороною 🥳"


class Short(Style):
    key = "short"
    title = "Коротке"

    def compose(self, name: str) -> str:
        return f"🎉 {name}, з днем народження!"


class StyleFactory:
    def __init__(self, *styles: type[Style]) -> None:
        self._styles = {style.key: style for style in styles}

    def has(self, key: str) -> bool:
        return key in self._styles

    def create(self, key: str) -> Style:
        try:
            return self._styles[key]()
        except KeyError:
            raise ValidationError("Невідомий стиль привітання") from None

    def catalog(self) -> list[dict[str, str]]:
        return [{"key": k, "title": s.title} for k, s in self._styles.items()]


def default_factory() -> StyleFactory:
    return StyleFactory(Warm, Formal, Funny, Short)
