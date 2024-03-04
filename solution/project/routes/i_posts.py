import uuid

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database.posts import Post
from ..database.users import User
from ..errors import assert404
from ..misc import app, get_db
from ..models.post import PostRendered
from ..tokens import resolve_token_into_user
from ..validations import validate_access


class NewPostModel(BaseModel):
    content: str
    tags: list[str]


@app.post("/api/posts/new")
def new_post(
    post: NewPostModel,
    user: User = Depends(resolve_token_into_user),
    db: Session = Depends(get_db),
):
    obj = Post(
        author=user.id,
        content=post.content,
        tags=post.tags,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)

    return PostRendered.from_orm(obj).as_json()


@app.get("/api/posts/{post_id}")
def view_post(
    post_id: str,
    user: User = Depends(resolve_token_into_user),
    db: Session = Depends(get_db),
):
    try:
        post_id = uuid.UUID(post_id)
    except ValueError:
        assert404(False)

    post, author = (
        db.query(Post, User)
        .join(User, Post.author == User.id)
        .filter(Post.id == post_id)
        .one()
    )

    validate_access(db, user, author, assert404)

    return PostRendered.from_orm(post).as_json()
