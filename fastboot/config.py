# fastboot/config.py
"""配置管理模块，使用Pydantic-Settings实现强类型配置加载，支持多种数据库。"""

import os
import yaml
from typing import Any, Optional, Dict, List, Union
from pydantic import Field, BaseModel as PydanticBaseModel, validator, field_validator

from pydantic_settings import BaseSettings, SettingsConfigDict

# --- 定义配置模型 ---
class AppSettings(PydanticBaseModel):
    """应用核心配置"""
    name: str = "FastBootApp"
    version: str = "0.3.1" # 版本更新示例
    host: str = "0.0.0.0"
    port: int = 8000
    modules_package: str = "modules"
    log_level: str = Field("INFO", description="日志级别, 例如: DEBUG, INFO, WARNING, ERROR")
    env: str = Field("dev", description="运行环境 (dev, test, prod)")
    enable_class_router_scanner: bool = Field(False, description="是否启用基于类装饰器的路由扫描器")
    description: Optional[str] = Field(None, description="应用的OpenAPI描述")
    # secret_key: str = "YOUR_VERY_SECRET_KEY_CHANGE_ME" # 用于JWT等
    # debug: bool = False # 通常根据 env 自动设置

class DatabaseSettings(PydanticBaseModel):
    """数据库连接配置"""
    type: str = Field("sqlite", description="数据库类型 (sqlite, mysql, postgresql)")
    name: str = Field("./fastboot_app.db", description="数据库名称或SQLite文件路径") # 对于SQLite是路径，对于其他是DB名
    
    # 以下字段对于非SQLite类型通常是必需的
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None # 敏感信息，推荐通过环境变量设置
    
    # (可选) 是否在应用启动时自动生成schemas (通常由迁移工具管理)
    generate_schemas: bool = Field(False, description="是否在启动时自动生成数据库表结构（开发用）")

    @field_validator('type')
    @classmethod
    def type_must_be_supported(cls, v: str) -> str:
        """校验数据库类型是否受支持"""
        supported_types = ["sqlite", "mysql", "postgresql"] # 可以扩展
        if v.lower() not in supported_types:
            raise ValueError(f"不支持的数据库类型: '{v}'. 支持的类型有: {', '.join(supported_types)}")
        return v.lower()

    def build_db_url(self) -> str:
        """根据配置构建数据库连接URL"""
        if self.type == "sqlite":
            # 对于SQLite，name通常是文件路径。确保路径正确。
            # 如果 name 不是绝对路径，可以考虑将其解析为相对于项目根目录的路径。
            db_path = self.name
            if not os.path.isabs(db_path) and not db_path.startswith(os.sep) and not db_path.startswith(":") : # 兼容 windows 盘符
                 # 假设此 config.py 在 fastboot_project_root/fastboot/config.py
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                db_path = os.path.join(project_root, db_path)
                # print(f"数据库调试: SQLite路径解析为: {db_path}") # 用于调试
            return f"sqlite://{db_path}"
        
        # 对于 MySQL 和 PostgreSQL 等其他类型
        required_for_network_db = {
            "username": self.username,
            "password": self.password,
            "host": self.host,
            "port": self.port,
            "name": self.name # 这里的 name 是数据库的名称
        }
        missing = [key for key, value in required_for_network_db.items() if value is None]
        if missing:
            raise ValueError(
                f"数据库类型 '{self.type}' 的连接参数不完整，缺少以下必需参数: {', '.join(missing)}。 "
                "请在配置文件或环境变量中提供这些值。"
            )
        
        return f"{self.type}://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"

class CORSSettings(PydanticBaseModel):
    """CORS跨域配置"""
    allow_origins: List[str] = ["*"]
    allow_credentials: bool = True
    allow_methods: List[str] = ["*"]
    allow_headers: List[str] = ["*"]

