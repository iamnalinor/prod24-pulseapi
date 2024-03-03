from pydantic import BaseModel

from ..database import User


class UserModel(BaseModel):
    login: str
    email: str
    countryCode: str
    isPublic: bool
    phone: str | None = None
    image: str | None = None

    @classmethod
    def from_orm(cls, obj: User) -> "UserModel":
        return cls(
            login=obj.login,
            email=obj.email,
            countryCode=obj.country_code,
            isPublic=obj.is_public,
            phone=obj.phone,
            image=obj.image,
        )

    def as_json(self):
        return self.dict(exclude_none=True)


class UserRegisterModel(UserModel):
    password: str
