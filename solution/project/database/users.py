from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql.sqltypes import Boolean, Text

from .conn import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(), nullable=False)

    login = Column(String(30), nullable=False, unique=True)
    email = Column(String(50), nullable=False)
    phone = Column(String(20))

    password_hash = Column(Text(), nullable=False)
    password_salt = Column(String(100), nullable=False)
    jwt_secret = Column(String(100))

    country_code = Column(String(2), nullable=False)
    is_public = Column(Boolean, nullable=False)
    image = Column(String(200))
