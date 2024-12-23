from pydantic import BaseModel
from models.models import User


class SignUpForm(BaseModel):
    userName: str
    password: str
    location: str

    @classmethod
    async def name_must_be_unique(cls, username: str):
        if await User.filter(userName=username).exists():
            raise ValueError('用户名已存在')
        return username


class SignInForm(BaseModel):
    userName: str
    password: str
