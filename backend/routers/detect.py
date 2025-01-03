from fastapi import APIRouter, UploadFile, Depends
from core.userController import get_current_user
from models.models import User

import core.detect as d

detect_api = APIRouter()


@detect_api.post("/plot/{plotId}/detect")
async def do_detect(
        plotId: str,
        file: UploadFile,
        user: User = Depends(get_current_user)
):
    return await d.do_detect(plotId, file, user)
