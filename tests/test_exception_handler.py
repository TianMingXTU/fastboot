from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from fastapi.testclient import TestClient
from fastboot.exception_handler import ExceptionHandler

# 创建 FastAPI 应用实例
app = FastAPI()

# 初始化异常处理器
exception_handler = ExceptionHandler(app)

# 定义一个简单的路由来触发 HTTPException
@app.get("/http_exception")
async def trigger_http_exception():
    raise HTTPException(status_code=404, detail="Item not found")

# 定义一个简单的路由来触发 RequestValidationError
class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

@app.post("/items/")
async def create_item(item: Item):
    return item

# 定义一个简单的路由来触发全局异常
@app.get("/global_exception")
async def trigger_global_exception():
    raise Exception("Something went wrong")

# 创建测试客户端
client = TestClient(app)

# 测试 HTTPException
response = client.get("/http_exception")
print("HTTPException Test:", response.json())

# 测试 RequestValidationError
response = client.post("/items/", json={"name": "foo", "price": "not a float"})
print("RequestValidationError Test:", response.json())

# 测试全局异常
response = client.get("/global_exception")
print("Global Exception Test:", response.json())