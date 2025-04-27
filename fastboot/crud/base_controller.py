# fastboot/crud/base_controller.py
"""通用基础控制器，自动生成增删改查接口。"""

from fastapi import HTTPException
from fastboot.router_scanner import controller, get, post


@controller("/base")  # 注意：子类一定要重写prefix
class BaseController:
    """基础Controller，自动提供标准CRUD接口。"""

    model = None  # 必须子类指定
    prefix = "/base"  # 必须子类指定

    def __init__(self):
        from fastboot.crud.base_service import BaseService

        if self.model is None:
            raise ValueError("model 未指定")
        self.service = BaseService(self.model)

    @post("/create")
    async def create(self, request: dict):
        try:
            obj = self.service.create(**request)
            return {"success": True, "data": obj.id}
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @get("/get/{id}")
    async def get_by_id(self, id: int):
        obj = self.service.get_by_id(id)
        if obj:
            return {"success": True, "data": obj.__data__}
        else:
            raise HTTPException(status_code=404, detail="对象不存在")

    @get("/all")
    async def get_all(self):
        objs = self.service.get_all()
        return {"success": True, "data": [obj.__data__ for obj in objs]}

    @post("/update/{id}")
    async def update(self, id: int, request: dict):
        affected = self.service.update(id, **request)
        if affected:
            return {"success": True}
        else:
            raise HTTPException(status_code=404, detail="更新失败")

    @post("/delete/{id}")
    async def delete(self, id: int):
        affected = self.service.delete(id)
        if affected:
            return {"success": True}
        else:
            raise HTTPException(status_code=404, detail="删除失败")
