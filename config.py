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

FILE_PATH=fr'D:\Desktop\启真问智比赛\LitMind\upload_files'