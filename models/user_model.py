# models/user_model.py
"""用户模型定义（数据库表结构）"""

from peewee import Model, AutoField, CharField, IntegerField, DatabaseProxy
from playhouse.shortcuts import model_to_dict

# 创建一个数据库代理
database_proxy = DatabaseProxy()

class BaseModel(Model):
    """所有模型继承的基类"""
    class Meta:
        database = database_proxy

class User(BaseModel):
    """用户表模型"""
    id = AutoField(primary_key=True)  # 修改为自增主键
    name = CharField()
    age = IntegerField()

    def to_dict(self):
        """辅助方法：把User对象转为字典"""
        return model_to_dict(self)
