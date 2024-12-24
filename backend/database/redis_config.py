from typing import Optional
import redis
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

class RedisConfig:
    _instance: Optional[redis.Redis] = None

    @classmethod
    def get_client(cls) -> redis.Redis:
        if cls._instance is None:
            cls._instance = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=int(os.getenv('REDIS_DB', 0)),
                decode_responses=True  # 自动将字节解码为字符串
            )
        return cls._instance 