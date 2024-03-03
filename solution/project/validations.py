import re

from sqlalchemy.orm import Session

from .database import Country, User
from .database.users import Friendship
from .errors import assert400, assert409, assert403


def validate_password(password: str):
    assert400(len(password) >= 6, "password has less than 6 characters")
    for regex in [r"[0-9]", r"[A-Z]", r"[a-z]"]:
        assert400(re.search(regex, password), "password is weak")


def validate_country_code(db: Session, country_code: str):
    assert400(re.fullmatch(r"[a-zA-Z]{2}", country_code), "invalid countryCode")
    assert400(
        db.query(Country).filter(Country.alpha2 == country_code).one_or_none(),
        "countryCode not found",
    )


def validate_phone(db: Session, phone: str):
    assert400(re.fullmatch(r"\+\d{1,20}", phone), "invalid phone")
    assert409(
        db.query(User).filter(User.phone == phone).one_or_none() is None,
        "phone conflicts with another user",
    )


def validate_image(image: str):
    assert400(1 <= len(image) <= 200, "invalid image")


def validate_access(db: Session, source: User, target: User):
    have_access = (
        target.id == source.id
        or target.is_public
        or (
            db.query(Friendship)
            .filter(Friendship.source == target.id, Friendship.target == source.id)
            .one_or_none()
            is not None
        )
    )
    assert403(have_access)
