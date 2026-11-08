import hashlib
import hmac
import json
import time
from typing import Optional
from urllib.parse import parse_qsl


class AuthError(Exception):
    pass


def validate_init_data(
    init_data: str, bot_token: str, max_age: int = 86400, now: Optional[float] = None
) -> dict:
    fields = dict(parse_qsl(init_data, keep_blank_values=True))
    received = fields.pop("hash", None)
    if not received:
        raise AuthError("hash is missing")

    check_string = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    expected = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, received):
        raise AuthError("signature mismatch")

    if (time.time() if now is None else now) - int(fields.get("auth_date", "0")) > max_age:
        raise AuthError("init data expired")
    try:
        return json.loads(fields["user"])
    except (KeyError, ValueError):
        raise AuthError("user is missing") from None
