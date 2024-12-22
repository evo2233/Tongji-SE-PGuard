from fastapi import APIRouter, Depends, HTTPException
from dependencies.auth import get_current_user
from models.models import User
from schemas.User import SignUpForm, SignInForm
import core.security as core
from datetime import timedelta
from jose import JWTError

user_api = APIRouter()


@user_api.post("/signup")
async def create_user(form: SignUpForm):
    try:
        # 先进行表单验证
        await form.name_must_be_unique(form.userName)

        # 创建新用户
        user = await User.create(
            userName=form.userName,
            password=core.get_password_hash(form.password),
            location=form.location,
            sumCount=0,
        )
        return {"message": "用户创建成功", "user_id": user.userId}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@user_api.post("/signin")
async def get_token(form: SignInForm):
    try:
        user = await User.get(userName=form.userName)
        if not user:
            raise HTTPException(status_code=400, detail="用户不存在")

        if not core.verify_password(form.password, user.password):
            raise HTTPException(status_code=400, detail="密码错误")

        # 生成access token
        access_token_expires = timedelta(minutes=30)
        access_token = core.create_access_token(
            data={"sub": str(user.userId)}, expires_delta=access_token_expires
        )

        # 生成refresh token
        refresh_token = core.create_refresh_token(
            data={"sub": str(user.userId)}
        )

        # 返回两个令牌
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@user_api.post("/refresh")
async def refresh_token(refresh_token: str):
    try:
        # 验证refresh token
        payload = core.decode_token(refresh_token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="无效的refresh token")

        # 生成新的access token
        access_token_expires = timedelta(minutes=30)
        access_token = core.create_access_token(
            data={"sub": user_id}, expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="无效的refresh token")


@user_api.get("/me")
async def get_crnt_user(current_user: User = Depends(get_current_user)):
    return {
        "userId": str(current_user.userId),
        "userName": current_user.userName,
        "location": current_user.location,
        "sumCount": current_user.sumCount
    }


@user_api.patch("/update")
async def update_user(form: SignUpForm, user: User = Depends(get_current_user)):
    user.userName = form.userName
    user.password = core.get_password_hash(form.password),
    user.location = form.location
    await user.save()
    return {
        "userId": str(user.userId),
        "userName": user.userName,
        "password": form.password,  # 加密算法不可解密
        "location": user.location,
    }


"""如何logout：在前端删除access_token和refresh_token"""


