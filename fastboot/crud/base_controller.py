"""通用基础控制器，自动提供标准CRUD接口（使用内部请求校验）。"""

from fastapi import HTTPException, Body
from fastboot.router_scanner import controller, get, post
from fastboot.crud.request_generator import (
    generate_create_request_model,
    generate_update_request_model,
)
from pydantic import ValidationError


@controller("/base")
class BaseController:
    """基础Controller，统一提供标准CRUD接口。"""

    model = None
    prefix = "/base"

    def __init__(self):
        from fastboot.crud.base_service import BaseService

        if self.model is None:
            raise ValueError("必须在子类中指定model！")

        self.service = BaseService(self.model)

        self.CreateRequest = generate_create_request_model(self.model)
        self.UpdateRequest = generate_update_request_model(self.model)

    @post("/create")
    async def create(self, request: dict = Body(...)):
        """创建对象"""
        try:
            validated = self.CreateRequest(**request)  # ✅ 这里手动校验
            obj = self.service.create(**validated.dict())
            return {"success": True, "data": obj.id}
        except ValidationError as ve:
            raise HTTPException(status_code=422, detail=ve.errors())
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"创建失败: {str(e)}")

    @get("/get/{id}")
    async def get_by_id(self, id: int):
        """根据ID查询对象"""
        obj = self.service.get_by_id(id)
        if obj:
            return {"success": True, "data": obj.__data__}
        else:
            raise HTTPException(status_code=404, detail="对象不存在")

    @get("/all")
    async def get_all(self):
        """查询所有对象"""
        objs = self.service.get_all()
        return {"success": True, "data": [obj.__data__ for obj in objs]}

    @post("/update/{id}")
    async def update(self, id: int, request: dict = Body(...)):
        """根据ID更新对象"""
        try:
            validated = self.UpdateRequest(**request)  # ✅ 更新也校验
            data = validated.dict(exclude_unset=True)
            affected = self.service.update(id, **data)
            if affected:
                return {"success": True}
            else:
                raise HTTPException(status_code=404, detail="更新失败，记录不存在")
        except ValidationError as ve:
            raise HTTPException(status_code=422, detail=ve.errors())
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"更新失败: {str(e)}")

    @post("/delete/{id}")
    async def delete(self, id: int):
        """根据ID删除对象"""
        affected = self.service.delete(id)
        if affected:
            return {"success": True}
        else:
            raise HTTPException(status_code=404, detail="删除失败，记录不存在")
