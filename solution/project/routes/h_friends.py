from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database.users import User, Friendship
from ..misc import app, get_db
from ..tokens import resolve_token_into_user
from ..utils import format_datetime


class LoginModel(BaseModel):
    login: str


@app.post("/api/friends/add")
async def add_friend(
    login: LoginModel,
    user: User = Depends(resolve_token_into_user),
    db: Session = Depends(get_db),
):
    if user.login != login.login:
        target = db.query(User).filter(User.login == login.login).one()

        if (
            not db.query(Friendship)
            .filter(Friendship.source == user.id, Friendship.target == target.id)
            .first()
        ):
            db.add(
                Friendship(
                    source=user.id,
                    target=target.id,
                )
            )
            db.commit()

    return {"status": "ok"}


@app.post("/api/friends/remove")
async def remove_friend(
    login: LoginModel,
    user: User = Depends(resolve_token_into_user),
    db: Session = Depends(get_db),
):
    if user.login != login.login:
        target = db.query(User).filter(User.login == login.login).one_or_none()

        if target:
            db.query(Friendship).filter(
                Friendship.source == user.id, Friendship.target == target.id
            ).delete()
            db.commit()

    return {"status": "ok"}


@app.get("/api/friends")
async def get_friends(
    limit: int = 5,
    offset: int = 0,
    user: User = Depends(resolve_token_into_user),
    db: Session = Depends(get_db),
):
    friends = (
        db.query(User.login, Friendship.created_at)
        .filter(Friendship.source == user.id)
        .join(User, Friendship.target == User.id)
        .order_by(Friendship.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        {
            "login": login,
            "addedAt": format_datetime(created_at),
        }
        for login, created_at in friends
    ]
