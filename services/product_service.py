# services/product_service.py

from fastboot.crud.base_service import BaseService
from models.product_model import Product

class ProductService(BaseService):
    """自定义Product业务逻辑"""

    async def find_product_by_name(self, name: str):
        """调用自定义Repository方法"""
        return await self.repository.get_by_name(name)
