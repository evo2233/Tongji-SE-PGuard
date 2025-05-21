import uuid
from datetime import timedelta

from fastapi import Depends, HTTPException
from jose import JWTError

from core.config import validate_location
from core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token, \
    is_token_blacklisted, invalidate_token
from core.auth import get_current_user
from models.models import User, City, Package


async def minus_sum_count(user: User = Depends(get_current_user)):
    if user.sumCount > 0:
        user.sumCount -= 1
        await user.save()
        return True
    else:
        return False


async def get_city(keyword):
    """根据关键字搜索城市"""
    try:
        cities = await City.filter(cityName__contains=keyword).all()
        if not cities:
            return {"message": "未找到匹配的城市"}
        return [
            {
                "cityName": city.cityName,
                "cityCode": city.cityCode
            }
            for city in cities
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索城市失败: {str(e)}")


async def get_city_code(user):
    try:
        city = await City.get(cityName=user.location)
        if not city:
            return {"message": "未找到匹配的城市"}
        return {
            "cityName": city.cityName,
            "cityCode": city.cityCode
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取城市码失败: {str(e)}")


async def add_user(form):
    try:
        # 先进行表单验证
        await form.name_must_be_unique(form.userName)
        await validate_location(form.location)

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


async def generate_token(form):
    try:
        user = await User.get(userName=form.userName)
        if not user:
            raise HTTPException(status_code=400, detail="用户不存在")

        if not verify_password(form.password, user.password):
            raise HTTPException(status_code=400, detail="密码错误")

        # 生成access token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": str(user.userId)}, expires_delta=access_token_expires
        )

        # 生成refresh token
        refresh_token = create_refresh_token(
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


async def renew_token(current_token, refresh_token):
    try:
        # 验证refresh token
        payload = decode_token(refresh_token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="无效的refresh token")

        # 验证access token(登录状态)
        if not is_token_blacklisted(current_token):
            # 将当前的access token加入黑名单
            invalidate_token(current_token)

            # 生成新的access token
            access_token_expires = timedelta(minutes=30)
            access_token = create_access_token(
                data={"sub": user_id}, expires_delta=access_token_expires)

            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
        else:
            raise HTTPException(status_code=401, detail="无效的access token")
    except JWTError:
        raise HTTPException(status_code=401, detail="无效的refresh token")


async def change_user_info(form, user):
    try:
        await validate_location(form.location)

        user.userName = form.userName
        user.password = get_password_hash(form.password)
        user.location = form.location
        await user.save()
        return {
            "userId": str(user.userId),
            "userName": user.userName,
            "location": user.location,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def black_token(current_token):
    if not is_token_blacklisted(current_token):
        invalidate_token(current_token)
        return {"登出成功"}
    else:
        raise HTTPException(status_code=401, detail="无效的access token")


async def all_package():
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


async def buy_package(package_id, user):
    try:
        package = await Package.get(packageId=uuid.UUID(package_id))
        user.sumCount += package.sumNum
        await user.save()
        return {"packageId": package_id, "sumCount": user.sumCount}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
