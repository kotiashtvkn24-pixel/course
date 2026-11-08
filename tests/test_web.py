import time

import pytest
from fastapi.testclient import TestClient

from app.auth import AuthError, validate_init_data
from app.web import create_app
from tests.helpers import BOT_TOKEN, make_init_data

OWNER_ID = 1


@pytest.fixture
def client(greetings, factory):
    return TestClient(create_app(BOT_TOKEN, OWNER_ID, greetings, factory))


@pytest.fixture
def auth():
    return {"X-Init-Data": make_init_data(user_id=OWNER_ID)}


def test_valid_init_data_returns_user():
    assert validate_init_data(make_init_data(user_id=5), BOT_TOKEN)["id"] == 5


@pytest.mark.parametrize(
    "data",
    [
        make_init_data(token="999:OTHER"),
        make_init_data(auth_date=int(time.time()) - 10 * 86400),
        "auth_date=1&user=%7B%7D",
        "",
    ],
)
def test_bad_init_data_is_rejected(data):
    with pytest.raises(AuthError):
        validate_init_data(data, BOT_TOKEN)


def test_api_requires_auth(client):
    assert client.get("/api/greetings").status_code == 401


def test_only_owner_has_access(client):
    stranger = {"X-Init-Data": make_init_data(user_id=2)}
    assert client.get("/api/greetings", headers=stranger).status_code == 403


def test_greeting_lifecycle(client, auth):
    body = {
        "recipient": "@Oksana_1",
        "send_at": "2026-11-10T09:00",
        "style": "warm",
        "text": None,
        "repeat": True,
    }
    created = client.post("/api/greetings", json=body, headers=auth)
    assert created.status_code == 201
    assert created.json()["send_at"] == "2026-11-10T09:00"
    assert created.json()["status"] == "pending"

    data = client.get("/api/greetings", headers=auth).json()
    assert [i["recipient"] for i in data["items"]] == ["oksana_1"]
    assert len(data["styles"]) == 4

    gid = created.json()["id"]
    assert client.delete(f"/api/greetings/{gid}", headers=auth).status_code == 204
    assert client.delete(f"/api/greetings/{gid}", headers=auth).status_code == 404


@pytest.mark.parametrize(
    "body",
    [
        {"recipient": "oksana_1", "send_at": "2020-01-01T09:00", "style": "warm"},
        {"recipient": "bad name", "send_at": "2026-11-10T09:00", "style": "warm"},
        {"recipient": "oksana_1", "send_at": "2026-11-10T09:00", "style": "nope"},
    ],
)
def test_invalid_input_returns_400(client, auth, body):
    assert client.post("/api/greetings", json=body, headers=auth).status_code == 400


def test_preview_and_index(client, auth):
    preview = client.get("/api/preview", params={"style": "short"}, headers=auth).json()
    assert "друже" in preview["text"]
    assert client.get("/").status_code == 200
