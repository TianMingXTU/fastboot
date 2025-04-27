from peewee import Model, DatabaseProxy
from playhouse.shortcuts import model_to_dict

# 创建数据库代理，延迟绑定
database_proxy = DatabaseProxy()

class BaseModel(Model):
    """所有模型统一继承的基类"""
    class Meta:
        database = database_proxy

    def to_dict(self):
        """将模型对象转换为字典"""
        return model_to_dict(self)
