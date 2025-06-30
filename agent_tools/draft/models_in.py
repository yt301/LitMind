from langchain.agents import tool
from pydantic import BaseModel, Field

class TranslateInput(BaseModel):
    text: str = Field(default="请输入文本",description="待翻译的文本")
    source_language: str = Field(default="Chinese", description="源语言代码（如 'Chinese'）")
    translated_language: str = Field(default="English",description="目标语言代码（如 'English'）")

class TextLengthInput(BaseModel):
    text: str = Field(..., description="需要统计长度的文本")

