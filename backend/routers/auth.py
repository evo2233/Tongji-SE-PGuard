from datetime import timedelta
from fastapi import APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from models.models import User
from schemas.User import SignUpForm, SignInForm
from core.security import create_access_token, verify_password, get_password_hash

auth_api = APIRouter()

@auth_api.post("/register")
async def add_user(form: SignUpForm):
    try:
        # 先进行表单验证
        await form.name_must_be_unique(form.userName)
        
        # 创建新用户
        user = await User.create(
            userName=form.userName,
            password=get_password_hash(form.password),
            location=form.location,
            sumCount=0,
        )
        return {"message": "用户创建成功", "user_id": user.userId}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@auth_api.post("/token")
async def user_login(form: SignInForm):
    try:
        user = await User.get(userName=form.userName)
        if not user:
            raise HTTPException(status_code=400, detail="用户不存在")

        if not verify_password(form.password, user.password):
            raise HTTPException(status_code=400, detail="密码错误")
        
        # 生成令牌
        access_token_expires = timedelta(minutes=30)
        # 将 UUID 转换为字符串
        access_token = create_access_token(
            data={"sub": str(user.userId)}, expires_delta=access_token_expires
        )
        # 返回令牌
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
