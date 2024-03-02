from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from ..env import POSTGRES_CONN

engine = create_engine(POSTGRES_CONN)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
