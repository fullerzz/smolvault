from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


def decode_token(token: str) -> User:
    return User(
        username="fakeuser",
        email="fake@email.com",
        full_name="Fake User",
    )


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    user = decode_token(token)
    return user
