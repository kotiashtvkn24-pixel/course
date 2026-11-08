import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

BOT_TOKEN = "123456:TEST-TOKEN"


def make_init_data(user_id=1, first_name="Тарас", username="taras_k", auth_date=None, token=BOT_TOKEN):
    fields = {
        "auth_date": str(int(time.time()) if auth_date is None else auth_date),
        "user": json.dumps(
            {"id": user_id, "first_name": first_name, "username": username}, ensure_ascii=False
        ),
    }
    check = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    fields["hash"] = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    return urlencode(fields)
