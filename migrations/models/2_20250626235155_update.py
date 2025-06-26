from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `literatures` ADD `is_referenced_by_count` INT NOT NULL COMMENT '被引用次数' DEFAULT 0;
        ALTER TABLE `literatures` ADD `score` DOUBLE NOT NULL COMMENT 'Crossref评分' DEFAULT 0;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `literatures` DROP COLUMN `is_referenced_by_count`;
        ALTER TABLE `literatures` DROP COLUMN `score`;"""
