from datetime import date

from pydantic import BaseModel, EmailStr, field_validator

from models import User


class UserLoginIn(BaseModel):
    username: str = None
    password: str
    email: str = None  # 使用 EmailStr 类型自动校验邮箱

class UserRegisterIn(BaseModel):
    username: str = None
    password: str
    email: EmailStr = None  # 使用 EmailStr 类型自动校验邮箱
    # 校验器
    @field_validator("username")
    @classmethod
    def check_username(cls, value: str):
        assert len(value) >= 4, "用户名至少为4位"
        return value

    # 校验器
    @field_validator("password")
    @classmethod
    def check_password(cls, value: str):
        assert len(value) > 6, "密码长度必须大于6"
        assert any(c.isalpha() for c in value), "密码必须包含字母"
        assert any(c.isdigit() for c in value), "密码必须包含数字"
        return value


class LiteratureIn(BaseModel):
    title: str
    id: int = None  # 文献ID可选，用于更新时传入
    author: str
    publication_date: date
    doi: str
    url: str
    reference_count: int
    reference_doi: list[str] = []  # 参考文献的DOI列表，默认为空列表
