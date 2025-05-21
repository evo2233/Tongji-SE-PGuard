from fastapi import APIRouter, Depends
from core.auth import get_current_user
from entities.models import User
from service.logService import make_summarize

log_api = APIRouter()


@log_api.get('/summary')
async def get_summary(user: User = Depends(get_current_user)):
    await make_summarize(user)
