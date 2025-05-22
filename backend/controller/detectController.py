from fastapi import APIRouter, UploadFile, Depends
from core.auth import get_current_user
from models.models import User
from service.detectService import do_detect

detect_api = APIRouter()


@detect_api.post("/plot/{plotId}/detect")
async def detect(
        plotId: str,
        file: UploadFile,
        user: User = Depends(get_current_user)
):
    return await do_detect(plotId, file, user)
