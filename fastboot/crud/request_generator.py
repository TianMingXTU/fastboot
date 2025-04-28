# fastboot/crud/request_generator.py

"""根据Tortoise ORM模型动态生成Pydantic请求体"""

from pydantic import BaseModel, create_model
from typing import Optional
from tortoise import fields
from tortoise.models import Model

def generate_create_request_model(model_cls: Model) -> BaseModel:
    """生成创建用的请求体模型（部分字段必填）"""
    model_fields = model_cls._meta.fields_map
    fields_def = {}

    for name, field in model_fields.items():
        if isinstance(field, fields.IntField) and field.pk:
            # 主键ID跳过
            continue
        
        python_type = map_tortoise_field_to_python(field)

        # 是否有默认值或者可空
        if field.default is not None or field.null:
            fields_def[name] = (Optional[python_type], field.default)
        else:
            fields_def[name] = (python_type, ...)

    CreateRequestModel = create_model(
        f"{model_cls.__name__}CreateRequest",
        **fields_def
    )
    return CreateRequestModel

def generate_update_request_model(model_cls: Model) -> BaseModel:
    """生成更新用的请求体模型（所有字段都可选）"""
    model_fields = model_cls._meta.fields_map
    fields_def = {}

    for name, field in model_fields.items():
        if isinstance(field, fields.IntField) and field.pk:
            # 主键ID跳过
            continue

        python_type = map_tortoise_field_to_python(field)
        fields_def[name] = (Optional[python_type], None)

    UpdateRequestModel = create_model(
        f"{model_cls.__name__}UpdateRequest",
        **fields_def
    )
    return UpdateRequestModel

def map_tortoise_field_to_python(field: fields.Field):
    """将Tortoise ORM字段映射为Python基础类型"""
    if isinstance(field, fields.IntField):
        return int
    elif isinstance(field, fields.CharField):
        return str
    elif isinstance(field, fields.DecimalField):
        return float
    elif isinstance(field, fields.FloatField):
        return float
    elif isinstance(field, fields.BooleanField):
        return bool
    elif isinstance(field, fields.DatetimeField):
        from datetime import datetime
        return datetime
    else:
        return str  # 默认fallback
