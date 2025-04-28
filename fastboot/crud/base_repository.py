# fastboot/crud/base_repository.py
class BaseRepository:
    """提供通用 CRUD 操作的基类仓库。

    该类封装了对 ORM 模型的通用数据库操作，支持同步/异步混合操作模式。

    Attributes:
        model: 关联的 ORM 模型类
    """

    def __init__(self, model):
        """初始化仓库实例。

        Args:
            model (object): 需要操作的 ORM 模型类
        """
        self.model = model

    def get_all(self):
        """获取模型所有实例。

        Returns:
            list: 包含所有模型实例的列表，按默认排序返回
        """
        return self.model.all()

    async def create(self, **kwargs):
        """异步创建新实例。

        Args:
            **kwargs: 模型字段的键值对参数

        Returns:
            object: 新创建的模型实例对象
            None: 创建失败时返回
        """
        return await self.model.create(**kwargs)

    async def get_by_id(self, id: int):
        """通过主键ID异步获取单个实例。

        Args:
            id (int): 要查询的实例主键ID

        Returns:
            object: 找到的模型实例对象
            None: 未找到时返回
        """
        return await self.model.get_or_none(id=id)

    async def update(self, id: int, **kwargs):
        """异步更新指定实例。

        执行流程：
        1. 根据ID查询实例
        2. 批量更新字段
        3. 保存到数据库

        Args:
            id (int): 要更新的实例主键ID
            **kwargs: 需要更新的字段键值对

        Returns:
            object: 更新后的模型实例对象
            None: 未找到对应实例时返回
        """
        obj = await self.get_by_id(id)
        if not obj:
            return None
        for key, value in kwargs.items():
            setattr(obj, key, value)
        await obj.save()
        return obj

    async def delete(self, id: int):
        """异步删除指定实例。

        Args:
            id (int): 要删除的实例主键ID

        Returns:
            object: 被删除的模型实例对象（已从数据库移除）
            None: 未找到对应实例时返回
        """
        obj = await self.get_by_id(id)
        if not obj:
            return None
        await obj.delete()
        return obj

    def filter_by(self, **kwargs):
        """同步过滤查询方法。

        Args:
            **kwargs: 过滤条件的键值对

        Returns:
            QuerySet: 包含过滤结果的查询集合对象
        """
        return self.model.filter(**kwargs)

    async def exists_by(self, **kwargs):
        """异步判断是否存在符合条件的实例。

        Args:
            **kwargs: 过滤条件的键值对

        Returns:
            bool: True表示存在，False表示不存在
        """
        return await self.model.filter(**kwargs).exists()

    async def count_by(self, **kwargs):
        """异步统计符合条件的实例数量。

        Args:
            **kwargs: 过滤条件的键值对

        Returns:
            int: 符合条件的实例总数
        """
        return await self.model.filter(**kwargs).count()

    def paginate(self, page: int = 1, page_size: int = 10, **kwargs):
        """分页查询方法。

        分页计算公式：
        offset = (page - 1) * page_size

        Args:
            page (int): 页码（默认：1）
            page_size (int): 每页数量（默认：10）
            **kwargs: 过滤条件的键值对

        Returns:
            QuerySet: 包含分页结果的查询集合对象
        """
        offset = (page - 1) * page_size
        return self.model.filter(**kwargs).offset(offset).limit(page_size)