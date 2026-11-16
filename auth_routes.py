from fastapi import APIRouter, Request, Response, HTTPException, status
from pydantic import BaseModel
from datetime import datetime, timezone
from app.database import get_db, hash_password, verify_password
from app.auth import create_token, get_current_user_from_request
from app.config import SESSION_COOKIE_NAME

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username_or_email: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    phone: str = ""
    company: str = ""

@router.post("/login")
def login(req: LoginRequest, response: Response):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, username, email, password_hash, salt, role, full_name, phone, company
    FROM users 
    WHERE username = ? OR email = ?
    """, (req.username_or_email.strip(), req.username_or_email.strip()))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    if not verify_password(req.password, user["password_hash"], user["salt"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    user_dict = dict(user)
    token = create_token(user_dict)

    # Set secure cookie
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=86400 * 7,
        httponly=True,
        samesite="lax"
    )

    return {
        "success": True,
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "full_name": user["full_name"],
            "company": user["company"]
        }
    }

@router.post("/register")
def register(req: RegisterRequest, response: Response):
    conn = get_db()
    cursor = conn.cursor()

    # Check existing
    cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (req.username.strip(), req.email.strip()))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already in use")

    pw_hash, salt = hash_password(req.password)
    now = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
    INSERT INTO users (username, email, password_hash, salt, role, full_name, phone, company, created_at)
    VALUES (?, ?, ?, ?, 'customer', ?, ?, ?, ?)
    """, (req.username.strip(), req.email.strip(), pw_hash, salt, req.full_name.strip(), req.phone.strip(), req.company.strip(), now))
    
    new_id = cursor.lastrowid
    conn.commit()

    user_dict = {
        "id": new_id,
        "username": req.username.strip(),
        "email": req.email.strip(),
        "role": "customer",
        "full_name": req.full_name.strip(),
        "company": req.company.strip()
    }
    conn.close()

    token = create_token(user_dict)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=86400 * 7,
        httponly=True,
        samesite="lax"
    )

    return {"success": True, "token": token, "user": user_dict}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(SESSION_COOKIE_NAME)
    return {"success": True, "message": "Successfully logged out"}

@router.get("/me")
def get_me(request: Request):
    user = get_current_user_from_request(request)
    if not user:
        return {"authenticated": False, "user": None}
    return {
        "authenticated": True,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "full_name": user["full_name"],
            "phone": user["phone"],
            "company": user["company"]
        }
    }
