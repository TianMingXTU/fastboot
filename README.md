# FastBoot

FastBoot是一个基于FastAPI构建的轻量级快速开发框架，  
借鉴了Spring Boot的模块化与自动化思想，专注于提升后端开发效率与规范性。

---

## ✨ 特性 Features

- 统一应用启动器（FastBootApp）
- 自动加载配置（ConfigManager）
- 自动连接数据库与建表（Database）
- 自动注册Service与Controller（ServiceManager / RouterScanner）
- 统一异常处理（ExceptionHandler）
- 结构清晰的MVC分层（Controller → Service → Repository → Model）
- 完善的日志系统（Logger）

---
## 📂 项目结构

```plaintext
fastboot/
    application.py        # 应用启动器
    config.py              # 配置管理
    database.py            # 数据库连接与建表
    exception_handler.py   # 统一异常处理
    logger.py              # 日志系统
    router_scanner.py      # 路由扫描器
    service_manager.py     # 服务注册器
controllers/
    user_controller.py     # 用户控制器示例
services/
    user_service.py        # 用户业务逻辑示例
repositories/
    user_repository.py     # 用户数据访问层示例
models/
    user_model.py          # 用户ORM模型
    model_register.py      # 模型注册表（用于建表）
config/
    config.yaml            # 应用配置文件
tests/
    test_user_api.py       # 接口测试脚本
main.py                    # 应用启动入口
```
---

## 🚀 快速开始 Quick Start

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 启动应用：

```bash
python main.py
```

默认地址：http://localhost:8000

---

## 🔥 接口示例 API Demo

- 注册用户：`POST /user/register`
- 查询用户：`GET /user/info/{user_id}`

详见 `tests/test_user_api.py` 示例脚本。

---

## 🛠️ 待优化计划 TODO

- 自动依赖注入支持
- 多环境配置管理
- 完善生命周期事件（on_startup, on_shutdown）
- Docker容器部署
- PyPI发布与版本管理

---