from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.auth import AuthError, validate_init_data
from app.models import Greeting, ValidationError
from app.service import GreetingService
from app.styles import StyleFactory

WEBAPP_DIR = Path(__file__).resolve().parent.parent / "webapp"


class GreetingIn(BaseModel):
    recipient: str
    send_at: datetime
    style: str
    text: Optional[str] = None
    repeat: bool = False


def _view(greeting: Greeting) -> dict:
    return {
        "id": greeting.id,
        "recipient": greeting.recipient,
        "send_at": greeting.send_at.isoformat(timespec="minutes"),
        "repeat": greeting.repeat,
        "status": greeting.status,
        "error": greeting.error,
    }


def create_app(
    bot_token: str, owner_id: int, greetings: GreetingService, factory: StyleFactory
) -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None)
    app.mount("/static", StaticFiles(directory=WEBAPP_DIR), name="static")

    @app.exception_handler(ValidationError)
    async def bad_request(_, exc: ValidationError):
        return JSONResponse({"detail": str(exc)}, status_code=400)

    async def owner_only(x_init_data: str = Header("")) -> None:
        try:
            tg_user = validate_init_data(x_init_data, bot_token)
        except AuthError:
            raise HTTPException(401, "unauthorized") from None
        if tg_user["id"] != owner_id:
            raise HTTPException(403, "forbidden")

    @app.get("/")
    async def index():
        return FileResponse(WEBAPP_DIR / "index.html")

    @app.get("/api/greetings", dependencies=[Depends(owner_only)])
    async def list_greetings():
        return {"styles": factory.catalog(), "items": [_view(g) for g in greetings.list_all()]}

    @app.post("/api/greetings", status_code=201, dependencies=[Depends(owner_only)])
    async def add_greeting(body: GreetingIn):
        created = greetings.add(body.recipient, body.send_at, body.style, body.text, body.repeat)
        return _view(created)

    @app.delete("/api/greetings/{greeting_id}", status_code=204, dependencies=[Depends(owner_only)])
    async def delete_greeting(greeting_id: int):
        if not greetings.remove(greeting_id):
            raise HTTPException(404, "not found")

    @app.get("/api/preview", dependencies=[Depends(owner_only)])
    async def preview(style: str):
        return {"text": factory.create(style).compose("друже")}

    return app
