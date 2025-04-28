import asyncio
import sys
import os
import httpx

# 添加项目根目录到Python路径（保证可以import fastboot下的模块）
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:8080/product"

async def test_create_product(client):
    """测试创建商品"""
    payload = {"name": "FastBoot商品", "price": 888}
    response = await client.post(f"{BASE_URL}/create", json=payload)
    response_data = response.json()
    print("创建返回：", response_data)

    assert response.status_code == 200, f"创建失败: {response_data}"
    return response_data["data"]  # 返回新建的商品ID

async def test_get_product(client, product_id):
    """测试根据ID查询商品"""
    response = await client.get(f"{BASE_URL}/get/{product_id}")
    response_data = response.json()
    print("查询返回：", response_data)

    assert response.status_code == 200, f"查询失败: {response_data}"
    assert response_data["data"]["id"] == product_id

async def test_find_product_by_name(client):
    """测试根据商品名查询（通过自定义接口）"""
    response = await client.get(f"{BASE_URL}/search_by_name/FastBoot商品")
    response_data = response.json()
    print("根据商品名查找：", response_data)

    assert response.status_code == 200, f"查询失败: {response_data}"
    assert response_data["data"]["name"] == "FastBoot商品"

async def test_delete_product(client, product_id):
    """测试删除商品"""
    response = await client.post(f"{BASE_URL}/delete/{product_id}")
    response_data = response.json()
    print("删除返回：", response_data)

    assert response.status_code == 200, f"删除失败: {response_data}"

async def run_tests():
    """主测试入口"""
    print("✅ 开始测试FastBoot接口能力")

    async with httpx.AsyncClient() as client:
        # 测试创建
        product_id = await test_create_product(client)

        # 测试查询
        await test_get_product(client, product_id)

        # 测试自定义搜索
        await test_find_product_by_name(client)

        # 测试删除
        await test_delete_product(client, product_id)

    print("✅ 所有接口测试通过！")

if __name__ == "__main__":
    asyncio.run(run_tests())
