from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database.users import User
from ..misc import app, get_db
from ..models.user import Profile
from ..tokens import resolve_token_into_user
from ..validations import validate_country_code, validate_image, validate_phone


@app.get("/api/me/profile")
def get_profile(user: Annotated[User, Depends(resolve_token_into_user)]):
    return Profile.from_orm(user).as_json()


EMPTY = object()


class ProfileUpdateModel(BaseModel):
    countryCode: str | None = None
    isPublic: bool | None = None
    phone: str | None = EMPTY
    image: str | None = EMPTY


@app.patch("/api/me/profile")
def update_profile(
    update: ProfileUpdateModel,
    user: Annotated[User, Depends(resolve_token_into_user)],
    db: Session = Depends(get_db),
):
    if update.isPublic is not None:
        user.is_public = update.isPublic

    if update.countryCode:
        validate_country_code(db, update.countryCode)
        user.country_code = update.countryCode

    if update.phone != EMPTY and update.phone != user.phone:
        if update.phone:
            validate_phone(db, update.phone)
            user.phone = update.phone or None
        else:
            user.phone = None

    if update.image != EMPTY:
        if update.image:
            validate_image(update.image)
            user.image = update.image or None
        else:
            user.image = None

    db.add(user)
    db.commit()

    return Profile.from_orm(user).as_json()
