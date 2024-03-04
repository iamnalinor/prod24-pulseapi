import uuid

from fastapi import Depends
from sqlalchemy.orm import Session

from ..database import Post, Reaction
from ..database.users import User
from ..errors import assert404
from ..misc import app, get_db
from ..models.post import PostRendered
from ..tokens import resolve_token_into_user
from ..validations import validate_access


@app.post("/api/posts/{post_id}/{action}")
def react_on_post(
    post_id: uuid.UUID,
    action: str,
    user: User = Depends(resolve_token_into_user),
    db: Session = Depends(get_db),
):
    assert404(action in ["like", "dislike"], "Invalid action")

    post, author = (
        db.query(Post, User)
        .join(User, Post.author == User.id)
        .filter(Post.id == post_id)
        .one()
    )

    validate_access(db, user, author)

    db.query(Reaction).filter(
        Reaction.post == post_id, Reaction.user == user.id
    ).delete()
    db.add(
        Reaction(
            post=post_id,
            user=user.id,
            is_like=(action == "like"),
        )
    )
    db.commit()

    return PostRendered.from_orm(post).as_json()
