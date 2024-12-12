TORTOISE_ORM = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'host': '113.44.76.249',
                'port': 5432,
                'user': 'postgres',
                'password': 'Yuki1_127',
                'database': 'PGuard',
                'minsize': 1,
                'maxsize': 3,
            }
        }
    },
    'apps': {
        'models': {
            'models': ['Models.models', 'aerich.models'],
            'default_connection': 'default',
        }
    },
    'use_tz': False,
    'timezone': 'Asia/Shanghai',
}
