"""ServiceManager模块：自动扫描services/，管理自定义和内置Service"""

import os
import importlib
import inspect
from fastboot.logger import Logger
from fastboot.crud.base_service import BaseService

class ServiceManager:
    """Service组件管理器，自动发现用户自定义Service，优先使用"""

    def __init__(self):
        self.logger = Logger()
        self.services = {}
        self.scan_builtin_services()
        self.scan_user_services()

    def scan_builtin_services(self):
        """注册内置BaseService（仅注册）"""
        self.services["BaseService"] = BaseService

    def scan_user_services(self):
        """扫描services/目录，注册用户自定义Service"""
        services_path = os.path.join(os.getcwd(), "services")
        if not os.path.exists(services_path):
            self.logger.info("No user services found, using built-in services only.")
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
                    if obj.__module__ == module_path:
                        self.services[name] = obj
                        self.logger.info(f"Custom Service registered: {name}")

    def get_service_class(self, model_cls):
        """根据模型推断Service类，优先使用用户自定义"""
        service_name = f"{model_cls.__name__}Service"
        return self.services.get(service_name, self.services.get("BaseService"))
