# fastboot/logger.py
"""Logger模块：负责初始化和管理FastBoot项目的统一日志系统。"""

import logging
import sys
from typing import Optional, Dict # <--- 添加了这行导入

class Logger:
    """
    FastBoot日志管理器，负责统一日志输出。
    通过在 FastBootApp 中创建单例并传递给其他组件来使用。
    """

    COLOR_MAP = {
        "DEBUG": "\033[94m",    # 蓝色
        "INFO": "\033[92m",     # 绿色
        "WARNING": "\033[93m",  # 黄色
        "ERROR": "\033[91m",    # 红色
        "CRITICAL": "\033[91m\033[1m", # 加粗红色
        "RESET": "\033[0m",     # 重置颜色
    }
    
    # 存储已初始化的logger实例，键是logger的名称，值是logger对象
    # 使用 Dict[str, logging.Logger] 进行类型提示
    _initialized_loggers: Dict[str, logging.Logger] = {} 

    def __init__(self, name: str = "FastBootApp", level: str = "INFO", enable_colors: bool = True):
        """
        初始化Logger实例。
        :param name: 日志记录器的名称。
        :param level: 日志级别字符串 (例如 "INFO", "DEBUG")。
        :param enable_colors: 是否启用控制台颜色输出。
        """
        self.logger_name = name
        self.log_level_str = level.upper()
        self.enable_colors = enable_colors
        
        # 获取或创建logger实例
        if name not in Logger._initialized_loggers:
            logger_instance = logging.getLogger(name)
            log_level_int = getattr(logging, self.log_level_str, logging.INFO)
            logger_instance.setLevel(log_level_int)

            # 仅当logger没有处理器时才添加，防止重复
            if not logger_instance.hasHandlers():
                console_handler = logging.StreamHandler(sys.stdout)
                formatter = logging.Formatter(
                    "[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(funcName)s:%(lineno)d]: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
                console_handler.setFormatter(formatter)
                logger_instance.addHandler(console_handler)
            
            Logger._initialized_loggers[name] = logger_instance
        
        self._logger = Logger._initialized_loggers[name]

    def _colorize(self, level_name: str, message: str) -> str:
        """如果启用了颜色，则为消息添加颜色代码。"""
        if not self.enable_colors or not sys.stdout.isatty(): # 仅当输出到tty时才启用颜色
            return message
        color = self.COLOR_MAP.get(level_name.upper(), "") #确保level_name是大写以匹配COLOR_MAP的键
        reset = self.COLOR_MAP["RESET"]
        return f"{color}{message}{reset}"

    def debug(self, message: str, *args, **kwargs):
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(self._colorize("DEBUG", message), *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        if self._logger.isEnabledFor(logging.INFO):
            self._logger.info(self._colorize("INFO", message), *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        if self._logger.isEnabledFor(logging.WARNING):
            self._logger.warning(self._colorize("WARNING", message), *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        if self._logger.isEnabledFor(logging.ERROR):
            self._logger.error(self._colorize("ERROR", message), *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        if self._logger.isEnabledFor(logging.CRITICAL):
            self._logger.critical(self._colorize("CRITICAL", message), *args, **kwargs)