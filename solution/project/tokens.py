from datetime import datetime, timedelta
from typing import cast

import jwt
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from .database import User
from .env import TOKEN_TTL_HOURS
from .errors import assert401


def issue_token(user_id: int, jwt_secret: str) -> str:
    deadline = datetime.now() + timedelta(hours=TOKEN_TTL_HOURS)
    encoded = jwt.encode(
        {"user_id": user_id, "exp": deadline},
        jwt_secret,
        algorithm="HS256",
    )
    return encoded


def resolve_token(db: Session, token: str) -> User:
    unsafe_data = jwt.decode(token, options={"verify_signature": False})
    assert401("user_id" in unsafe_data)

    user = db.query(User).filter(User.id == unsafe_data["user_id"]).first()
    assert401(user)

    try:
        data = jwt.decode(token, user.jwt_secret, algorithms=["HS256"])
    except InvalidTokenError:
        return assert401(False)

    assert data["user_id"] == user.id
    assert user is not None

    return cast(User, user)
