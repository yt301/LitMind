from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` ADD `hashed_password` VARCHAR(128) NOT NULL;
        ALTER TABLE `users` DROP COLUMN `password`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `users` ADD `password` VARCHAR(255) NOT NULL COMMENT '密码';
        ALTER TABLE `users` DROP COLUMN `hashed_password`;"""
