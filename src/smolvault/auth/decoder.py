from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from smolvault.auth.models import User
from smolvault.clients.database import DatabaseClient, UserInfo

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def decode_token(token: str, db_client: DatabaseClient) -> UserInfo | None:
    user = db_client.get_user(token)
    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db_client: Annotated[DatabaseClient, Depends(DatabaseClient)]
) -> User:
    user = decode_token(token, db_client)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return User(username=user.username, email=user.email, full_name=user.full_name)
