# fastboot/database.py

from peewee import MySQLDatabase
from models.base_model import database_proxy  # 修改导入路径
from models.model_register import MODELS
from fastboot.config import ConfigManager
from fastboot.logger import Logger

class Database:
    """数据库初始化器"""

    def __init__(self):
        config = ConfigManager()
        self.logger = Logger()
        db_config = config.get("database")
        
        # 创建数据库连接
        self.db = MySQLDatabase(
            db_config["name"],
            host=db_config["host"],
            port=db_config["port"],
            user=db_config["username"],
            password=db_config["password"],
            charset='utf8mb4'
        )
        
        # 初始化数据库代理
        database_proxy.initialize(self.db)
        
        # 初始化数据库连接
        self.db.connect()
        self.logger.info("数据库连接成功")
        
        # 创建表
        self.create_tables()
        self.logger.info(f"成功创建数据表：{[model.__name__ for model in MODELS]}")

    def create_tables(self):
        """自动建表，如果表存在则跳过。"""
        self.db.create_tables(MODELS, safe=True)

    def close(self):
        """关闭数据库连接"""
        if not self.db.is_closed():
            self.db.close()
