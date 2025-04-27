import requests

BASE_URL = "http://localhost:8080/product"

def test_create_product():
    """测试创建商品"""
    payload = {
        "name": "Test Product",
        "price": 100.00,
        "stock": 0  # 添加stock字段
    }
    response = requests.post(f"{BASE_URL}/create", json=payload)
    assert response.status_code == 200, f"创建失败，状态码: {response.status_code}"
    data = response.json()
    print("✅ 创建返回:", data)
    assert data.get("success") is True
    assert isinstance(data.get("data"), int)  # data是新建的ID
    return data["data"]

def test_get_product(product_id: int):
    """测试查询单个商品"""
    response = requests.get(f"{BASE_URL}/get/{product_id}")
    assert response.status_code == 200, f"查询失败，状态码: {response.status_code}"
    data = response.json()
    print("✅ 查询单个返回:", data)
    assert data.get("success") is True
    assert data["data"]["id"] == product_id

def test_get_all_products():
    """测试查询所有商品"""
    response = requests.get(f"{BASE_URL}/all")
    assert response.status_code == 200, f"查询全部失败，状态码: {response.status_code}"
    data = response.json()
    print("✅ 查询所有返回:", data)
    assert data.get("success") is True
    assert isinstance(data.get("data"), list)

def test_update_product(product_id: int):
    """测试更新商品"""
    payload = {
        "price": 200.00,
        "stock": 10  # 添加stock字段
    }
    response = requests.post(f"{BASE_URL}/update/{product_id}", json=payload)
    assert response.status_code == 200, f"更新失败，状态码: {response.status_code}"
    data = response.json()
    print("✅ 更新返回:", data)
    assert data.get("success") is True

def test_delete_product(product_id: int):
    """测试删除商品"""
    response = requests.post(f"{BASE_URL}/delete/{product_id}")
    assert response.status_code == 200, f"删除失败，状态码: {response.status_code}"
    data = response.json()
    print("✅ 删除返回:", data)
    assert data.get("success") is True

def test_query_deleted_product(product_id: int):
    """测试查询已删除的商品"""
    response = requests.get(f"{BASE_URL}/get/{product_id}")
    data = response.json()
    print("✅ 查询已删除商品返回:", data)
    assert response.status_code == 404, "已删除商品应返回404"

if __name__ == "__main__":
    print("🚀 开始测试 FastBoot Product模块 API接口...")
    new_product_id = test_create_product()
    test_get_product(new_product_id)
    test_get_all_products()
    test_update_product(new_product_id)
    test_get_product(new_product_id)  # 更新后再查一次
    test_delete_product(new_product_id)
    test_query_deleted_product(new_product_id)
    print("🎉 所有测试通过！")
