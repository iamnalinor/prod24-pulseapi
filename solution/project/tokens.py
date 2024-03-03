from datetime import datetime, timedelta
from typing import Annotated, cast

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from .database import User
from .env import TOKEN_TTL_HOURS
from .errors import assert401
from .misc import get_db


def issue_token(user_id: int, jwt_secret: str) -> str:
    deadline = datetime.now() + timedelta(hours=TOKEN_TTL_HOURS)
    encoded = jwt.encode(
        {"user_id": user_id, "exp": deadline},
        jwt_secret,
        algorithm="HS256",
    )
    return encoded


def resolve_token_into_user(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(OAuth2PasswordBearer("token", auto_error=False))],
) -> User:
    assert401(token)

    try:
        unsafe_data = jwt.decode(token, options={"verify_signature": False})
    except InvalidTokenError:
        return assert401(False)

    assert401("user_id" in unsafe_data)

    user = db.query(User).filter(User.id == unsafe_data["user_id"]).first()
    assert401(user)
    assert401(user.jwt_secret)

    try:
        data = jwt.decode(token, user.jwt_secret, algorithms=["HS256"])
    except InvalidTokenError:
        return assert401(False)

    assert data["user_id"] == user.id
    assert user is not None

    return cast(User, user)
