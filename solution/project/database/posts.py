import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, UUID, func
from sqlalchemy.sql.sqltypes import Boolean, Text

from .conn import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID, default=uuid.uuid4, primary_key=True)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)
    author = Column(Integer, ForeignKey("users.id"), nullable=False)

    content = Column(Text(), nullable=False)
    tags = Column(JSON, default=list, nullable=False)


class Reaction(Base):
    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(), server_default=func.now(), nullable=False)

    post = Column(UUID, ForeignKey("posts.id"), nullable=False)
    user = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_like = Column(Boolean, nullable=False)
