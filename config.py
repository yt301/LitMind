# TORTOISE_ORM配置
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

# 用户上传文件路径
FILE_PATH=fr'D:\Desktop\Qizhenwenzhi_Competition\LitMind\upload_files'

# 知识库路径
KNOWLEDGE_BASE_PATH=fr'D:\Desktop\Qizhenwenzhi_Competition\LitMind\knowledge_base'

# 向量存储路径（向量知识库）
VECTOR_STORE_PATH=fr'D:\Desktop\Qizhenwenzhi_Competition\LitMind\vectorstore'
