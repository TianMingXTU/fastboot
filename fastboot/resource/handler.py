# fastboot/resource/handler.py
from typing import Type, TypeVar, Generic, List, Any, Optional
from tortoise.models import Model
from fastboot.entity.registry import default_registry

# 定义泛型类型变量
EntityType = TypeVar("EntityType")

# --- @resource_handler 装饰器 ---
def resource_handler(entity_cls: Type[EntityType]):
    """
    @resource_handler 装饰器。
    用于将一个处理器类(Handler)与一个实体类(Entity)进行绑定，
    并自动将此绑定关系注册到全局的实体注册中心。
    """
    def wrap(handler_cls: Type) -> Type:
        # 1. 将实体类附加到处理器类上，方便后续访问
        setattr(handler_cls, '_entity_cls', entity_cls)
        # 2. 调用注册中心的register_handler方法，进行注册
        default_registry.register_handler(entity_cls, handler_cls)
        return handler_cls
    return wrap

# --- BaseResourceHandler 基类 ---
class BaseResourceHandler(Generic[EntityType]):
    """
    【SST驱动版】资源处理器基类。
    它合并了传统 Repository 和 Service 的职责，直接提供可注入的、
    具备完整CRUD能力的业务逻辑单元。
    """
    _entity_cls: Type[EntityType]     # 由 @resource_handler 装饰器注入
    orm_model: Type[Model]            # 从 EntityRegistry 获取的ORM模型

    def __init__(self):
        """
        构造函数。在FastAPI的DI系统调用时，完成初始化。
        """
        if not hasattr(self, '_entity_cls'):
            raise TypeError(f"{self.__class__.__name__} 必须由 @resource_handler 装饰器绑定到一个实体类。")

        entity_name = self._entity_cls.__name__
        orm_model_cls = default_registry.get_orm_model(entity_name)
        
        if not orm_model_cls:
            raise RuntimeError(f"无法在实体注册中心找到实体 '{entity_name}' 对应的ORM模型。")
            
        self.orm_model = orm_model_cls

    async def get_by_id(self, item_id: Any) -> Optional[Model]:
        """通过主键ID异步获取单个实例。"""
        return await self.orm_model.get_or_none(id=item_id)

    async def create(self, create_data_dict: dict[str, Any]) -> Model:
        """异步创建新实例。"""
        return await self.orm_model.create(**create_data_dict)

    async def update(self, item_id: Any, update_data_dict: dict[str, Any]) -> Optional[Model]:
        """异步更新指定实例。"""
        obj = await self.get_by_id(item_id)
        if not obj:
            return None
        
        for key, value in update_data_dict.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        
        await obj.save()
        return obj

    async def delete(self, item_id: Any) -> bool:
        """异步删除指定实例。"""
        deleted_count = await self.orm_model.filter(id=item_id).delete()
        return deleted_count > 0

    async def paginate(self, page: int, page_size: int, **kwargs: Any) -> List[Model]:
        """异步分页查询方法。"""
        if page < 1: page = 1
        if page_size < 1: page_size = 10
        offset = (page - 1) * page_size
        return await self.orm_model.filter(**kwargs).offset(offset).limit(page_size)

    async def filter_by(self, **kwargs: Any) -> List[Model]:
        """根据提供的关键字参数异步过滤查询实例。"""
        return await self.orm_model.filter(**kwargs)

    async def exists_by(self, **kwargs: Any) -> bool:
        """异步判断是否存在符合指定条件的实例。"""
        return await self.orm_model.filter(**kwargs).exists()

    async def count_by(self, **kwargs: Any) -> int:
        """异步统计符合指定条件的实例数量。"""
        return await self.orm_model.filter(**kwargs).count()
