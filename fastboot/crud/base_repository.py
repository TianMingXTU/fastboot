# fastboot/crud/base_repository.py
"""通用基础数据访问层，封装标准CRUD操作。"""

class BaseRepository:
    """基础Repository，提供create, get, update, delete等操作。"""

    def __init__(self, model):
        self.model = model

    def create(self, **kwargs):
        """创建新记录"""
        return self.model.create(**kwargs)

    def get_by_id(self, id):
        """根据ID查询"""
        try:
            return self.model.get_by_id(id)
        except self.model.DoesNotExist:
            return None

    def get_all(self):
        """查询所有记录"""
        return list(self.model.select())

    def update(self, id, **kwargs):
        """根据ID更新记录"""
        query = self.model.update(**kwargs).where(self.model.id == id)
        return query.execute()

    def delete(self, id):
        """根据ID删除记录"""
        query = self.model.delete().where(self.model.id == id)
        return query.execute()
