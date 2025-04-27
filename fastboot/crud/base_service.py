"""通用基础业务逻辑层，支持自动挂载用户自定义Repository"""

from fastboot.repository_manager import RepositoryManager

repository_manager = RepositoryManager()

class BaseService:
    """基础Service，封装标准操作，优先挂载用户自定义Repository"""

    def __init__(self, model):
        repository_cls = repository_manager.get_repository_class(model)
        self.repository = repository_cls(model)

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

    def filter_by(self, **kwargs):
        return self.repository.filter_by(**kwargs)

    def exists_by(self, **kwargs):
        return self.repository.exists_by(**kwargs)

    def count_by(self, **kwargs):
        return self.repository.count_by(**kwargs)

    def paginate(self, page: int = 1, page_size: int = 10, **kwargs):
        return self.repository.paginate(page, page_size, **kwargs)
