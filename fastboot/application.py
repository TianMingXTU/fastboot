# fastboot/application.py
from fastapi import FastAPI
from fastboot.config import ConfigManager
from fastboot.logger import Logger
from fastboot.router_scanner import RouterScanner
from fastboot.service_manager import ServiceManager
from fastboot.exception_handler import ExceptionHandler
from fastboot.database import Database

class FastBootApp:
    def __init__(self):
        self.app = FastAPI()
        self.config = ConfigManager()
        self.logger = Logger()
        self.database = Database()   # 初始化数据库连接
        self.services = ServiceManager()
        self.router_scanner = RouterScanner(self.app)
        self.exception_handler = ExceptionHandler(self.app)
        # 从配置文件中读取host和port
        self.host = self.config.get("app.host", "0.0.0.0")
        self.port = self.config.get("app.port", 8000)

    def __del__(self):
        """析构函数，确保数据库连接被正确关闭"""
        if hasattr(self, 'database'):
            self.database.close()

    def run(self, host=None, port=None):
        """启动FastBoot应用。

        Args:
            host (str, optional): 服务器主机地址. 默认使用配置文件中的值或"0.0.0.0"
            port (int, optional): 服务器端口. 默认使用配置文件中的值或8000
        """
        import uvicorn
        self.logger.info("FastBoot应用初始化完成，正在准备启动服务器...")
        
        # 使用传入的参数或默认值
        final_host = host if host is not None else self.host
        final_port = port if port is not None else self.port
        
        self.logger.info(f"服务器将在 {final_host}:{final_port} 启动")
        uvicorn.run(self.app, host=final_host, port=final_port)
