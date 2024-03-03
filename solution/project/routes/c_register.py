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
from ..utils import hash_password, rand_string


class RegisterModel(BaseModel):
    login: str
    email: str
    password: str
    countryCode: str
    isPublic: bool
    phone: str | None = None
    image: str | None = None


@app.post("/api/auth/register")
def register_user(register: RegisterModel, db: Session = Depends(get_db)):
    assert400(re.fullmatch(r"[a-zA-Z0-9-]{1,30}", register.login), "invalid login")
    assert409(
        db.query(User).filter(User.login == register.login).first() is None,
        "login conflicts with another user",
    )

    assert400(
        register.email and len(register.email) <= 30 and "@" in register.email,
        "invalid email",
    )
    assert409(
        db.query(User).filter(User.email == register.email).first() is None,
        "email conflicts with another user",
    )

    assert400(len(register.password) >= 6, "password has less than 6 characters")
    for regex in [r"[0-9]", r"[A-Z]", r"[a-z]"]:
        assert400(re.search(regex, register.password), "password is weak")

    assert400(re.fullmatch(r"[a-zA-Z]{2}", register.countryCode), "invalid countryCode")
    assert400(
        db.query(Country).filter(Country.alpha2 == register.countryCode).first(),
        "countryCode not found",
    )

    # replace empty strings with None
    register.phone = register.phone or None
    if register.phone:
        assert400(re.fullmatch(r"\+\d{1,20}", register.phone), "invalid phone")
        assert409(
            db.query(User).filter(User.phone == register.phone).first() is None,
            "phone conflicts with another user",
        )

    register.image = register.image or None
    if register.image:
        assert400(1 <= len(register.image) <= 200, "invalid image")

    password_salt = rand_string()
    password_hash = hash_password(register.password, password_salt)

    user = User(
        created_at=datetime.now(),
        login=register.login,
        email=register.email,
        password_hash=password_hash,
        password_salt=password_salt,
        country_code=register.countryCode,
        is_public=register.isPublic,
        phone=register.phone,
        image=register.image,
    )
    db.add(user)
    db.commit()

    profile = {
        "login": user.login,
        "email": user.email,
        "countryCode": user.country_code,
        "isPublic": user.is_public,
    }
    if user.phone:
        profile["phone"] = user.phone
    if user.image:
        profile["image"] = user.image

    return JSONResponse({"profile": profile}, status_code=201)
