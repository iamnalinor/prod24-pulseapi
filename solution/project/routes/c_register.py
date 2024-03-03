import re
from datetime import datetime

from fastapi import Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from ..database.users import User
from ..errors import assert400, assert409
from ..misc import app, get_db
from ..models.user import Profile, UserRegisterModel
from ..utils import hash_password, rand_string
from ..validations import validate_country_code, validate_image, validate_phone


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

    validate_country_code(db, user.countryCode)

    user.phone = user.phone or None
    if user.phone:
        validate_phone(db, user.phone)

    user.image = user.image or None
    if user.image:
        validate_image(user.image)

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

    return JSONResponse({"profile": Profile.from_orm(user).as_json()}, status_code=201)
