# Планувальник привітань (Telegram-бот + мініап)

Бот відкриває мініап: ви вводите юзернейм, дату й час, обираєте стиль (або пишете свій текст),
і в цей момент привітання надсилається з вашого особистого акаунта. Опція «щороку» автоматично
переносить відправку на наступний рік. Про результат бот повідомляє вам у чаті.

## Запуск

1. Токен бота від @BotFather.
2. `API_ID` та `API_HASH`: my.telegram.org, розділ API development tools.
3. Ваш Telegram ID: надішліть боту `/id`.
4. `pip install -r requirements.txt`, потім `cp .env.example .env` і заповніть значення.
5. Один раз увійдіть в акаунт: `python -m app.login` (номер, код, за потреби пароль).
6. Публічна HTTPS-адреса для мініапу: `cloudflared tunnel --url http://localhost:8000`, її в `WEBAPP_URL`.
7. `python -m app.main`

Файл `*.session` дає повний доступ до акаунта: не публікуйте його й не комітьте в репозиторій.

## Тести

```bash
pytest --cov=app
```

## Архітектура

| Шар | Файли |
|-----|-------|
| Model | `models.py`, `styles.py`, `events.py`, `sender.py`, `service.py`, `storage.py` |
| View | `webapp/` |
| Controller | `web.py` (REST API), `bot.py` (команди бота) |

Патерни: Strategy і Factory (`styles.py`), Observer (`events.py`), Repository (`storage.py`).
Відправник (`sender.py`) прихований за інтерфейсом `Sender`, тому в тестах підставляється заглушка.
Діаграма класів: `docs/class_diagram.puml`.
