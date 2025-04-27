"""根据Peewee模型动态生成Pydantic请求体"""

from pydantic import BaseModel, create_model
from typing import Optional
from peewee import Model, Field, AutoField

def generate_create_request_model(model_cls: Model) -> BaseModel:
    """生成创建用的请求体模型（部分字段必填）"""
    fields = {}
    for name, field in model_cls._meta.fields.items():
        if isinstance(field, AutoField):
            continue
            
        field_type = map_peewee_field_to_python(field)
        
        # 如果字段有默认值或允许为空，则设置为可选
        if field.default is not None or field.null:
            fields[name] = (Optional[field_type], field.default)
        else:
            fields[name] = (field_type, ...)
    
    CreateRequestModel = create_model(
        f"{model_cls.__name__}CreateRequest",
        **fields
    )
    return CreateRequestModel

def generate_update_request_model(model_cls: Model) -> BaseModel:
    """生成更新用的请求体模型（字段可选）"""
    fields = {}
    for name, field in model_cls._meta.fields.items():
        if isinstance(field, AutoField):
            continue
        field_type = map_peewee_field_to_python(field)
        fields[name] = (Optional[field_type], None)
    
    UpdateRequestModel = create_model(
        f"{model_cls.__name__}UpdateRequest",
        **fields
    )
    return UpdateRequestModel

def map_peewee_field_to_python(field: Field):
    """将Peewee字段类型映射为Python基础类型"""
    from peewee import IntegerField, CharField, DecimalField, FloatField, BooleanField

    if isinstance(field, IntegerField):
        return int
    elif isinstance(field, CharField):
        return str
    elif isinstance(field, DecimalField):
        return float
    elif isinstance(field, FloatField):
        return float
    elif isinstance(field, BooleanField):
        return bool
    else:
        return str  # 默认fallback
