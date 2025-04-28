# fastboot/crud/base_service.py

"""通用基础业务逻辑层（Tortoise ORM异步版），支持自动挂载用户自定义Repository"""

from fastboot.repository_manager import RepositoryManager

repository_manager = RepositoryManager()

class BaseService:
    """基础Service，封装标准异步操作，优先挂载用户自定义Repository"""

    def __init__(self, model):
        repository_cls = repository_manager.get_repository_class(model)
        self.repository = repository_cls(model)

    async def create(self, **kwargs):
        return await self.repository.create(**kwargs)

    async def get_by_id(self, id):
        return await self.repository.get_by_id(id)

    async def get_all(self):
        return await self.repository.get_all()

    async def update(self, id, **kwargs):
        return await self.repository.update(id, **kwargs)

    async def delete(self, id):
        return await self.repository.delete(id)

    async def filter_by(self, **kwargs):
        return await self.repository.filter_by(**kwargs)

    async def exists_by(self, **kwargs):
        return await self.repository.exists_by(**kwargs)

    async def count_by(self, **kwargs):
        return await self.repository.count_by(**kwargs)

    async def paginate(self, page: int = 1, page_size: int = 10, **kwargs):
        return await self.repository.paginate(page, page_size, **kwargs)
