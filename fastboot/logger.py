# fastboot/logger.py
"""Logger模块：负责初始化和管理FastBoot项目的统一日志系统。"""

import logging
import sys
from fastboot.config import ConfigManager


class Logger:
    """FastBoot日志管理器，负责统一日志输出，防止多次初始化。"""

    COLOR_MAP = {
        "DEBUG": "\033[94m",
        "INFO": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "RESET": "\033[0m",
    }

    _logger_instance = None  # 单例缓存

    def __new__(cls, *args, **kwargs):
        """保证Logger是单例，不会多次创建。"""
        if not cls._logger_instance:
            cls._logger_instance = super(Logger, cls).__new__(cls)
        return cls._logger_instance

    def __init__(self):
        """初始化Logger模块，只设置一次Handler。"""
        if hasattr(self, "_initialized") and self._initialized:
            return  # 防止重复初始化

        self.config = ConfigManager()
        log_level_str = self.config.get("logging.level", default="INFO").upper()
        log_level = getattr(logging, log_level_str, logging.INFO)

        self.logger = logging.getLogger("FastBootLogger")
        self.logger.setLevel(log_level)

        if not self.logger.hasHandlers():  # 🔥 核心防止重复添加Handler
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(funcName)s:%(lineno)d]: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        self._initialized = True  # 标记已初始化

    def _colorize(self, level: str, message: str) -> str:
        color = self.COLOR_MAP.get(level, "")
        reset = self.COLOR_MAP["RESET"]
        return f"{color}{message}{reset}"

    def debug(self, message: str):
        self.logger.debug(self._colorize("DEBUG", message))

    def info(self, message: str):
        self.logger.info(self._colorize("INFO", message))

    def warning(self, message: str):
        self.logger.warning(self._colorize("WARNING", message))

    def error(self, message: str):
        self.logger.error(self._colorize("ERROR", message))
