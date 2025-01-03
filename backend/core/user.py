from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, Body
from jose import jwt, JWTError

from database.redis_config import RedisConfig
from core.config import pwd_context, SECRET_KEY, ALGORITHM, REFRESH_TOKEN_EXPIRE_DAYS, oauth2_scheme

from schemas.form import SignUpForm, SignInForm
from models.models import User
from core.userController import get_current_user
from core.cityController import validate_location


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()  # 创建一个可修改的副本
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))  # 设置过期时间
    to_encode.update({"exp": expire})  # 添加到期时间到令牌数据
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # 使用密钥和算法生成 JWT


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def invalidate_token(token: str):
    """将token加入黑名单"""
    try:
        # 解析token获取过期时间
        payload = decode_token(token)
        exp = datetime.fromtimestamp(payload['exp'])
        # 计算剩余有效期
        ttl = (exp - datetime.utcnow()).total_seconds()
        if ttl > 0:
            # 使用RedisConfig获取redis客户端
            redis_client = RedisConfig.get_client()
            # 将token加入黑名单，并设置过期时间
            redis_client.setex(f"blacklist:{token}", int(ttl), "1")
    except Exception:
        pass


def is_token_blacklisted(token: str) -> bool:
    """检查token是否在黑名单中"""
    redis_client = RedisConfig.get_client()
    return bool(redis_client.get(f"blacklist:{token}"))


async def create_user(form: SignUpForm):
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


async def get_token(form: SignInForm):
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


async def refresh_token(current_token: str = Depends(oauth2_scheme), refresh_token: str = Body(...)):
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


async def get_user(current_user: User = Depends(get_current_user)):
    return {
        "userId": str(current_user.userId),
        "userName": current_user.userName,
        "location": current_user.location,
        "sumCount": current_user.sumCount
    }


async def update_user(form: SignUpForm, user: User = Depends(get_current_user)):
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


async def logout(current_token: str = Depends(oauth2_scheme)):
    if not is_token_blacklisted(current_token):
        invalidate_token(current_token)
        return {"登出成功"}
    else:
        raise HTTPException(status_code=401, detail="无效的access token")
