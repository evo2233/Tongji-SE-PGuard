import os
from dotenv import load_dotenv

load_dotenv()

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# 将项目根目录添加到 Python 路径
import sys
sys.path.append(BASE_DIR)

TORTOISE_ORM = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'host': os.getenv('DB_HOST'),
                'port': 5432,
                'user': 'postgres',
                'password': os.getenv('DB_PWD'),
                'database': 'PGuard',
                'minsize': 1,
                'maxsize': 3,
            }
        }
    },
    'apps': {
        'models': {
            'models': ['models.models', 'aerich.models'],
            'default_connection': 'default',
        }
    },
    'use_tz': False,
    'timezone': 'Asia/Shanghai',
}
