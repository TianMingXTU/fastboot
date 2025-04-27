#fastboot\crud\base_repository.py
"""通用基础数据访问层，封装标准CRUD + 扩展操作"""

class BaseRepository:
    """基础Repository，提供标准CRUD和扩展查询操作"""

    def __init__(self, model):
        self.model = model

    def create(self, **kwargs):
        return self.model.create(**kwargs)

    def get_by_id(self, id):
        try:
            return self.model.get_by_id(id)
        except self.model.DoesNotExist:
            return None

    def get_all(self):
        return list(self.model.select())

    def update(self, id, **kwargs):
        query = self.model.update(**kwargs).where(self.model.id == id)
        return query.execute()

    def delete(self, id):
        query = self.model.delete().where(self.model.id == id)
        return query.execute()

    # 🚀 新增扩展方法
    def filter_by(self, **kwargs):
        """根据条件过滤查询"""
        query = self.model.select()
        for k, v in kwargs.items():
            query = query.where(getattr(self.model, k) == v)
        return list(query)

    def exists_by(self, **kwargs):
        """检查是否存在符合条件的记录"""
        query = self.model.select()
        for k, v in kwargs.items():
            query = query.where(getattr(self.model, k) == v)
        return query.exists()

    def count_by(self, **kwargs):
        """符合条件的记录数量"""
        query = self.model.select()
        for k, v in kwargs.items():
            query = query.where(getattr(self.model, k) == v)
        return query.count()

    def paginate(self, page: int = 1, page_size: int = 10, **kwargs):
        """分页查询"""
        query = self.model.select()
        for k, v in kwargs.items():
            query = query.where(getattr(self.model, k) == v)
        return list(query.paginate(page, page_size))
