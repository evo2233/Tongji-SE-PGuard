from pydantic import BaseModel
from models.models import User
from typing import List


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


class LogDetail(BaseModel):
    logId: str
    timeStamp: str
    diseaseName: str
    content: str
    imagesURL: str


class PlotDetails(BaseModel):
    plotId: str
    plotName: str
    plantId: str
    plantName: str
    plantFeature: str
    plantIconURL: str
    logs: List[LogDetail]