# --- 主配置类 ---
class GlobalSettings(BaseSettings):
    """应用全局配置模型"""
    model_config = SettingsConfigDict(
        env_prefix='FASTBOOT_',
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
        case_sensitive=False
    )

    app: AppSettings = Field(default_factory=AppSettings)
    # 'db' 字段现在直接使用增强后的 DatabaseSettings
    db: DatabaseSettings = Field(default_factory=DatabaseSettings) 
    cors: CORSSettings = Field(default_factory=CORSSettings)
    # 兼容旧的 logging.level, 但推荐使用 app.log_level
    logging: Dict[str, Any] = Field(default_factory=lambda: {"level": "INFO"}) 

    @classmethod
    def load_settings(cls, yaml_config_path: Optional[str] = None) -> 'GlobalSettings':
        """
        加载配置。顺序: Pydantic模型默认值 -> YAML -> .env -> 环境变量。
        """
        init_kwargs = {}
        final_yaml_path = yaml_config_path
        
        if final_yaml_path and os.path.exists(final_yaml_path):
            try:
                with open(final_yaml_path, 'r', encoding='utf-8') as f:
                    yaml_data = yaml.safe_load(f)
                    if yaml_data and isinstance(yaml_data, dict):
                        init_kwargs.update(yaml_data)
                        # print(f"调试：从YAML '{final_yaml_path}' 加载的配置: {yaml_data}") # 用于调试
            except Exception as e:
                print(f"警告：无法加载或解析YAML配置文件 '{final_yaml_path}': {e}")
        else:
            print(f"调试：YAML配置文件 '{final_yaml_path}' 未找到或未指定，将跳过YAML加载。")
            
        # Pydantic-Settings 会自动处理环境变量和 .env 文件，并覆盖 init_kwargs 中的同名顶层键
        # 对于嵌套模型，环境变量需要遵循特定格式，例如 FASTBOOT_APP_PORT 或 FASTBOOT_DB_USERNAME
        return cls(**init_kwargs)

class ConfigManager:
    """配置管理器，提供对全局配置的访问。"""
    _settings: GlobalSettings

    def __init__(self, config_file_path: Optional[str] = None):
        """
        初始化配置管理器并加载配置。
        """
        actual_config_path = config_file_path
        if actual_config_path is None:
            actual_config_path = os.getenv("FASTBOOT_CONFIG_PATH", "config/config.yaml")
            if not os.path.isabs(actual_config_path) and not actual_config_path.startswith(os.sep):
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                actual_config_path = os.path.join(project_root, actual_config_path)
        
        # print(f"ConfigManager: 最终尝试加载的YAML路径: {actual_config_path}") # 用于调试
        self._settings = GlobalSettings.load_settings(yaml_config_path=actual_config_path)
        # print(f"ConfigManager: 配置加载完成。应用名: {self._settings.app.name}, DB类型: {self._settings.db.type}") # 用于调试

    def get_settings(self) -> GlobalSettings:
        """返回完整的强类型全局配置对象。"""
        return self._settings

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        根据点分隔的路径获取配置项。例如: "app.host" 或 "db.port"
        """
        keys = key_path.split('.')
        value_node = self._settings
        try:
            for key in keys:
                if isinstance(value_node, PydanticBaseModel):
                    value_node = getattr(value_node, key)
                elif isinstance(value_node, dict): # 如果配置中某部分是普通字典
                    value_node = value_node.get(key)
                    if value_node is None: # 如果在字典中未找到
                        if key == keys[-1] and default is not None: # 如果是最后一个键且有默认值
                            return default
                        raise KeyError # 中间键找不到，路径无效
                else:
                    if default is not None: return default
                    raise TypeError(f"无法在非结构化类型 ({type(value_node)}) 中查找键 '{key}'")
            return value_node
        except (AttributeError, KeyError, TypeError):
            if default is not None:
                return default
            raise KeyError(f"配置项 '{key_path}' 未找到，且未提供默认值。")

    def get_section(self, section_name: str) -> Optional[PydanticBaseModel | Dict]:
        """获取整个配置节，例如 'app' 或 'db'"""
        try:
            return getattr(self._settings, section_name)
        except AttributeError:
            return None