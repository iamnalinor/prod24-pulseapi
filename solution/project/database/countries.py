from sqlalchemy import Column, Integer, Text

from .conn import Base


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    alpha2 = Column(Text)
    alpha3 = Column(Text)
    region = Column(Text)
