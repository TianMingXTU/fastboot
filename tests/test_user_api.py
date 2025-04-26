import requests

# 设置FastBoot应用运行的基础地址
BASE_URL = "http://localhost:8080"

def test_register_user():
    url = f"{BASE_URL}/user/register"
    data = {
        "name": "Alice",
        "age": 22
    }
    response = requests.post(url, json=data)
    print("注册用户返回：", response.json())
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["data"]["name"] == "Alice"

def test_get_user_info(user_id):
    url = f"{BASE_URL}/user/info/{user_id}"
    response = requests.get(url)
    print("查询用户返回：", response.json())
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["data"]["id"] == user_id

def test_get_nonexistent_user():
    url = f"{BASE_URL}/user/info/99999"  # 假设这个用户不存在
    response = requests.get(url)
    print("查询不存在用户返回：", response.json())
    assert response.status_code == 404 or response.json()["success"] == False

if __name__ == "__main__":
    # 1. 测试注册用户
    test_register_user()

    # 2. 测试查询刚注册的用户（假设是ID 1）
    test_get_user_info(1)

    # 3. 测试查询不存在的用户
    test_get_nonexistent_user()
