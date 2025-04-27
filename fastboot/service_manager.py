# fastboot/service_manager.py
"""ServiceManager模块：用于管理Service实例（目前基于通用CRUD体系，暂不自动扫描）"""

from fastboot.logger import Logger


class ServiceManager:
    """Service组件管理器，统一管理注册的Service实例。"""

    def __init__(self):
        """初始化Service管理器（当前无自动扫描）。"""
        self.logger = Logger()
        self.services = {}

    def register_service(self, name: str, service_instance):
        """手动注册一个Service实例（预留扩展功能）。

        Args:
            name (str): Service名称
            service_instance (object): Service实例
        """
        self.services[name] = service_instance
        self.logger.info(f"Service registered manually: {name}")

    def get_service(self, name: str):
        """根据Service名称获取Service实例。

        Args:
            name (str): Service类名（注意大小写）

        Returns:
            object: Service实例

        Raises:
            KeyError: 如果找不到Service
        """
        if name in self.services:
            return self.services[name]
        else:
            raise KeyError(f"Service '{name}' not found.")
