"""通用基础控制器，自动提供标准CRUD接口（统一返回格式 + 支持扩展）"""

from fastapi import Body, Query
from fastboot.router_scanner import controller, get, post
from fastboot.response import SuccessResponse, ErrorResponse
from fastboot.crud.request_generator import generate_create_request_model, generate_update_request_model
from pydantic import ValidationError
from fastboot.service_manager import ServiceManager

service_manager = ServiceManager()

@controller("/base")
class BaseController:
    """基础Controller，统一提供标准CRUD接口，并支持扩展"""

    model = None
    prefix = "/base"

    def __init__(self):

        if self.model is None:
            raise ValueError("必须在子类中指定model！")
        
        service_cls = service_manager.get_service_class(self.model)
        self.service = service_cls(self.model)

        self.CreateRequest = generate_create_request_model(self.model)
        self.UpdateRequest = generate_update_request_model(self.model)

    @post("/create")
    async def create(self, request: dict = Body(...)):
        """创建对象"""
        try:
            validated = self.CreateRequest(**request)
            obj = self.service.create(**validated.dict())
            return SuccessResponse.ok(obj.id)
        except ValidationError as ve:
            return ErrorResponse.fail(str(ve), status_code=422)
        except Exception as e:
            return ErrorResponse.fail(f"创建失败: {str(e)}", status_code=400)

    @get("/get/{id}")
    async def get_by_id(self, id: int):
        """根据ID查询对象"""
        obj = self.service.get_by_id(id)
        if obj:
            return SuccessResponse.ok(obj.__data__)
        else:
            return ErrorResponse.fail("对象不存在", status_code=404)

    @get("/all")
    async def get_all(self):
        """查询所有对象"""
        objs = self.service.get_all()
        return SuccessResponse.ok([obj.__data__ for obj in objs])

    @get("/page")
    async def paginate(self, page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
        """分页查询对象"""
        objs = self.service.paginate(page=page, page_size=page_size)
        return SuccessResponse.ok([obj.__data__ for obj in objs])

    @post("/update/{id}")
    async def update(self, id: int, request: dict = Body(...)):
        """根据ID更新对象"""
        try:
            validated = self.UpdateRequest(**request)
            data = validated.dict(exclude_unset=True)
            affected = self.service.update(id, **data)
            if affected:
                return SuccessResponse.ok()
            else:
                return ErrorResponse.fail("更新失败，记录不存在", status_code=404)
        except ValidationError as ve:
            return ErrorResponse.fail(str(ve), status_code=422)
        except Exception as e:
            return ErrorResponse.fail(f"更新失败: {str(e)}", status_code=400)

    @post("/delete/{id}")
    async def delete(self, id: int):
        """根据ID删除对象"""
        affected = self.service.delete(id)
        if affected:
            return SuccessResponse.ok()
        else:
            return ErrorResponse.fail("删除失败，记录不存在", status_code=404)
