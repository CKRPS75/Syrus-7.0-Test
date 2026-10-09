import base64
import binascii
import hashlib
import hmac
import logging
import os
import re
import secrets
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Annotated, Iterator

from fastapi import APIRouter, Cookie, HTTPException, Response, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)

SESSION_COOKIE = "trustroute_session"
SESSION_DURATION = timedelta(hours=12)
REMEMBERED_SESSION_DURATION = timedelta(days=30)
PASSWORD_ITERATIONS = 600_000
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = Field(default=False, alias="rememberMe")


class RegistrationRequest(BaseModel):
    full_name: str = Field(alias="fullName")
    email: str
    password: str


class PasswordResetRequest(BaseModel):
    email: str


class UserResponse(BaseModel):
    name: str
    email: str


class AuthResponse(BaseModel):
    user: UserResponse


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS)
    return "pbkdf2_sha256${}${}${}".format(
        PASSWORD_ITERATIONS,
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations_text, salt_text, digest_text = encoded.split("$")
        iterations = int(iterations_text)
        if algorithm != "pbkdf2_sha256" or not 100_000 <= iterations <= 1_000_000:
            return False
        salt = base64.urlsafe_b64decode(salt_text.encode("ascii"))
        expected = base64.urlsafe_b64decode(digest_text.encode("ascii"))
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError, binascii.Error):
        return False


_DUMMY_PASSWORD_HASH = hash_password("not-a-real-password")


def normalized_email(email: str) -> str:
    return email.strip().lower()


def validate_email(email: str) -> None:
    if len(email) > 254 or not EMAIL_PATTERN.fullmatch(email):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Enter a valid email address.")


def validate_password(password: str) -> None:
    if len(password) < 8 or len(password) > 128 or not re.search(r"[a-z]", password, re.IGNORECASE) or not re.search(r"\d", password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Use at least 8 characters, including a letter and a number.",
        )


@contextmanager
def get_connection() -> Iterator[object]:
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AUTH_DATABASE_NOT_CONFIGURED")
    try:
        import psycopg
    except ImportError as error:
        logger.exception("The PostgreSQL driver is not installed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AUTH_DATABASE_DRIVER_UNAVAILABLE",
        ) from error

    connection = None
    try:
        connection = psycopg.connect(database_url)
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS trustroute_users (
                id TEXT PRIMARY KEY,
                full_name VARCHAR(120) NOT NULL,
                email VARCHAR(254) NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS trustroute_sessions (
                token_hash TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES trustroute_users(id) ON DELETE CASCADE,
                expires_at TIMESTAMPTZ NOT NULL
            )
            """
        )
        yield connection
        connection.commit()
    except psycopg.Error as error:
        if connection is not None:
            connection.rollback()
        logger.exception("Could not connect to the authentication database")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AUTH_DATABASE_UNAVAILABLE",
        ) from error
    except Exception:
        if connection is not None:
            connection.rollback()
        raise
    finally:
        if connection is not None:
            connection.close()


def session_cookie_settings(remember_me: bool) -> dict:
    settings = {
        "key": SESSION_COOKIE,
        "httponly": True,
        "secure": os.getenv("ENVIRONMENT", "development").lower() == "production",
        "samesite": "lax",
        "path": "/",
    }
    if remember_me:
        settings["max_age"] = int(REMEMBERED_SESSION_DURATION.total_seconds())
    return settings


def session_token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def user_for_session(connection, token: str | None):
    if not token:
        return None
    result = connection.execute(
        """
        SELECT users.id, users.full_name, users.email
        FROM trustroute_sessions AS sessions
        JOIN trustroute_users AS users ON users.id = sessions.user_id
        WHERE sessions.token_hash = %s AND sessions.expires_at > NOW()
        """,
        (session_token_hash(token),),
    ).fetchone()
    return result


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegistrationRequest):
    full_name = payload.full_name.strip()
    email = normalized_email(payload.email)
    if not 2 <= len(full_name) <= 120:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Enter your full name.")
    validate_email(email)
    validate_password(payload.password)

    user_id = secrets.token_urlsafe(18)
    try:
        with get_connection() as connection:
            created = connection.execute(
                """
                INSERT INTO trustroute_users (id, full_name, email, password_hash)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (email) DO NOTHING
                RETURNING id
                """,
                (user_id, full_name, email, hash_password(payload.password)),
            ).fetchone()
            if not created:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="ACCOUNT_ALREADY_EXISTS")
    except HTTPException:
        raise
    return {"message": "Account created. You can now sign in."}


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, response: Response):
    email = normalized_email(payload.email)
    validate_email(email)
    if not payload.password:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Enter your password.")

    try:
        with get_connection() as connection:
            user = connection.execute(
                "SELECT id, full_name, email, password_hash FROM trustroute_users WHERE email = %s",
                (email,),
            ).fetchone()
            password_hash = user[3] if user else _DUMMY_PASSWORD_HASH
            if not verify_password(payload.password, password_hash) or not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="INVALID_CREDENTIALS",
                )

            remember_me = payload.remember_me
            token = secrets.token_urlsafe(32)
            duration = REMEMBERED_SESSION_DURATION if remember_me else SESSION_DURATION
            expires_at = datetime.now(timezone.utc) + duration
            connection.execute(
                "INSERT INTO trustroute_sessions (token_hash, user_id, expires_at) VALUES (%s, %s, %s)",
                (session_token_hash(token), user[0], expires_at),
            )
    except HTTPException:
        raise

    response.set_cookie(value=token, **session_cookie_settings(remember_me))
    return {"user": {"name": user[1], "email": user[2]}}


@router.get("/me", response_model=AuthResponse)
def get_current_user(
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None,
):
    try:
        with get_connection() as connection:
            user = user_for_session(connection, session_token)
            if not user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="SESSION_EXPIRED")
            return {"user": {"name": user[1], "email": user[2]}}
    except HTTPException:
        raise


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    session_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None,
):
    try:
        if session_token:
            with get_connection() as connection:
                connection.execute(
                    "DELETE FROM trustroute_sessions WHERE token_hash = %s",
                    (session_token_hash(session_token),),
                )
    except HTTPException:
        raise

    response.delete_cookie(
        key=SESSION_COOKIE,
        httponly=True,
        secure=os.getenv("ENVIRONMENT", "development").lower() == "production",
        samesite="lax",
        path="/",
    )
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.post("/reset")
def reset_password(_payload: PasswordResetRequest):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="PASSWORD_RESET_EMAIL_NOT_CONFIGURED",
    )
