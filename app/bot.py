import logging

from aiogram import Bot, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from app.events import Notification, Observer

log = logging.getLogger(__name__)


class TelegramNotifier(Observer):
    def __init__(self, bot: Bot, owner_id: int) -> None:
        self._bot = bot
        self._owner_id = owner_id

    async def notify(self, notification: Notification) -> None:
        try:
            await self._bot.send_message(self._owner_id, notification.message)
        except TelegramAPIError as exc:
            log.warning("Cannot notify owner: %s", exc)


def build_router(owner_id: int, webapp_url: str) -> Router:
    router = Router()

    @router.message(Command("id"))
    async def on_id(message: Message) -> None:
        await message.answer(f"Ваш Telegram ID: {message.from_user.id}")

    @router.message(CommandStart())
    async def on_start(message: Message) -> None:
        if message.from_user.id != owner_id:
            await message.answer("Це приватний бот.")
            return
        markup = None
        if webapp_url:
            button = InlineKeyboardButton(
                text="🎂 Запланувати привітання", web_app=WebAppInfo(url=webapp_url)
            )
            markup = InlineKeyboardMarkup(inline_keyboard=[[button]])
        await message.answer(
            "Відкрийте застосунок: вкажіть юзернейм, дату й час, "
            "і привітання піде з вашого акаунта.",
            reply_markup=markup,
        )

    return router
