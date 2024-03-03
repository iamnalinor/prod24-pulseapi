from .conn import Base, engine
from .countries import Country
from .users import User, Friendship
from .posts import Post, Reaction

Base.metadata.create_all(engine)
