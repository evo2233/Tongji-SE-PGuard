from fastapi import APIRouter, Depends

from core.dependency import get_current_user

from models.models import User

import service.log as lo

log_api = APIRouter()


@log_api.get('/summary')
async def get_summary(user: User = Depends(get_current_user)):
    return await lo.get_summary(user)
