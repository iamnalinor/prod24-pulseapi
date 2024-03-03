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
from ..tokens import issue_token, resolve_token


class SignInModel(BaseModel):
    login: str
    password: str


@app.post("/api/auth/sign-in")
def register_user(sign_in: SignInModel, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.login == sign_in.login).first()
    assert400(user, "User not found")

    password_hash = hash_password(sign_in.password, user.password_salt)
    assert400(user.password_hash == password_hash, "Invalid password")

    if not user.jwt_secret:
        user.jwt_secret = rand_string()
        db.add(user)
        db.commit()

    token = issue_token(user.id, user.jwt_secret)

    assert resolve_token(db, token).id == user.id

    return {"token": token}
