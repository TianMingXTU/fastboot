# fastboot/crud/base_service.py
"""通用基础业务逻辑层，直接调用BaseRepository"""

from fastboot.crud.base_repository import BaseRepository

class BaseService:
    """基础Service，直接封装Repository的标准操作。"""

    def __init__(self, model):
        self.repository = BaseRepository(model)

    def create(self, **kwargs):
        return self.repository.create(**kwargs)

    def get_by_id(self, id):
        return self.repository.get_by_id(id)

    def get_all(self):
        return self.repository.get_all()

    def update(self, id, **kwargs):
        return self.repository.update(id, **kwargs)

    def delete(self, id):
        return self.repository.delete(id)
