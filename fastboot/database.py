# fastboot/database.py

from peewee import MySQLDatabase
from models.base_model import database_proxy
from models.model_register import MODELS
from fastboot.config import ConfigManager
from fastboot.logger import Logger

class Database:
    """数据库管理器"""

    def __init__(self):
        self.config = ConfigManager()
        self.logger = Logger()
        self.db = None  # 先不连接，只定义

    def initialize(self):
        """初始化数据库连接对象，不实际连接"""
        db_config = self.config.get("database")
        self.db = MySQLDatabase(
            db_config["name"],
            host=db_config["host"],
            port=db_config["port"],
            user=db_config["username"],
            password=db_config["password"],
            charset='utf8mb4'
        )
        database_proxy.initialize(self.db)
        self.logger.info("[FastBoot] 数据库对象已初始化")

    def connect(self):
        """连接数据库，并建表"""
        if self.db is None:
            raise RuntimeError("数据库未初始化，请先调用 initialize()")
        
        if self.db.is_closed():
            self.db.connect()
            self.logger.info("[FastBoot] 数据库连接成功")
        else:
            self.logger.warning("[FastBoot] 数据库已连接，无需重复连接")

        self.create_tables()

    def create_tables(self):
        """建表操作"""
        if self.db:
            self.db.create_tables(MODELS, safe=True)
            self.logger.info(f"[FastBoot] 成功创建数据表：{[model.__name__ for model in MODELS]}")

    def close(self):
        """关闭数据库连接"""
        if self.db and not self.db.is_closed():
            self.db.close()
            self.logger.info("[FastBoot] 数据库连接已关闭")
        else:
            self.logger.warning("[FastBoot] 数据库连接已关闭或不存在")
