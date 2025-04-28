# fastboot/crud/base_repository.py

"""通用基础数据访问层（Tortoise ORM异步版），封装标准CRUD + 扩展操作"""

class BaseRepository:
    """基础Repository，提供标准异步CRUD和扩展查询操作"""

    def __init__(self, model):
        self.model = model

    async def create(self, **kwargs):
        """创建新记录"""
        instance = await self.model.create(**kwargs)
        return instance

    async def get_by_id(self, id):
        """根据ID查询记录"""
        try:
            instance = await self.model.get(id=id)
            return instance
        except self.model.DoesNotExist:
            return None

    async def get_all(self):
        """查询所有记录"""
        instances = await self.model.all()
        return instances

    async def update(self, id, **kwargs):
        """根据ID更新记录"""
        update_count = await self.model.filter(id=id).update(**kwargs)
        return update_count

    async def delete(self, id):
        """根据ID删除记录"""
        delete_count = await self.model.filter(id=id).delete()
        return delete_count

    async def filter_by(self, **kwargs):
        """根据条件过滤查询"""
        query = self.model.filter(**kwargs)
        instances = await query.all()
        return instances

    async def exists_by(self, **kwargs):
        """检查是否存在符合条件的记录"""
        exists = await self.model.filter(**kwargs).exists()
        return exists

    async def count_by(self, **kwargs):
        """符合条件的记录数量"""
        count = await self.model.filter(**kwargs).count()
        return count

    async def paginate(self, page: int = 1, page_size: int = 10, **kwargs):
        """分页查询"""
        offset = (page - 1) * page_size
        query = self.model.filter(**kwargs).offset(offset).limit(page_size)
        instances = await query.all()
        return instances
