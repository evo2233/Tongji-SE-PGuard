from fastapi import Depends, HTTPException
from datetime import datetime, timedelta
from jose import jwt
from database.redis_config import RedisConfig

from core.config import SECRET_KEY, ALGORITHM, REFRESH_TOKEN_EXPIRE_DAYS, oauth2_scheme
from core.dependency import get_current_user
from models.models import User


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


async def logout(current_token: str = Depends(oauth2_scheme)):
    if not is_token_blacklisted(current_token):
        invalidate_token(current_token)
        return {"登出成功"}
    else:
        raise HTTPException(status_code=401, detail="无效的access token")


async def minus_sum_count(user: User = Depends(get_current_user)):
    if user.sumCount > 0:
        user.sumCount -= 1
        await user.save()
        return True
    else:
        return False
