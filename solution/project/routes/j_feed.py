from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from ..database import Post
from ..database.users import User, Friendship
from ..errors import assert403, assert404
from ..misc import app, get_db
from ..models.post import PostRendered
from ..models.user import Profile
from ..tokens import resolve_token_into_user
from ..validations import validate_access


@app.get("/api/posts/feed/my")
def get_my_posts(
    limit: int = 5,
    offset: int = 0,
    user: User = Depends(resolve_token_into_user),
    db: Session = Depends(get_db),
):
    posts = (
        db.query(Post).filter(Post.author == user.id).offset(offset).limit(limit).all()
    )
    # todo придумать что-то с join
    return [PostRendered.from_orm(post).as_json() for post in posts]


@app.get("/api/posts/feed/{login}")
def get_my_posts(
    login: str,
    limit: int = 5,
    offset: int = 0,
    user: User = Depends(resolve_token_into_user),
    db: Session = Depends(get_db),
):
    author = db.query(User).filter(User.login == login).one()
    validate_access(db, user, author, assert404)

    posts = (
        db.query(Post)
        .filter(Post.author == author.id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    # todo придумать что-то с join
    return [PostRendered.from_orm(post).as_json() for post in posts]
