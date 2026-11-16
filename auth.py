import hmac
import hashlib
import base64
import json
import time
from fastapi import Request, HTTPException, status
from app.config import SECRET_KEY, SESSION_COOKIE_NAME
from app.database import get_db, verify_password

TOKEN_EXPIRATION_SECONDS = 86400 * 7 # 7 days

def create_token(user_dict: dict) -> str:
    payload = {
        "id": user_dict["id"],
        "username": user_dict["username"],
        "email": user_dict["email"],
        "role": user_dict["role"],
        "full_name": user_dict["full_name"],
        "exp": int(time.time()) + TOKEN_EXPIRATION_SECONDS
    }
    payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode('utf-8').rstrip('=')
    signature = hmac.new(SECRET_KEY.encode('utf-8'), payload_b64.encode('utf-8'), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{signature}"

def decode_token(token: str) -> dict | None:
    try:
        if not token or "." not in token:
            return None
        payload_b64, signature = token.split(".", 1)
        expected_sig = hmac.new(SECRET_KEY.encode('utf-8'), payload_b64.encode('utf-8'), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_sig, signature):
            return None
        # Add padding back if needed
        padding = 4 - (len(payload_b64) % 4)
        if padding and padding != 4:
            payload_b64 += "=" * padding
        payload_bytes = base64.urlsafe_b64decode(payload_b64.encode('utf-8'))
        payload = json.loads(payload_bytes.decode('utf-8'))
        if payload.get("exp", 0) < int(time.time()):
            return None
        return payload
    except Exception:
        return None

def get_current_user_from_request(request: Request) -> dict | None:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
    if not token:
        return None
    payload = decode_token(token)
    if not payload:
        return None
    
    # Optionally verify existence in db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, role, full_name, phone, company FROM users WHERE id = ?", (payload["id"],))
    user = cursor.fetchone()
    conn.close()
    if not user:
        return None
    return dict(user)

def require_user(request: Request) -> dict:
    user = get_current_user_from_request(request)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return user

def require_admin(request: Request) -> dict:
    user = require_user(request)
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator privileges required")
    return user

def require_staff_or_admin(request: Request) -> dict:
    user = require_user(request)
    if user["role"] not in ("admin", "staff"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Staff or Administrator privileges required")
    return user
