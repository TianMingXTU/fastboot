# 🚀 FastBoot - 极简 · 异步 · 高效的 Python 后端开发框架

FastBoot 是基于 **FastAPI + Tortoise ORM** 构建的极简异步开发框架，  
借鉴了 Spring Boot 的模块化思想，  
致力于让 Python 后端开发实现**开箱即用、结构清晰、扩展自然**的体验。

---

## ✨ 核心特性

- ✅ 全链路异步支持（Controller / Service / Repository）
- ✅ 自动扫描并挂载自定义 Service / Repository
- ✅ 动态生成 Pydantic 请求体（Create/Update）
- ✅ 通用标准 CRUD 接口一键继承
- ✅ 统一响应格式（SuccessResponse / ErrorResponse）
- ✅ 全局异常处理与日志系统
- ✅ 简洁灵活的项目结构，支持中大型项目扩展
- ✅ 配套前端测试中心（浏览器直接调试所有接口）
- ✅ 配套异步接口自动化测试脚本

---

## 📂 项目结构概览

```bash
fastboot/
├── application.py         # FastBootApp应用启动器
├── config.py               # 配置管理器
├── database.py             # 数据库连接管理（Tortoise ORM）
├── exception_handler.py    # 全局异常捕获
├── logger.py               # 日志系统
├── router_scanner.py       # 自动路由扫描注册器
├── service_manager.py      # Service自动挂载器
├── repository_manager.py   # Repository自动挂载器
└── crud/
    ├── base_model.py       # 通用模型基类
    ├── base_repository.py  # 通用异步Repository
    ├── base_service.py     # 通用异步Service
    ├── base_controller.py  # 通用异步Controller
    └── request_generator.py# 动态生成Pydantic请求体
models/
├── base_model.py           # ORM模型基类
└── product_model.py        # 示例商品模型
repositories/
└── product_repository.py   # 示例商品Repository
services/
└── product_service.py      # 示例商品Service
controllers/
└── product_controller.py   # 示例商品Controller
config/
└── config.yaml             # 配置文件（DB等）
html_tests/
└── test_fastboot.html      # 浏览器可视化接口测试中心
tests/
└── test_product_api.py     # 后端异步API测试脚本
main.py                     # 应用启动入口
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

推荐使用 `uv` 加速：

```bash
pip install uv
uv pip install -r requirements.txt
```

---

### 2. 运行项目

```bash
python main.py
```

默认启动在：

```
http://localhost:8080
```

---

### 3. 快速测试接口

- 浏览器打开：
  ```
  html_tests/test_fastboot.html
  ```
- 快速体验创建商品、查询商品、更新商品、删除商品等标准接口

✅ 自动显示接口日志，便于调试！

---

### 4. 后端接口异步测试

```bash
python tests/test_product_api.py
```

自动执行创建、查询、搜索、删除的完整异步接口测试。

✅ 异步 httpx 测试客户端  
✅ 全链路验证接口正确性  
✅ 支持黑盒测试（只测API，不动数据库连接）

---

## 🧠 核心设计理念

- 模块化：
  - 每个模块独立职责（config、router、exception、database）
- 标准化：
  - 统一返回结构、统一错误处理、统一日志风格
- 异步化：
  - Controller → Service → Repository → Model 全链路 async/await
- 可扩展：
  - 易于添加新模型、新模块、新中间件
- 开箱即用：
  - 快速开发标准API，不需要重复劳动

---

## 📋 统一接口返回格式

成功返回：

```json
{
  "success": true,
  "data": {...},
  "error": null
}
```

失败返回：

```json
{
  "success": false,
  "data": null,
  "error": "错误信息"
}
```

---

## 🔥 开发计划（Roadmap）

| 阶段       | 内容                                  |
|:-----------|:-------------------------------------|
| v2.0       | 完成基础异步版CRUD框架                  |
| v2.1       | 标准化分页查询返回结构                  |
| v2.2       | 集成Redis异步缓存（aioredis）            |
| v2.3       | 支持异步任务调度（定时任务/异步消息）    |
| v2.4       | 集成权限系统（JWT + RBAC）              |
| v2.5       | Docker一键部署，分环境切换（dev/test/prod）|
| v2.6       | 发布正式版至PyPI开源                     |

---

## ❤️ 特别感谢

- [FastAPI](https://fastapi.tiangolo.com/)
- [Tortoise ORM](https://tortoise-orm.readthedocs.io/)
- [Spring Boot](https://spring.io/projects/spring-boot)（架构设计灵感）

---

## 📌 备注

- 本项目适用于中小型项目、管理后台、内部系统、快速原型开发。
- 如果追求超高并发或极致分布式微服务，需要做进一步扩展优化。

---

# ✨ 项目口号

> 让 Python 后端开发，也能拥有 Spring Boot 的丝滑体验！

---

# 📢 贡献 & 支持

如果你喜欢这个项目，欢迎 Star ⭐、Fork 🍴、提交 PR 📬！

一起来完善 FastBoot，一起进步成长！

---