# fastboot/resource/router_factory.py (最终修正版)
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Type, TypeVar, List
from pydantic import BaseModel
from tortoise.models import Model

# === 核心变更：导入新的基类 ===
from .handler import BaseResourceHandler 
from ..response import SuccessResponse, ErrorResponse
from ..entity.registry import default_registry

# === 核心变更：更新泛型类型定义 ===
EntityArg = TypeVar("EntityArg")
HandlerArg = TypeVar("HandlerArg", bound=BaseResourceHandler) 

def create_generic_crud_router(
    # === 核心变更：更新参数名和类型提示 ===
    entity_cls: Type[EntityArg],
    handler_cls: Type[HandlerArg], 
    
    can_create: bool = True,
    can_read_one: bool = True,
    can_read_all: bool = True, 
    can_update: bool = True,
    can_delete: bool = True
) -> APIRouter:
    """
    【SST驱动版】工厂函数，为指定的实体(Entity)和资源处理器(Handler)创建包含标准CRUD路由的APIRouter。
    """
    router = APIRouter()
    
    entity_name = entity_cls.__name__

    orm_model = default_registry.get_orm_model(entity_name)
    response_schema = default_registry.get_pydantic_schema(entity_name, 'response')
    create_schema = default_registry.get_pydantic_schema(entity_name, 'create')
    update_schema = default_registry.get_pydantic_schema(entity_name, 'update')
    
    if not all([orm_model, response_schema, create_schema, update_schema]):
        raise RuntimeError(f"无法为实体 '{entity_name}' 创建CRUD路由，因其ORM或Pydantic模型未能生成。")

    pk_field = orm_model._meta.pk
    pk_type: Type = pk_field.field_type

    # CREATE 操作
    if can_create:
        @router.post("/", status_code=status.HTTP_201_CREATED, summary=f"创建 {entity_name}")
        async def create_item_endpoint(
            item_in: create_schema, # type: ignore
            handler: HandlerArg = Depends(handler_cls) # 核心变更: 变量名和类型
        ):
            created_item_orm = await handler.create(create_data_dict=item_in.model_dump())
            pk_value = getattr(created_item_orm, pk_field.model_field_name)
            return SuccessResponse.ok({"id": pk_value}) 

    # READ ONE 操作
    if can_read_one:
        @router.get("/{item_id}", response_model=response_schema, summary=f"获取 {entity_name}") # type: ignore
        async def get_item_by_id_endpoint(
            item_id: pk_type, # type: ignore
            handler: HandlerArg = Depends(handler_cls) # 核心变更: 变量名和类型
        ):
            item_orm = await handler.get_by_id(item_id=item_id)
            if not item_orm: 
                ErrorResponse.fail(f"{entity_name} (ID: {item_id}) 未找到", status.HTTP_404_NOT_FOUND)
            return item_orm

    # READ ALL / PAGINATE 操作
    if can_read_all:
        @router.get("/", response_model=List[response_schema], summary=f"获取 {entity_name} 列表") # type: ignore
        async def get_all_items_endpoint(
            page: int = Query(1, ge=1), 
            page_size: int = Query(10, ge=1, le=100), 
            handler: HandlerArg = Depends(handler_cls) # 核心变更: 变量名和类型
        ):
            items_orm_list = await handler.paginate(page=page, page_size=page_size)
            return items_orm_list

    # UPDATE 操作
    if can_update:
        @router.put("/{item_id}", summary=f"更新 {entity_name}")
        async def update_item_endpoint(
            item_id: pk_type, # type: ignore
            item_in: update_schema, # type: ignore
            handler: HandlerArg = Depends(handler_cls) # 核心变更: 变量名和类型
        ):
            update_data = item_in.model_dump(exclude_unset=True)
            if not update_data: 
                ErrorResponse.fail("更新请求体不能为空", status.HTTP_400_BAD_REQUEST)
            updated_item = await handler.update(item_id=item_id, update_data_dict=update_data)
            if not updated_item: 
                ErrorResponse.fail(f"{entity_name} (ID: {item_id}) 未找到", status.HTTP_404_NOT_FOUND)
            return SuccessResponse.ok_message(message=f"{entity_name} (ID: {item_id}) 更新成功。")

    # DELETE 操作
    if can_delete:
        @router.delete("/{item_id}", status_code=status.HTTP_200_OK, summary=f"删除 {entity_name}")
        async def delete_item_endpoint(
            item_id: pk_type, # type: ignore
            handler: HandlerArg = Depends(handler_cls) # 核心变更: 变量名和类型
        ):
            success = await handler.delete(item_id=item_id)
            if not success: 
                ErrorResponse.fail(f"{entity_name} (ID: {item_id}) 未找到", status.HTTP_404_NOT_FOUND)
            return SuccessResponse.ok_message(message=f"{entity_name} (ID: {item_id}) 删除成功。")

    return router