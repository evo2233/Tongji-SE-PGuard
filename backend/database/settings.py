from dotenv import load_dotenv
import os

load_dotenv()

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
