import uuid
from fastapi import APIRouter, Depends, HTTPException, Body
from dependencies.auth import get_current_user, oauth2_scheme
from models.models import User, Package
from schemas.form import SignUpForm, SignInForm
import core.security as core
from datetime import timedelta
from jose import JWTError
from typing import List

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
async def refresh_token(current_token: str = Depends(oauth2_scheme), refresh_token: str = Body(...)):
    try:
        # 验证refresh token
        payload = core.decode_token(refresh_token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="无效的refresh token")

        # 验证access token(登录状态)
        if not core.is_token_blacklisted(current_token):
            # 将当前的access token加入黑名单
            core.invalidate_token(current_token)

            # 生成新的access token
            access_token_expires = timedelta(minutes=30)
            access_token = core.create_access_token(
                data={"sub": user_id}, expires_delta=access_token_expires)

            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
        else:
            raise HTTPException(status_code=401, detail="无效的access token")
    except JWTError:
        raise HTTPException(status_code=401, detail="无效的refresh token")


@user_api.get("/me")
async def get_user(current_user: User = Depends(get_current_user)):
    return {
        "userId": str(current_user.userId),
        "userName": current_user.userName,
        "location": current_user.location,
        "sumCount": current_user.sumCount
    }


@user_api.patch("/update")
async def update_user(form: SignUpForm, user: User = Depends(get_current_user)):
    user.userName = form.userName
    user.password = core.get_password_hash(form.password)
    user.location = form.location
    await user.save()
    return {
        "userId": str(user.userId),
        "userName": user.userName,
        "password": form.password,  # 加密算法不可解密
        "location": user.location,
    }


@user_api.post("/logout")
async def logout(current_token: str = Depends(oauth2_scheme)):
    if not core.is_token_blacklisted(current_token):
        core.invalidate_token(current_token)
        return {"登出成功"}
    else:
        raise HTTPException(status_code=401, detail="无效的access token")


@user_api.get('/package', response_model=List[dict])
async def get_all_packages():
    try:
        packages = await Package.all()
        return [
            {
                "packageId": str(package.packageId),
                "packageName": package.packageName,
                "price": package.price,
                "sumNum": package.sumNum
            }
            for package in packages
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取套餐列表失败: {str(e)}")


@user_api.post("/recharge/{package_id}")
async def purchase(package_id: str, user: User = Depends(get_current_user)):
    try:
        package = await Package.get(packageId=uuid.UUID(package_id))
        user.sumCount += package.sumNum
        await user.save()
        return {"packageId": package_id, "sumCount": user.sumCount}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
