import hashlib
import hmac
import os
import random
import secrets
from datetime import UTC, datetime, timedelta
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field


dotenv_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path)

router = APIRouter()

OTP_TTL_MINUTES = 10
OTP_STORE: dict[str, dict[str, object]] = {}


class RequestOtpPayload(BaseModel):
    user_name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class SignupPayload(BaseModel):
    user_name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    otp: str = Field(min_length=6, max_length=6)


class LoginPayload(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


def _database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD", "")

    if not all([host, name, user]):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not configured. Set DATABASE_URL or DB_* env vars.",
        )
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


def _ensure_users_table(cursor) -> None:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            user_name VARCHAR(50) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )


def _hash_password(password: str, salt: bytes | None = None) -> str:
    actual_salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), actual_salt, 120_000)
    return f"{actual_salt.hex()}:{digest.hex()}"


def _verify_password(password: str, encoded: str) -> bool:
    try:
        salt_hex, expected_hash = encoded.split(":")
        computed = _hash_password(password, bytes.fromhex(salt_hex)).split(":")[1]
        return hmac.compare_digest(computed, expected_hash)
    except (ValueError, TypeError):
        return False


@router.post("/request-otp")
def request_otp(payload: RequestOtpPayload) -> dict[str, object]:
    connection = psycopg2.connect(_database_url())
    try:
        with connection.cursor() as cursor:
            _ensure_users_table(cursor)
            cursor.execute("SELECT 1 FROM users WHERE email = %s", (payload.email.lower(),))
            if cursor.fetchone() is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already exists. Please login instead.",
                )
    except HTTPException:
        raise
    except psycopg2.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {exc}",
        ) from exc
    finally:
        connection.close()

    otp = f"{random.randint(0, 999999):06d}"
    expires_at = datetime.now(UTC) + timedelta(minutes=OTP_TTL_MINUTES)

    OTP_STORE[payload.email.lower()] = {
        "otp": otp,
        "expires_at": expires_at,
        "user_name": payload.user_name.strip(),
        "password_hash": _hash_password(payload.password),
    }

    # Frontend can send this OTP using EmailJS.
    return {
        "message": "OTP generated. Send it to user email with EmailJS and verify.",
        "otp": otp,
        "expires_in_minutes": OTP_TTL_MINUTES,
    }


@router.post("/signup")
def signup(payload: SignupPayload) -> dict[str, object]:
    key = payload.email.lower()
    otp_data = OTP_STORE.get(key)
    if otp_data is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP not requested for this email.",
        )

    if datetime.now(UTC) > otp_data["expires_at"]:
        OTP_STORE.pop(key, None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired. Request a new OTP.",
        )

    if str(otp_data["otp"]) != payload.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP.",
        )

    connection = psycopg2.connect(_database_url())
    connection.autocommit = False
    try:
        with connection.cursor() as cursor:
            _ensure_users_table(cursor)
            cursor.execute("SELECT user_id FROM users WHERE email = %s", (payload.email.lower(),))
            if cursor.fetchone() is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already exists.",
                )

            cursor.execute(
                """
                INSERT INTO users (user_name, email, password_hash)
                VALUES (%s, %s, %s)
                RETURNING user_id, user_name, email
                """,
                (
                    payload.user_name.strip(),
                    payload.email.lower(),
                    otp_data["password_hash"],
                ),
            )
            user_id, user_name, email = cursor.fetchone()
            connection.commit()
    except HTTPException:
        connection.rollback()
        raise
    except psycopg2.Error as exc:
        connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {exc}",
        ) from exc
    finally:
        connection.close()
        OTP_STORE.pop(key, None)

    return {
        "message": "Signup successful.",
        "user": {
            "user_id": user_id,
            "user_name": user_name,
            "email": email,
        },
    }

@router.post("/login")
def login(payload: LoginPayload) -> dict[str, object]:
    connection = psycopg2.connect(_database_url())
    try:
        with connection.cursor() as cursor:
            _ensure_users_table(cursor)
            cursor.execute(
                """
                SELECT 
                    u.user_id, 
                    u.user_name, 
                    u.email, 
                    u.password_hash, 
                    MAX(l.id) AS highest_level_completed
                FROM users u
                LEFT JOIN levelscompleted lc ON u.user_id = lc.user_id
                LEFT JOIN levels l ON lc.level_id = l.id AND l.main_level = 0
                WHERE u.email = %s
                GROUP BY u.user_id, u.user_name, u.email, u.password_hash
                """,
                (payload.email.lower(),),
            )
            row = cursor.fetchone()
            if row is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password.",
                )

            user_id, user_name, email, password_hash, highest_level_completed = row  # ← unpack all 5

            if not _verify_password(payload.password, password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password.",
                )

    except HTTPException:
        raise
    except psycopg2.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {exc}",
        ) from exc
    finally:
        connection.close()

    token = secrets.token_urlsafe(24)
    return {
        "message": "Login successful.",
        "token": token,
        "user": {
            "user_id": user_id,
            "user_name": user_name,
            "email": email,
            "highest_level_completed": highest_level_completed,  # now defined
        },
    }