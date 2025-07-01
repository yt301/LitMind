from langchain.agents import tool
from pydantic import BaseModel, Field
from typing import Optional, Any, Self
from pydantic import field_validator
from enum import Enum

class TranslateInput(BaseModel):
    text: str = Field(default="请输入文本", description="待翻译的文本")
    source_language: str = Field(default="Chinese", description="源语言代码（如 'Chinese'）")
    translated_language: str = Field(default="English", description="目标语言代码（如 'English'）")
    style: str = Field(default="general", description="翻译风格: general/academic/literary")

class SummaryInput(BaseModel):
    text: str = Field(description="待总结的文献内容")
    language: str = Field(default="Chinese", description="总结输出语言(Chinese/English)")
    detail_level: str = Field(default="standard", description="总结详细程度(brief/standard/detailed)")

# 定义排序方式的枚举
class SortMethod(str, Enum):
    RELEVANCE = "relevance"  # 相关性排序（默认）
    SCORE = "score"  # 按Crossref评分排序
    UPDATED = "updated"  # 按更新时间排序
    CITATIONS = "is-referenced-by-count"  # 按被引用次数排序

class SearchInput(BaseModel):
    query: str = Field(description="搜索关键词")
    rows: int = Field(3, description="返回结果数量(1-10)")
    filter: Optional[str] = Field(None, description="过滤条件字符串")
    sort: SortMethod = Field(
        default=SortMethod.RELEVANCE,
        description="排序方式（默认按相关性排序）"
    )

    @field_validator("rows")
    @classmethod
    def validate_rows(cls, value):
        if value < 1 or value > 10:
            raise ValueError("rows超出范围，允许的范围为1-10！")
        return value

    @field_validator("filter")
    @classmethod
    def validate_filter(cls, value: Optional[str]) -> Optional[str]:
        if value:
            valid_fields = {'from-pub-date', 'until-pub-date'}
            # 简单验证过滤条件格式（实际使用时可根据Crossref支持的字段进一步验证）
            for pair in value.split(','):
                if ':' not in pair:
                    raise ValueError(f"过滤条件格式错误，应为 'field:value'，实际得到: {pair}")
                field = pair.split(':')[0]
                if field not in valid_fields:
                    raise ValueError(
                        f"非法字段'{field}'，可用字段：{valid_fields}"
                    )
        return value