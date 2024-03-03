from .conn import Base, engine
from .countries import Country
from .users import User

Base.metadata.create_all(engine)
