import requests
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastboot.database import Database
from fastboot.config import ConfigManager

BASE_URL = "http://localhost:8080/product"

# 初始化数据库连接
db = Database()
db.initialize()  # 添加这行
db.connect()     # 添加这行

def test_create_product():
    payload = {"name": "FastBoot商品", "price": 888}
    response = requests.post(f"{BASE_URL}/create", json=payload)
    print("创建返回：", response.json())
    assert response.status_code == 200
    return response.json()["data"]

def test_get_product(product_id):
    response = requests.get(f"{BASE_URL}/get/{product_id}")
    print("查询返回：", response.json())
    assert response.status_code == 200

def test_find_product_by_name():
    # 这里我们要直接测试 ProductService.find_product_by_name()
    from services.product_service import ProductService
    from models.product_model import Product

    service = ProductService(Product)
    product = service.find_product_by_name("FastBoot商品")
    print("根据商品名查找：", product.__data__ if product else None)
    assert product is not None
    assert product.name == "FastBoot商品"

def test_delete_product(product_id):
    response = requests.post(f"{BASE_URL}/delete/{product_id}")
    print("删除返回：", response.json())
    assert response.status_code == 200

def cleanup():
    try:
        if db and db.db and not db.db.is_closed():
            db.close()
    except:
        pass

if __name__ == "__main__":
    try:
        print("✅ 开始测试FastBoot自定义扩展能力")
        product_id = test_create_product()
        test_get_product(product_id)
        test_find_product_by_name()
        test_delete_product(product_id)
        print("✅ 所有测试通过！")
    finally:
        cleanup()
