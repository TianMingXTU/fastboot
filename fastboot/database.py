# fastboot/database.py (已重构)
from tortoise import Tortoise, models
from typing import List, Type
from fastboot.config import ConfigManager, DatabaseSettings as PydanticDatabaseSettings
from fastboot.logger import Logger

class Database:
    """Tortoise ORM 异步数据库管理器"""

    def __init__(self, config_manager: ConfigManager, logger: Logger):
        self.config_manager = config_manager
        self.logger = logger
        self.db_url: str | None = None
        # === 变更点: 不再存储字符串路径，而是直接存储模型类 ===
        self.registered_models: List[Type[models.Model]] = []

    # === 变更点: 方法签名和逻辑都已改变 ===
    def initialize(self, model_classes: List[Type[models.Model]]):
        """
        初始化数据库配置，并直接接收生成的模型类列表。
        :param model_classes: 由 EntityRegistry 动态生成的 Tortoise ORM 模型类列表。
        """
        db_settings_model = self.config_manager.get_section("db")
        
        if not isinstance(db_settings_model, PydanticDatabaseSettings):
            raise RuntimeError("未找到或配置格式错误的数据库连接配置。")
        
        try:
            self.db_url = db_settings_model.build_db_url()
        except ValueError as e:
            raise RuntimeError(f"构建数据库URL失败: {e}")
        
        if not model_classes:
            self.logger.warning("警告：初始化数据库时未提供任何业务模型类！")
        
        # 直接存储模型类
        self.registered_models = model_classes
        
        model_names = [m.__name__ for m in self.registered_models]
        self.logger.info(f"[FastBoot] 数据库配置已初始化。URL: '{self.db_url}', 模型类: {model_names}")

    async def connect(self):
        """异步连接数据库并按需生成/检查schemas"""
        if self.db_url is None:
            raise RuntimeError("数据库URL未正确初始化。")

        self.logger.info(f"[FastBoot] 尝试连接数据库: {self.db_url}")
        
        try:
            # === 变更点: 直接将模型类列表传递给 Tortoise.init ===
            await Tortoise.init(
                db_url=self.db_url,
                modules={"models": self.registered_models} # 直接使用模型类列表
            )
            
            db_settings = self.config_manager.get_section("db")
            generate_schemas_flag = getattr(db_settings, 'generate_schemas', False)

            if generate_schemas_flag:
                self.logger.info("[FastBoot] 正在生成/检查数据库表结构 (generate_schemas)...")
                await Tortoise.generate_schemas()
            else:
                self.logger.info("[FastBoot] 跳过 generate_schemas (根据配置或默认值)。")

            self.logger.info("[FastBoot] 数据库连接成功，数据表结构已准备就绪。")
        except Exception as e:
            self.logger.error(f"[FastBoot] 数据库连接或表结构生成失败: {e}", exc_info=True)
            raise

    async def close(self):
        """异步关闭数据库连接"""
        self.logger.info("[FastBoot] 准备关闭数据库连接...")
        await Tortoise.close_connections()
        self.logger.info("[FastBoot] 数据库连接已关闭。")
