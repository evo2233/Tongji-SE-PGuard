from fastapi import FastAPI, Request, Response
from tortoise.contrib.fastapi import register_tortoise
from config import TORTOISE_ORM

from UserService import user

app = FastAPI()

app.include_router(user, prefix="/user", tags=["UserService"])

register_tortoise(
    app=app,
    config=TORTOISE_ORM,
)