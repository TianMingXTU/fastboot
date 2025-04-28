# models/base_model.py

from tortoise import fields, models

class BaseModel(models.Model):
    """所有模型统一继承的基类"""

    id = fields.IntField(pk=True)  # 主键ID，Tortoise需要显式声明

    class Meta:
        abstract = True  # 声明这是一个抽象基类，Tortoise不会给它单独建表

    def to_dict(self):
        """将模型对象转换为字典"""
        data = {}
        for field in self._meta.fields_map:
            data[field] = getattr(self, field)
        return data
