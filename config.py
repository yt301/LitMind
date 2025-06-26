# TORTOISE_ORM
CONFIG={
                'connections': {
                    'default': {
                        'engine': 'tortoise.backends.mysql',
                        'credentials': {
                            'host': 'localhost',
                            'port': '3306',
                            'user': 'root',
                            'password': 'zst12345',
                            'database': 'LitMind',
                        }
                    },
                },
                'apps': {
                    'models': {
                        'models': ['models.models',"aerich.models"],
                        'default_connection': 'default',
                    }
                }
            }