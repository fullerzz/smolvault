from functools import cached_property

import bcrypt
from pydantic import BaseModel, SecretStr, computed_field


class User(BaseModel):
    id: int
    username: str
    email: str | None = None
    full_name: str | None = None


class NewUserDTO(BaseModel):
    username: str
    email: str
    full_name: str
    password: SecretStr

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def hashed_password(self) -> str:
        return bcrypt.hashpw(self.password.get_secret_value().encode(), bcrypt.gensalt()).decode()


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
