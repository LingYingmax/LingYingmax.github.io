import base64
import binascii
import hashlib
import hmac
import json
import time

from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings


bearer_scheme = HTTPBearer(auto_error=False)


def _encode_part(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _decode_part(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def create_access_token(username: str, role: str) -> str:
    header = _encode_part(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    payload = _encode_part(
        json.dumps(
            {
                "sub": username,
                "role": role,
                "exp": int(time.time()) + settings.access_token_expire_minutes * 60,
            },
            separators=(",", ":"),
        ).encode()
    )
    message = f"{header}.{payload}".encode("ascii")
    signature = hmac.new(settings.jwt_secret.encode(), message, hashlib.sha256).digest()
    return f"{header}.{payload}.{_encode_part(signature)}"


def authenticate(username: str, password: str) -> str | None:
    if hmac.compare_digest(username, settings.admin_username) and hmac.compare_digest(password, settings.admin_password):
        return "admin"
    if hmac.compare_digest(username, settings.user_username) and hmac.compare_digest(password, settings.user_password):
        return "user"
    return None


def decode_token(credentials: HTTPAuthorizationCredentials | None) -> dict[str, object]:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized

    try:
        header, payload, signature = credentials.credentials.split(".")
        header_data = json.loads(_decode_part(header))
        if header_data.get("alg") != "HS256" or header_data.get("typ") != "JWT":
            raise unauthorized
        message = f"{header}.{payload}".encode("ascii")
        expected = hmac.new(settings.jwt_secret.encode(), message, hashlib.sha256).digest()
        if not hmac.compare_digest(_decode_part(signature), expected):
            raise unauthorized
        data = json.loads(_decode_part(payload))
        if int(data["exp"]) <= int(time.time()) or not data["sub"] or data["role"] not in {"admin", "user"}:
            raise unauthorized
        return data
    except (ValueError, KeyError, TypeError, binascii.Error, json.JSONDecodeError, UnicodeDecodeError):
        raise unauthorized


def require_admin(
    credentials: HTTPAuthorizationCredentials | None,
) -> str:
    data = decode_token(credentials)
    if data["role"] != "admin" or data["sub"] != settings.admin_username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="administrator role required")
    return str(data["sub"])


def require_user(credentials: HTTPAuthorizationCredentials | None) -> str:
    data = decode_token(credentials)
    return str(data["sub"])
