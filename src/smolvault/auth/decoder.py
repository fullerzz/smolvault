from datetime import datetime, timedelta
from typing import Annotated, Any
from zoneinfo import ZoneInfo

import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError

from smolvault.auth.models import Token, TokenData, User
from smolvault.clients.database import DatabaseClient, UserInfo
from smolvault.config import get_settings

settings = get_settings()
SECRET_KEY = settings.auth_secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def decode_token(token: str, db_client: DatabaseClient) -> UserInfo | None:
    user = db_client.get_user(token)
    return user


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> Token:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(ZoneInfo("UTC")) + expires_delta
    else:
        expire = datetime.now(ZoneInfo("UTC")) + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)  # type: ignore
    return Token(access_token=encoded_jwt, token_type="bearer")  # noqa: S106


def authenticate_user(db_client: DatabaseClient, username: str, password: str) -> UserInfo | None:
    user = db_client.get_user(username)
    if not user:
        return None
    if not bcrypt.checkpw(password.encode(), user.hashed_password.encode()):
        return None
    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db_client: Annotated[DatabaseClient, Depends(DatabaseClient)],
) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError as e:
        raise credentials_exception from e
    if token_data.username is None:
        raise credentials_exception
    user = db_client.get_user(token_data.username)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.id is None:
        raise HTTPException(
            status_code=500,
            detail="Corrputed user data",
        )
    return User(id=user.id, username=user.username, email=user.email, full_name=user.full_name)
