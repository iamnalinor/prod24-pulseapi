from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from ..database.users import User
from ..errors import assert403
from ..misc import app, get_db
from ..models.user import Profile
from ..tokens import resolve_token_into_user
from ..validations import validate_access


@app.get("/api/profiles/{login}")
def get_profile(
    login: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(resolve_token_into_user)],
):
    target_user = db.query(User).filter(User.login == login).one_or_none()
    assert403(target_user is not None)

    validate_access(db, user, target_user)

    return Profile.from_orm(target_user).as_json()
