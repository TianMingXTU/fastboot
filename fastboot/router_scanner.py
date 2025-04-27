# fastboot/router_scanner.py
"""RouterScanner模块：负责扫描并注册所有Controller路由（兼容通用CRUD体系）"""

import os
import importlib
import inspect
from fastapi import APIRouter
from fastboot.logger import Logger


# controller、get、post 装饰器保持不变
def controller(prefix: str):
    """给类打上路由前缀标记"""

    def wrapper(cls):
        cls.__route_prefix__ = prefix
        return cls

    return wrapper


def get(path: str):
    """给方法打上GET路由标记"""

    def wrapper(func):
        func.__method__ = "GET"
        func.__path__ = path
        return func

    return wrapper


def post(path: str):
    """给方法打上POST路由标记"""

    def wrapper(func):
        func.__method__ = "POST"
        func.__path__ = path
        return func

    return wrapper


class RouterScanner:
    """自动扫描controllers目录下的Controller并注册路由"""

    def __init__(self, app):
        self.app = app
        self.logger = Logger()
        self.scan_controllers()

    def scan_controllers(self):
        """扫描controllers目录并注册路由"""
        controllers_path = os.path.join(os.getcwd(), "controllers")

        if not os.path.exists(controllers_path):
            self.logger.warning(f"Controllers目录未找到：{controllers_path}")
            return

        total_controllers = 0

        for filename in os.listdir(controllers_path):
            if filename.endswith(".py") and not filename.startswith("_"):
                module_name = filename[:-3]
                module_path = f"controllers.{module_name}"

                try:
                    module = importlib.import_module(module_path)
                except Exception as e:
                    self.logger.error(
                        f"导入控制器模块失败：{module_path}，错误信息：{e}"
                    )
                    continue

                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if obj.__module__ == module_path:
                        self.register_routes(obj)
                        total_controllers += 1

        self.logger.info(f"控制器扫描完成，总计注册 {total_controllers} 个控制器。")

    def register_routes(self, controller_cls):
        """注册单个控制器的路由"""
        prefix = getattr(controller_cls, "__route_prefix__", None)
        if prefix is None:
            return  # 不是Controller类，跳过

        router = APIRouter()
        controller_instance = controller_cls()

        registered_routes = 0

        for name, method in inspect.getmembers(controller_instance, inspect.ismethod):
            http_method = getattr(method, "__method__", None)
            path = getattr(method, "__path__", None)

            if http_method and path:
                full_path = f"{prefix}{path}"
                if http_method == "GET":
                    router.get(path)(method)
                elif http_method == "POST":
                    router.post(path)(method)

                self.logger.info(f"已注册路由: {http_method} {full_path}")
                registered_routes += 1

        self.app.include_router(router, prefix=prefix)
        self.logger.info(
            f"控制器 {controller_cls.__name__} 注册完成，共 {registered_routes} 个路由。"
        )
