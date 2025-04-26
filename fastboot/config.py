"""配置管理模块，用于加载和访问应用配置。

这个模块提供了ConfigManager类，用于从YAML文件中加载配置，
并支持通过点分隔的方式访问嵌套配置项。

典型用法:
    config = ConfigManager()
    db_host = config.get("database.host")
    port = config.get("app.port", default=8000)
"""

import os
import yaml

class ConfigManager:
    """配置管理器，负责加载和访问YAML格式的配置文件。

    这个类提供了一个统一的配置访问接口，支持默认值和点分隔的键访问。
    配置文件默认位于项目根目录的config/config.yaml。

    Attributes:
        _config_data (dict): 存储加载的配置数据的字典。

    Raises:
        FileNotFoundError: 当配置文件不存在时抛出。
    """

    def __init__(self, config_path=None):
        """初始化配置管理器。

        Args:
            config_path (str, optional): 配置文件的路径。
                如果为None，则使用默认路径 "config/config.yaml"。

        Raises:
            FileNotFoundError: 如果指定的配置文件不存在。
        """
        if config_path is None:
            config_path = os.path.join(os.getcwd(), "config", "config.yaml")
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found at: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            self._config_data = yaml.safe_load(f) or {}

    def get(self, key: str, default=None):
        """获取配置值。

        支持使用点号分隔的键来访问嵌套的配置值。

        Args:
            key (str): 配置键，支持点号分隔，如 "database.host"。
            default (Any, optional): 当键不存在时返回的默认值。

        Returns:
            Any: 配置值，如果键不存在且提供了默认值，则返回默认值。

        Raises:
            KeyError: 如果键不存在且没有提供默认值。

        Examples:
            >>> config = ConfigManager()
            >>> config.get("database.host")
            'localhost'
            >>> config.get("not.exist", default="N/A")
            'N/A'
        """
        keys = key.split(".")
        value = self._config_data

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            if default is not None:
                return default
            else:
                raise KeyError(f"Config key '{key}' not found.")
