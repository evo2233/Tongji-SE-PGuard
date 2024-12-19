from fastapi import APIRouter, Depends
from dependencies.auth import get_current_user
from models.models import User

user_api = APIRouter()

@user_api.get("/me")
async def get_crnt_user(current_user: User = Depends(get_current_user)):
    # 返回用户信息，排除密码字段
    return {
        "userId": str(current_user.userId),
        "userName": current_user.userName,
        "location": current_user.location,
        "sumCount": current_user.sumCount
    }
