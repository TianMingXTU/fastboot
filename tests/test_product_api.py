import requests

BASE_URL = "http://localhost:8080/product"


def test_create_product():
    payload = {"name": "Test Product", "price": 100}
    response = requests.post(f"{BASE_URL}/create", json=payload)
    assert response.status_code == 200
    data = response.json()
    print("创建返回：", data)
    assert data["success"] is True
    assert isinstance(data["data"], int)  # 返回新创建的ID
    return data["data"]


def test_get_product(product_id):
    response = requests.get(f"{BASE_URL}/get/{product_id}")
    assert response.status_code == 200
    data = response.json()
    print("查询返回：", data)
    assert data["success"] is True
    assert data["data"]["id"] == product_id


def test_get_all_products():
    response = requests.get(f"{BASE_URL}/all")
    assert response.status_code == 200
    data = response.json()
    print("查询所有返回：", data)
    assert data["success"] is True
    assert isinstance(data["data"], list)


def test_update_product(product_id):
    payload = {"price": 200}
    response = requests.post(f"{BASE_URL}/update/{product_id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    print("更新返回：", data)
    assert data["success"] is True


def test_delete_product(product_id):
    response = requests.post(f"{BASE_URL}/delete/{product_id}")
    assert response.status_code == 200
    data = response.json()
    print("删除返回：", data)
    assert data["success"] is True


def test_query_deleted_product(product_id):
    response = requests.get(f"{BASE_URL}/get/{product_id}")
    print("查询已删除的返回：", response.json())
    assert response.status_code == 404  # 已删除，返回404


if __name__ == "__main__":
    new_product_id = test_create_product()
    test_get_product(new_product_id)
    test_get_all_products()
    test_update_product(new_product_id)
    test_get_product(new_product_id)  # 更新后再查一次
    test_delete_product(new_product_id)
    test_query_deleted_product(new_product_id)
