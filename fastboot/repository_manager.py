"""RepositoryManager模块：自动扫描repositories/，管理自定义和内置Repository"""

import os
import importlib
import inspect
from fastboot.logger import Logger
from fastboot.crud.base_repository import BaseRepository

class RepositoryManager:
    """Repository组件管理器，自动发现用户自定义Repository，优先使用"""

    def __init__(self):
        self.logger = Logger()
        self.repositories = {}
        self.scan_builtin_repositories()
        self.scan_user_repositories()

    def scan_builtin_repositories(self):
        """注册内置BaseRepository"""
        self.repositories["BaseRepository"] = BaseRepository

    def scan_user_repositories(self):
        """扫描repositories/目录，注册用户自定义Repository"""
        repositories_path = os.path.join(os.getcwd(), "repositories")
        if not os.path.exists(repositories_path):
            self.logger.info("No user repositories found, using built-in repositories only.")
            return

        for filename in os.listdir(repositories_path):
            if filename.endswith(".py") and not filename.startswith("_"):
                module_name = filename[:-3]
                module_path = f"repositories.{module_name}"

                try:
                    module = importlib.import_module(module_path)
                except Exception as e:
                    self.logger.error(f"Failed to import repository module {module_path}: {e}")
                    continue

                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if obj.__module__ == module_path:
                        self.repositories[name] = obj
                        self.logger.info(f"Custom Repository registered: {name}")

    def get_repository_class(self, model_cls):
        """根据模型推断Repository类，优先使用用户自定义"""
        repository_name = f"{model_cls.__name__}Repository"
        return self.repositories.get(repository_name, self.repositories.get("BaseRepository"))
