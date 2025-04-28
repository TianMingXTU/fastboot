# controllers/product_controller.py

from fastboot.router_scanner import controller, get
from fastboot.crud.base_controller import BaseController
from models.product_model import Product
from fastboot.response import SuccessResponse, ErrorResponse

@controller("/product")
class ProductController(BaseController):
    model = Product
    prefix = "/product"

    @get("/search_by_name/{name}")
    async def search_by_name(self, name: str):  
        """自定义接口：根据商品名查询商品"""
        product = await self.service.find_product_by_name(name)
        if product:
            return SuccessResponse.ok(product.to_dict())
        else:
            return ErrorResponse.fail("没有找到匹配的商品", status_code=404)
