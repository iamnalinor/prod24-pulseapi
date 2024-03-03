from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database.users import User
from ..errors import assert403
from ..misc import app, get_db
from ..tokens import resolve_token_into_user
from ..utils import hash_password, rand_string
from ..validations import validate_password


class UpdatePasswordModel(BaseModel):
    oldPassword: str
    newPassword: str


@app.post("/api/me/updatePassword")
def update_password(
    update: UpdatePasswordModel,
    user: User = Depends(resolve_token_into_user),
    db: Session = Depends(get_db),
):
    password_hash = hash_password(update.oldPassword, user.password_salt)
    assert403(user.password_hash == password_hash, "Invalid password")

    validate_password(update.newPassword)

    user.password_salt = rand_string()
    user.password_hash = hash_password(update.newPassword, user.password_salt)
    user.jwt_secret = None

    db.add(user)
    db.commit()

    return {"status": "ok"}
