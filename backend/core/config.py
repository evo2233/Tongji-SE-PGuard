import os
from typing import Set
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # bcrypt加密密码(不能解密)


if os.getenv("SECRET_KEY"):
    SECRET_KEY = os.getenv('SECRET_KEY')
else:
    raise ValueError("SECRET_KEY environment variable not set")
ALGORITHM = os.getenv('ALGORITHM')  # 加密算法


REFRESH_TOKEN_EXPIRE_DAYS = 30  # refresh token有效期30天


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/token")


# 允许的图片类型
ALLOWED_IMAGE_TYPES: Set[str] = {'.jpg', '.jpeg', '.png'}
# 获取项目根目录的resource文件夹路径
RESOURCE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resource")
# 确保resource目录存在
if not os.path.exists(RESOURCE_PATH):
    os.makedirs(RESOURCE_PATH)

# yolov8模型路径
ULTRALYTICS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "yolov8\\ultralytics-main")

# 按地块分类存放上传检测图片的文件夹
UPLOAD_PATH: str = os.path.join(RESOURCE_PATH, "log")
