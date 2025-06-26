from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `files` ADD `file_type` VARCHAR(255) NOT NULL COMMENT '文件类型';
        ALTER TABLE `translations` ADD `file_size` INT NOT NULL COMMENT '文件大小（字节）';
        ALTER TABLE `translations` ADD `file_name` VARCHAR(255) NOT NULL COMMENT '文件名';
        ALTER TABLE `translations` ADD `file_type` VARCHAR(255) NOT NULL COMMENT '文件类型';
        ALTER TABLE `translations` ADD `translated_language` VARCHAR(50) NOT NULL COMMENT '翻译文件语言';
        ALTER TABLE `translations` DROP COLUMN `target_language`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `files` DROP COLUMN `file_type`;
        ALTER TABLE `translations` ADD `target_language` VARCHAR(50) NOT NULL COMMENT '目标语言';
        ALTER TABLE `translations` DROP COLUMN `file_size`;
        ALTER TABLE `translations` DROP COLUMN `file_name`;
        ALTER TABLE `translations` DROP COLUMN `file_type`;
        ALTER TABLE `translations` DROP COLUMN `translated_language`;"""
