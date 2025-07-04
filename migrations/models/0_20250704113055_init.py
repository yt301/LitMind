from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `literatures` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    `title` VARCHAR(255) NOT NULL COMMENT '文献标题',
    `author` VARCHAR(255) NOT NULL COMMENT '作者',
    `publication_date` DATE NOT NULL COMMENT '出版日期',
    `doi` VARCHAR(255) NOT NULL UNIQUE COMMENT '数字对象标识符（DOI）',
    `url` VARCHAR(255) NOT NULL COMMENT '文献链接',
    `reference_count` INT NOT NULL COMMENT '参考文献数量',
    `reference_doi` JSON NOT NULL COMMENT '参考文献的DOI列表',
    `is_referenced_by_count` INT NOT NULL COMMENT '被引用次数' DEFAULT 0,
    `score` DOUBLE NOT NULL COMMENT 'Crossref评分' DEFAULT 0,
    `theme_auto` VARCHAR(255) NOT NULL COMMENT '自动生成的主题标签'
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    `username` VARCHAR(255) NOT NULL UNIQUE COMMENT '用户名',
    `hashed_password` VARCHAR(128) NOT NULL,
    `email` VARCHAR(255) NOT NULL UNIQUE COMMENT '电子邮箱',
    `registration_date` DATETIME(6) NOT NULL COMMENT '注册时间' DEFAULT CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `files` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    `file_name` VARCHAR(255) NOT NULL COMMENT '文件名',
    `file_path` VARCHAR(255) NOT NULL COMMENT '文件存储路径',
    `file_size` INT NOT NULL COMMENT '文件大小（字节）',
    `file_type` VARCHAR(255) NOT NULL COMMENT '文件类型',
    `upload_time` DATETIME(6) NOT NULL COMMENT '上传时间' DEFAULT CURRENT_TIMESTAMP(6),
    `user_id` INT NOT NULL COMMENT '关联用户',
    CONSTRAINT `fk_files_users_de5c82ea` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `literature_user` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `theme_tags` JSON NOT NULL COMMENT '用户输入的主题标签列表',
    `literature_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    UNIQUE KEY `uid_literature__literat_85c007` (`literature_id`, `user_id`),
    CONSTRAINT `fk_literatu_literatu_58d1514b` FOREIGN KEY (`literature_id`) REFERENCES `literatures` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_literatu_users_bbd3f75c` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
