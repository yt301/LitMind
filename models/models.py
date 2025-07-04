from tortoise.models import Model  # Tortoise ORM 框架
from tortoise import fields
from tools import *
from pydantic import EmailStr

# 用户模型定义
class User(Model):
    id = fields.IntField(pk=True, description='主键')
    username = fields.CharField(max_length=255, unique=True, description='用户名')
    hashed_password = fields.CharField(max_length=128)  # 存储哈希值而非明文
    email = fields.CharField(max_length=255, unique=True, description='电子邮箱')
    registration_date = fields.DatetimeField(auto_now_add=True, description='注册时间')

    def verify_password(self, password: str):
        return verify_password(password, self.hashed_password)

    @classmethod
    async def create_user(cls, username: str, password: str, email: EmailStr):
        return await cls.create(
            username=username,
            email=email,
            hashed_password=get_password_hash(password)  # 自动哈希
        )

    class Meta:
        table = 'users'  # 显式指定表名
        description = '用户表'

# 文献记录模型定义
class Literature(Model):
    id = fields.IntField(pk=True, description='主键')
    title = fields.CharField(max_length=255, description='文献标题')
    author = fields.CharField(max_length=255, description='作者')
    publication_date = fields.DateField(description='出版日期')
    doi = fields.CharField(max_length=255, unique=True, description='数字对象标识符（DOI）')
    url = fields.CharField(max_length=255, description='文献链接')
    reference_count = fields.IntField(description='参考文献数量')
    reference_doi = fields.JSONField(default=list, description='参考文献的DOI列表')
    is_referenced_by_count = fields.IntField(default=0, description='被引用次数')
    score = fields.FloatField(default=0.0, description='Crossref评分')
    theme_auto = fields.CharField(max_length=255, description='自动生成的主题标签')  # 主题标签

    # 多对多关系，关联用户
    # users = fields.ManyToManyField('models.User', through='literature_user',through_fields=('literature', 'user'), related_name='literatures', description='关联用户')
    users = fields.ManyToManyField(
        'models.User',
        through='literature_user',  # 中间表的表名
        # through_fields=('literature', 'user'),  # 明确指定中间表里两个外键字段的名称，顺序是 ('指向当前模型的外键字段名', '指向关联模型的外键字段名')
        forward_key='literature_id',  # 显式指定 Literature 的外键列名
        backward_key='user_id',       # 显式指定 User 的外键列名
        related_name='literatures',
        description='关联用户'
    )

    class Meta:
        table = 'literatures'
        description = '文献记录表'

# 文献与用户的多对多关系模型定义
class LiteratureUser(Model):
    literature = fields.ForeignKeyField('models.Literature')
    user = fields.ForeignKeyField('models.User')
    theme_tags = fields.JSONField(default=list,description='用户输入的主题标签列表')  # 使用 JSONField 存储列表

    class Meta:
        table = 'literature_user'
        unique_together = (('literature', 'user'),)  # 确保联合唯一


# 图片记录模型定义
# class Picture(Model):
#     id = fields.IntField(pk=True, description='主键')
#     picture_path = fields.CharField(max_length=255, description='图片存储路径')
#     picture_time = fields.DatetimeField(auto_now_add=True, description='图片生成时间')
#     # 一对多
#     user = fields.ForeignKeyField('models.User', related_name='pictures', description='关联用户')
#
#     class Meta:
#         table = 'pictures'
#         description = '图片记录表'


# 上传文件记录模型定义
class File(Model):
    id = fields.IntField(pk=True, description='主键')
    file_name = fields.CharField(max_length=255, description='文件名')
    file_path = fields.CharField(max_length=255, description='文件存储路径')
    file_size = fields.IntField(description='文件大小（字节）')
    file_type = fields.CharField(max_length=255, description='文件类型')
    upload_time = fields.DatetimeField(auto_now_add=True, description='上传时间')  # 自动赋值
    # 一对多
    user = fields.ForeignKeyField('models.User', related_name='files', description='关联用户')

    class Meta:
        table = 'files'
        description = '上传文件记录表'


# 翻译文件记录模型定义
# class Translation(Model):
#     id = fields.IntField(pk=True, description='主键')
#     file_name = fields.CharField(max_length=255, description='文件名')
#     file_path = fields.CharField(max_length=255, description='翻译文件存储路径')
#     file_size = fields.IntField(description='文件大小（字节）')
#     file_type = fields.CharField(max_length=255, description='文件类型')
#     source_language = fields.CharField(max_length=50, description='源语言')
#     translated_language = fields.CharField(max_length=50, description='翻译文件语言')
#     translation_time = fields.DatetimeField(auto_now_add=True, description='翻译时间')
#     style = fields.CharField(max_length=50, description='翻译风格', null=True, default=None)
#     # 一对多
#     user = fields.ForeignKeyField('models.User', related_name='translations', description='关联用户')
#
#     class Meta:
#         table = 'translations'
#         description = '翻译文件记录表'

# 迁移命令：aerich init -t config.CONFIG
# 初始化数据库：aerich init-db
# 添加迁移命令:aerich migrate
# 应用迁移命令：aerich upgrade
# 撤回应用的迁移命令：aerich downgrade
# 查看迁移历史：aerich history
