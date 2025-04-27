# controllers/product_controller.py
from fastboot.crud.base_controller import BaseController
from models.product_model import Product
from fastboot.router_scanner import controller


@controller("/product")
class ProductController(BaseController):
    model = Product
    prefix = "/product"
