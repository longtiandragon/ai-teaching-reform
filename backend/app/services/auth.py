import base64
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Depends, Header, HTTPException

from backend.app.config import get_settings
from backend.app.services.database import get_user


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000)
    return f"pbkdf2_sha256${salt}${base64.urlsafe_b64encode(digest).decode('ascii')}"


def verify_password(password: str, stored: str | None) -> bool:
    if not stored:
        return False
    try:
        algorithm, salt, _digest = stored.split("$", 2)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    return hmac.compare_digest(hash_password(password, salt), stored)


def create_access_token(user: dict[str, Any]) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        "sub": user["id"],
        "role": user["role"],
        "name": user["name"],
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_expire_minutes)).timestamp()),
    }
    header = {"alg": "HS256", "typ": "JWT"}
    signing_input = f"{_b64_json(header)}.{_b64_json(payload)}"
    signature = hmac.new(
        settings.jwt_secret_key.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_b64(signature)}"


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}"
        expected = _b64(hmac.new(settings.jwt_secret_key.encode("utf-8"), signing_input.encode("ascii"), hashlib.sha256).digest())
        if not hmac.compare_digest(expected, signature_b64):
            raise ValueError("bad signature")
        payload = json.loads(_b64_decode(payload_b64).decode("utf-8"))
        if int(payload.get("exp", 0)) < int(datetime.now(UTC).timestamp()):
            raise ValueError("token expired")
        return payload
    except Exception as exc:
        raise HTTPException(status_code=401, detail="invalid or expired token") from exc


def current_user(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    payload = decode_access_token(authorization.split(" ", 1)[1].strip())
    row = get_user(str(payload["sub"]))
    if not row:
        raise HTTPException(status_code=401, detail="user not found")
    return dict(row)


def require_teacher(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    if user.get("role") != "teacher":
        raise HTTPException(status_code=403, detail="teacher role required")
    return user


def require_student(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    if user.get("role") != "student":
        raise HTTPException(status_code=403, detail="student role required")
    return user


def _b64_json(value: dict[str, Any]) -> str:
    return _b64(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64_decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
