# fastboot/application.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastboot.config import ConfigManager
from fastboot.logger import Logger
from fastboot.router_scanner import RouterScanner
from fastboot.service_manager import ServiceManager
from fastboot.exception_handler import ExceptionHandler
from fastboot.database import Database

class FastBootApp:
    def __init__(self):
        self.database = Database()
        self.config = ConfigManager()
        self.logger = Logger()
        self.services = ServiceManager()

        # 初始化数据库配置
        self.database.initialize()

        # 创建FastAPI实例，挂载lifespan
        self.app = FastAPI(lifespan=self._lifespan)

        self.host = self.config.get("app.host", "0.0.0.0")
        self.port = self.config.get("app.port", 8000)

        # 注册中间件、扫描路由等
        self._setup()

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI):
        """应用生命周期管理"""
        self.logger.info("[FastBoot] 启动中：连接数据库...")
        await self.database.connect()
        yield
        self.logger.info("[FastBoot] 关闭中：断开数据库...")
        await self.database.close()

    def _setup(self):
        from fastapi.middleware.cors import CORSMiddleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.router_scanner = RouterScanner(self.app)
        self.exception_handler = ExceptionHandler(self.app)

    def run(self, host=None, port=None):
        import uvicorn
        self.logger.info("[FastBoot] 应用初始化完成，准备启动服务器...")
        final_host = host if host else self.host
        final_port = port if port else self.port
        uvicorn.run(self.app, host=final_host, port=final_port)
