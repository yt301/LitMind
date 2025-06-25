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
    `reference_doi` JSON NOT NULL COMMENT '参考文献的DOI列表'
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    `username` VARCHAR(255) NOT NULL UNIQUE COMMENT '用户名',
    `password` VARCHAR(255) NOT NULL COMMENT '密码',
    `email` VARCHAR(255) NOT NULL UNIQUE COMMENT '电子邮箱',
    `registration_date` DATETIME(6) NOT NULL COMMENT '注册时间' DEFAULT CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `files` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    `file_name` VARCHAR(255) NOT NULL COMMENT '文件名',
    `file_path` VARCHAR(255) NOT NULL COMMENT '文件存储路径',
    `file_size` INT NOT NULL COMMENT '文件大小（字节）',
    `upload_time` DATETIME(6) NOT NULL COMMENT '上传时间' DEFAULT CURRENT_TIMESTAMP(6),
    `user_id` INT NOT NULL COMMENT '关联用户',
    CONSTRAINT `fk_files_users_de5c82ea` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `pictures` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    `picture_path` VARCHAR(255) NOT NULL COMMENT '图片存储路径',
    `picture_time` DATETIME(6) NOT NULL COMMENT '图片生成时间' DEFAULT CURRENT_TIMESTAMP(6),
    `user_id` INT NOT NULL COMMENT '关联用户',
    CONSTRAINT `fk_pictures_users_06a5cbbf` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `translations` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    `file_path` VARCHAR(255) NOT NULL COMMENT '翻译文件存储路径',
    `source_language` VARCHAR(50) NOT NULL COMMENT '源语言',
    `target_language` VARCHAR(50) NOT NULL COMMENT '目标语言',
    `translation_time` DATETIME(6) NOT NULL COMMENT '翻译时间' DEFAULT CURRENT_TIMESTAMP(6),
    `style` VARCHAR(50) COMMENT '翻译风格',
    `user_id` INT NOT NULL COMMENT '关联用户',
    CONSTRAINT `fk_translat_users_8ece0596` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `literatures_users` (
    `literatures_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    FOREIGN KEY (`literatures_id`) REFERENCES `literatures` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uidx_literatures_literat_111485` (`literatures_id`, `user_id`)
) CHARACTER SET utf8mb4 COMMENT='关联用户';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
