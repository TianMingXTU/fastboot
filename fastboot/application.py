# fastboot/application.py (最终版，实现智能方法路由)
"""
FastBoot 应用核心类 (FastBootApp)。
负责初始化和组装框架的各个组件，包括配置、日志、数据库、
路由、中间件和异常处理。
"""
import inspect
import re
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from pydantic import BaseModel
import importlib
import os
from typing import Optional, Any, Callable

# 核心框架组件导入
from fastboot.config import ConfigManager, GlobalSettings
from fastboot.logger import Logger
from fastboot.database import Database
from fastboot.exception_handler import ExceptionHandler
from fastboot.entity.registry import EntityRegistry, default_registry
from fastboot.resource.router_factory import create_generic_crud_router
from fastboot.resource.handler import BaseResourceHandler # 导入基类用于方法排除

class FastBootApp:
    """
    FastBoot 应用核心类。
    """
    app: FastAPI
    config_manager: ConfigManager
    settings: GlobalSettings
    logger: Logger
    database: Database
    exception_handler: ExceptionHandler
    modules_base_package_name: str
    host: str
    port: int
    entity_registry: EntityRegistry
    
    def __init__(self, config_file_path: Optional[str] = None):
        """
        初始化FastBootApp实例。
        """
        if config_file_path is None:
            config_file_path = os.getenv("FASTBOOT_CONFIG_PATH", "config/config.yaml")
            if not os.path.isabs(config_file_path):
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                config_file_path = os.path.join(project_root, config_file_path)
        
        self.config_manager = ConfigManager(config_file_path=config_file_path)
        self.settings = self.config_manager.get_settings()
        
        self.logger = Logger(name=self.settings.app.name, level=self.settings.app.log_level)
        self.logger.info(f"配置文件 '{config_file_path}' 已加载。")

        self.modules_base_package_name = self.settings.app.modules_package
        self.logger.info(f"[FastBoot] 应用模块基础包设置为: '{self.modules_base_package_name}'")

        self.logger.info("[FastBoot] 初始化实体注册中心...")
        self.entity_registry = default_registry
        self.entity_registry.logger = self.logger
        self.entity_registry.discover_entities(self.modules_base_package_name)
        
        model_classes_for_db = self.entity_registry.get_all_orm_models()
        self.database = Database(config_manager=self.config_manager, logger=self.logger)
        self.database.initialize(model_classes=model_classes_for_db)
        
        self.app = FastAPI(
            title=self.settings.app.name,
            version=self.settings.app.version,
            lifespan=self._lifespan,
            description=self.settings.app.description,
        )

        self.host = self.settings.app.host
        self.port = self.settings.app.port

        self._setup_core_components()

        self.app.state.config_manager = self.config_manager
        self.app.state.logger = self.logger
        self.app.state.settings = self.settings
        self.app.state.entity_registry = self.entity_registry

        self.logger.info(f"[FastBoot] 应用 '{self.app.title} v{self.app.version}' 初始化流程完成。")

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI):
        self.logger.info("[FastBoot] 应用生命周期事件：启动中...")
        await self.database.connect()
        yield
        self.logger.info("[FastBoot] 应用生命周期事件：关闭中...")
        await self.database.close()

    def _discover_and_register_resource_handlers(self):
        """
        【自动驾驶PRO模式】扫描所有已注册的实体，找到它们的处理器，
        并自动为它们创建和注册【标准CRUD路由】和【自定义方法路由】。
        """
        self.logger.info("自动路由注册：开始扫描资源处理器...")
        
        base_handler_methods = {name for name, func in inspect.getmembers(BaseResourceHandler, predicate=inspect.isfunction)}
        all_entities = self.entity_registry.get_all_entities()
        
        for entity_cls in all_entities:
            handler_cls = self.entity_registry.get_handler_for_entity(entity_cls)
            if not handler_cls:
                self.logger.debug(f"自动路由注册：实体 '{entity_cls.__name__}' 未找到对应的资源处理器，跳过。")
                continue

            # 1. 创建并注册标准的CRUD路由
            crud_router = create_generic_crud_router(entity_cls=entity_cls, service_cls=handler_cls)
            prefix = f"/{entity_cls.__name__.lower()}s"
            tags = [entity_cls.__name__]
            self.app.include_router(crud_router, prefix=prefix, tags=tags)
            self.logger.info(f"自动路由注册：已为实体 '{entity_cls.__name__}' 创建并注册【标准CRUD】路由组。")

            # 2. 扫描并注册自定义方法路由
            for method_name, method_func in inspect.getmembers(handler_cls, predicate=inspect.isfunction):
                if method_name.startswith('_') or method_name in base_handler_methods:
                    continue # 跳过私有方法和基类方法

                # 解析HTTP动词
                http_verb = ""
                if method_name.startswith("get_"): http_verb = "GET"
                elif method_name.startswith("post_") or method_name.startswith("create_"): http_verb = "POST"
                elif method_name.startswith("put_") or method_name.startswith("update_"): http_verb = "PUT"
                elif method_name.startswith("patch_"): http_verb = "PATCH"
                elif method_name.startswith("delete_"): http_verb = "DELETE"
                else: continue # 如果没有匹配的动词前缀，则跳过

                # 解析路径和路径参数
                path_part = re.sub(f"^{http_verb.lower()}_", "", method_name) # 移除动词前缀
                path_params = re.findall(r"\{(\w+)\}", path_part)
                final_path = re.sub(r"\{(\w+)\}", r"{\1}", path_part.replace('_', '-'))
                
                # 创建一个注入了handler的端点函数
                def create_endpoint(handler_method: Callable) -> Callable:
                    async def endpoint_wrapper(*args, handler_instance: Any = Depends(handler_cls), **kwargs):
                        # FastAPI会将路径参数、查询参数等自动匹配到kwargs中
                        return await handler_method(handler_instance, *args, **kwargs)
                    
                    # 关键：复制原始方法的签名，以便FastAPI正确解析参数
                    original_sig = inspect.signature(handler_method)
                    # 移除 'self' 参数
                    params_without_self = list(original_sig.parameters.values())[1:]
                    # 更新wrapper的签名
                    endpoint_wrapper.__signature__ = original_sig.replace(parameters=params_without_self) # type: ignore
                    return endpoint_wrapper

                custom_endpoint = create_endpoint(method_func)

                # 将自定义端点添加到主应用中
                self.app.add_api_route(
                    f"{prefix}/{final_path}",
                    custom_endpoint,
                    methods=[http_verb],
                    tags=tags,
                    summary=f"自定义操作: {method_name}"
                )
                self.logger.info(f"自动路由注册：已为方法 '{method_name}' 创建并注册【自定义】路由: {http_verb} {prefix}/{final_path}")

    def _setup_core_components(self):
        """注册核心组件"""
        self.logger.info("[FastBoot] 开始设置核心组件...")
        
        from fastapi.middleware.cors import CORSMiddleware
        self.app.add_middleware(CORSMiddleware, **self.settings.cors.model_dump())
        self.logger.info("CORS中间件已注册。")

        self.exception_handler = ExceptionHandler(self.app, self.logger)

        # 启用全新的、自动化的路由注册方式
        self._discover_and_register_resource_handlers()
        
        self.logger.info("[FastBoot] 核心组件设置完成。")

    def run(self, host: Optional[str] = None, port: Optional[int] = None):
        """启动Uvicorn服务器"""
        import uvicorn
        final_host = host if host is not None else self.host
        final_port = port if port is not None else self.port
        self.logger.info(f"[FastBoot] 应用 '{self.app.title}' 准备就绪，将在 http://{final_host}:{final_port} 启动服务器...")
        uvicorn.run(self.app, host=final_host, port=final_port, log_config=None)
