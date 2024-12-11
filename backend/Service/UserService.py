from Models.User import User
import uuid

from fastapi import APIRouter

user = APIRouter()

@user.get('/{id}')
async def get_user(id: uuid.UUID):
    return id