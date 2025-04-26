# fastboot/router_scanner.py
"""RouterScanner模块：负责扫描并注册所有Controller路由。"""

import os
import importlib
import inspect
from fastapi import APIRouter
from fastboot.logger import Logger

# 临时简单模拟装饰器（后续可以改进）
def controller(prefix: str):
    """给类打上路由前缀的标记。"""
    def wrapper(cls):
        cls.__route_prefix__ = prefix
        return cls
    return wrapper

def get(path: str):
    """给方法打上GET请求的标记。"""
    def wrapper(func):
        func.__method__ = "GET"
        func.__path__ = path
        return func
    return wrapper

def post(path: str):
    """给方法打上POST请求的标记。"""
    def wrapper(func):
        func.__method__ = "POST"
        func.__path__ = path
        return func
    return wrapper

class RouterScanner:
    """路由扫描器，负责自动注册controllers目录下的路由。"""

    def __init__(self, app):
        """初始化RouterScanner。

        Args:
            app (FastAPI): FastAPI应用实例。
        """
        self.app = app
        self.logger = Logger()
        self.scan_controllers()

    def scan_controllers(self):
        """扫描controllers目录并注册路由。"""
        controllers_path = os.path.join(os.getcwd(), "controllers")

        if not os.path.exists(controllers_path):
            self.logger.warning(f"Controllers directory not found: {controllers_path}")
            return

        for filename in os.listdir(controllers_path):
            if filename.endswith(".py") and not filename.startswith("_"):
                module_name = filename[:-3]
                module_path = f"controllers.{module_name}"

                try:
                    module = importlib.import_module(module_path)
                except Exception as e:
                    self.logger.error(f"Failed to import controller module {module_path}: {e}")
                    continue

                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # 只注册本模块定义的类
                    if obj.__module__ == module_path:
                        self.register_routes(obj)

    def register_routes(self, controller_cls):
        """注册单个Controller的路由。

        Args:
            controller_cls (type): 控制器类。
        """
        prefix = getattr(controller_cls, "__route_prefix__", None)
        if prefix is None:
            return  # 不是Controller类，跳过

        router = APIRouter()
        controller_instance = controller_cls()

        for name, method in inspect.getmembers(controller_instance, inspect.ismethod):
            http_method = getattr(method, "__method__", None)
            path = getattr(method, "__path__", None)

            if http_method and path:
                if http_method == "GET":
                    router.get(path)(method)
                elif http_method == "POST":
                    router.post(path)(method)

                self.logger.info(f"Route registered: {http_method} {prefix}{path}")

        self.app.include_router(router, prefix=prefix)
