# fastboot/entity/decorators.py
from typing import Type
from fastboot.entity.registry import default_registry

def entity(cls: Type = None, *, table_name: str = None):
    """
    @entity 装饰器。
    用于标记一个类为“单一事实来源”的业务实体。
    """
    def wrap(c: Type) -> Type:
        # 在这里可以给类附加一些元数据，比如表名
        setattr(c, '_meta_table_name', table_name or c.__name__.lower() + 's')
        
        # 将类注册到中心
        default_registry.register(c)
        return c

    if cls is None:
        # 允许带参数调用: @entity(table_name="my_books")
        return wrap
    # 允许不带参数调用: @entity
    return wrap(cls)