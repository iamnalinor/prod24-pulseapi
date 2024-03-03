import datetime
import uuid

from pydantic import BaseModel

from ..database import User
from ..database.posts import Post, Reaction
from ..misc import get_db
from ..utils import format_datetime


class PostRendered(BaseModel):
    id: uuid.UUID
    content: str
    author: str
    tags: list[str]
    createdAt: datetime.datetime
    likesCount: int
    dislikesCount: int

    @classmethod
    def from_orm(cls, obj: Post) -> "PostRendered":
        db = next(get_db())

        author = db.query(User.login).filter(User.id == obj.author).scalar()
        likes = (
            db.query(Reaction).filter(Reaction.post == obj.id, Reaction.is_like).count()
        )
        dislikes = (
            db.query(Reaction)
            .filter(Reaction.post == obj.id, ~Reaction.is_like)
            .count()
        )

        return cls(
            id=obj.id,
            content=obj.content,
            author=author,
            tags=obj.tags,
            createdAt=obj.created_at,
            likesCount=likes,
            dislikesCount=dislikes,
        )

    def as_json(self):
        json = self.dict()
        json["createdAt"] = format_datetime(json["createdAt"])
        return json
