from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from database.redis_config import RedisConfig

# 仅用于开发环境加载.env
load_dotenv()

if os.getenv("SECRET_KEY"):
    SECRET_KEY = os.getenv('SECRET_KEY')
else:
    raise ValueError("SECRET_KEY environment variable not set")
ALGORITHM = os.getenv('ALGORITHM')  # 加密算法
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 令牌有效期
REFRESH_TOKEN_EXPIRE_DAYS = 30  # refresh token有效期30天

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # bcrypt加密密码(不能解密)


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
