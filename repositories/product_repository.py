# repositories/product_repository.py
from fastboot.crud.base_repository import BaseRepository
from models.product_model import Product

class ProductRepository(BaseRepository):
    """自定义Product数据访问层"""

    def get_by_name(self, name: str):
        """根据商品名查询商品"""
        return self.model.select().where(self.model.name == name).first()
