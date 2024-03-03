import re
from datetime import datetime

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from ..database.countries import Country
from ..database.users import User
from ..errors import assert400, assert409
from ..misc import app, get_db
from ..models.user import UserModel, UserRegisterModel
from ..utils import hash_password, rand_string


@app.post("/api/auth/register")
def register_user(user: UserRegisterModel, db: Session = Depends(get_db)):
    assert400(re.fullmatch(r"[a-zA-Z0-9-]{1,30}", user.login), "invalid login")
    assert409(
        db.query(User).filter(User.login == user.login).first() is None,
        "login conflicts with another user",
    )

    assert400(
        user.email and len(user.email) <= 30 and "@" in user.email,
        "invalid email",
    )
    assert409(
        db.query(User).filter(User.email == user.email).first() is None,
        "email conflicts with another user",
    )

    assert400(len(user.password) >= 6, "password has less than 6 characters")
    for regex in [r"[0-9]", r"[A-Z]", r"[a-z]"]:
        assert400(re.search(regex, user.password), "password is weak")

    assert400(re.fullmatch(r"[a-zA-Z]{2}", user.countryCode), "invalid countryCode")
    assert400(
        db.query(Country).filter(Country.alpha2 == user.countryCode).first(),
        "countryCode not found",
    )

    # replace empty strings with None

    user.phone = user.phone or None
    if user.phone:
        assert400(re.fullmatch(r"\+\d{1,20}", user.phone), "invalid phone")
        assert409(
            db.query(User).filter(User.phone == user.phone).first() is None,
            "phone conflicts with another user",
        )

    user.image = user.image or None
    if user.image:
        assert400(1 <= len(user.image) <= 200, "invalid image")

    password_salt = rand_string()
    password_hash = hash_password(user.password, password_salt)

    user = User(
        created_at=datetime.now(),
        login=user.login,
        email=user.email,
        password_hash=password_hash,
        password_salt=password_salt,
        country_code=user.countryCode,
        is_public=user.isPublic,
        phone=user.phone,
        image=user.image,
    )
    db.add(user)
    db.commit()

    return JSONResponse(
        {"profile": UserModel.from_orm(user).as_json()}, status_code=201
    )
