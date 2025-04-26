# fastboot/service_manager.py
"""ServiceManager模块：负责扫描并管理所有Service组件。"""

import os
import importlib
import inspect
from fastboot.logger import Logger

class ServiceManager:
    """Service组件管理器，用于扫描并提供Service实例。"""

    def __init__(self):
        """初始化Service管理器，自动扫描并注册所有Service。"""
        self.logger = Logger()
        self.services = {}
        self.scan_services()

    def scan_services(self):
        """扫描services目录，自动导入并注册所有Service类。"""
        services_path = os.path.join(os.getcwd(), "services")

        if not os.path.exists(services_path):
            self.logger.warning(f"Services directory not found: {services_path}")
            return

        for filename in os.listdir(services_path):
            if filename.endswith(".py") and not filename.startswith("_"):
                module_name = filename[:-3]
                module_path = f"services.{module_name}"

                try:
                    module = importlib.import_module(module_path)
                except Exception as e:
                    self.logger.error(f"Failed to import service module {module_path}: {e}")
                    continue

                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # 只注册当前模块定义的类
                    if obj.__module__ == module_path:
                        service_instance = obj()
                        self.services[name] = service_instance
                        self.logger.info(f"Service registered: {name}")

    def get_service(self, name: str):
        """根据类名获取对应的Service实例。

        Args:
            name (str): Service类名（注意大小写）。

        Returns:
            object: 对应的Service实例。

        Raises:
            KeyError: 如果Service不存在。
        """
        if name in self.services:
            return self.services[name]
        else:
            raise KeyError(f"Service '{name}' not found.")
