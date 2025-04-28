# fastboot/database.py

from tortoise import Tortoise
from fastboot.config import ConfigManager
from fastboot.logger import Logger

class Database:
    """Tortoise ORM 异步数据库管理器"""

    def __init__(self):
        self.config = ConfigManager()
        self.logger = Logger()
        self.db_config = None

    def initialize(self):
        """初始化数据库配置，不连接"""
        self.db_config = self.config.get("database")
        if not self.db_config:
            raise RuntimeError("未找到数据库配置")
        self.logger.info("[FastBoot] 数据库配置已初始化")

    async def connect(self):
        """异步连接数据库"""
        if self.db_config is None:
            raise RuntimeError("数据库未初始化，请先调用 initialize()")

        await Tortoise.init(
            db_url=self._build_db_url(),
            modules={"models": ["models"]}  # 自动扫描 models 目录下所有Tortoise模型
        )
        await Tortoise.generate_schemas()
        self.logger.info("[FastBoot] 数据库连接成功，数据表创建完成")

    async def close(self):
        """异步关闭数据库连接"""
        await Tortoise.close_connections()
        self.logger.info("[FastBoot] 数据库连接已关闭")

    def _build_db_url(self):
        """根据配置文件构建数据库URL"""
        db_type = self.db_config.get("type", "mysql")
        user = self.db_config["username"]
        password = self.db_config["password"]
        host = self.db_config["host"]
        port = self.db_config["port"]
        database = self.db_config["name"]
        return f"{db_type}://{user}:{password}@{host}:{port}/{database}"
