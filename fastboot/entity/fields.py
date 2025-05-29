# fastboot/entity/fields.py
from dataclasses import dataclass, field
from typing import Any, Type, Optional
from tortoise import fields as tortoise_fields

@dataclass
class FieldDefinition:
    """
    一个数据类，用于存储我们统一字段的所有元数据。
    """
    # 数据库相关配置
    db_type: Type[tortoise_fields.Field]
    pk: bool = False
    db_index: bool = False
    unique: bool = False
    nullable: bool = False
    max_length: Optional[int] = None
    
    # API及校验相关配置 (为未来步骤预留)
    api_expose: bool = True
    api_mutable: bool = True
    pydantic_type: Optional[Type] = None
    
    # 存储原始的Python类型提示
    python_type: Optional[Type] = None
    
    # 存储传递给Tortoise字段构造函数的额外参数
    extra_db_args: dict = field(default_factory=dict)

def Field(
    db_type: Type[tortoise_fields.Field],
    *,
    pk: bool = False,
    db_index: bool = False,
    unique: bool = False,
    nullable: bool = False,
    max_length: Optional[int] = None,
    # 未来可添加更多参数
    **kwargs: Any
) -> Any:
    """
    我们统一的字段定义函数。
    它不直接返回值，而是返回一个包含所有配置的 FieldDefinition 实例。
    """
    return FieldDefinition(
        db_type=db_type,
        pk=pk,
        db_index=db_index,
        unique=unique,
        nullable=nullable,
        max_length=max_length,
        extra_db_args=kwargs
    )