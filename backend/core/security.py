from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

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
