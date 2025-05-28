# 🚀 FastBoot X - 下一代Python异步后端框架 (SST与自动化驱动)

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python version"></a>
  <a href="#"><img src="https://img.shields.io/badge/FastAPI-latest-green.svg" alt="FastAPI"></a>
  <a href="#"><img src="https://img.shields.io/badge/Tortoise%20ORM-latest-orange.svg" alt="Tortoise ORM"></a>
  <a href="#"><img src="https://img.shields.io/badge/License-MIT-brightgreen.svg" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Build-passing-success.svg" alt="Build Status"></a>
</p>

**FastBoot X** 是一个基于 **FastAPI + Tortoise ORM** 构建的、具备高度自动化和AI原生演进能力的下一代Python异步后端框架。它通过一系列颠覆性的设计（如“单一事实来源”、“资源处理器”、“智能方法路由”），将开发者从繁琐的样板代码和配置工作中彻底解放，让您可以前所未有地专注于业务逻辑的创新与实现。

> **为极致的开发体验而生。定义您的业务，剩下的交给 FastBoot X。**

---

## 📖 核心理念：我们为何与众不同？

在开启一个新项目时，开发者常常陷入一个困境：是选择Django那样“大而全”但略显笨重的框架，还是选择Flask/FastAPI那样“小而美”但需要自己构建大量架构的框架？FastBoot X 旨在成为第三种选择：**一个既有强大工程化能力，又有极致开发效率的智能框架。**

我们的所有创新，都围绕着一个核心目标：**最大化业务开发效率，最小化技术实现成本。**

* **单一事实来源 (SST)**: 拒绝在ORM模型、Pydantic Schema、API接口之间复制粘贴。数据结构只定义一次，所有技术层面的实现由框架自动生成。
* **资源即服务**: 传统的`Controller-Service-Repository`分层在很多场景下是过度设计。我们将业务逻辑和数据操作内聚于一个“资源处理器”，它才是业务的核心。
* **约定优于配置**: 我们坚信，清晰的命名约定胜过繁琐的装饰器和配置文件。框架应足够智能，能从开发者的代码中“读懂”其意图。
* **声明式扩展**: 框架应提供正交的、非侵入式的能力扩展方式。无论是缓存还是权限，都应像“插件”一样即插即用，而不是污染核心业务代码。
* **智能数据访问**: 数据查询不应是拼凑ORM语句，而应是声明式的、如同调用一个普通函数一样自然和类型安全。

---

## ⚔️ 框架对比：FastBoot X 的革命性优势

为了更直观地展示 FastBoot X 的先进性，我们将其与当前主流的开发模式进行直接对比：

| 开发维度 | 传统模式 (如 Django REST Framework) | 现代模式 (原生 FastAPI) | **FastBoot X (新范式)** |
| :--- | :--- | :--- | :--- |
| **数据定义** | **分散割裂**。需要在`models.py`中定义ORM模型，在`serializers.py`中定义序列化器，两者字段大量重复。 | **部分重复**。需要在`models.py`中定义ORM模型，在`schemas.py`中定义Pydantic DTO，存在重复劳动和不一致的风险。 | **🔥 单一事实来源 (SST)**。仅需在`entity.py`中定义唯一的实体类，ORM模型和所有API DTOs由框架**自动生成**，完全消除冗余。 |
| **业务逻辑层** | **僵化分层**。`Service`层和`Repository`层（或`Manager`）职责不清，常常只是简单的方法调用转发，徒增文件数量和复杂度。 | **模式自选**。开发者需要自行设计和实现Service/Repository层，缺乏统一的最佳实践，项目规模化后容易混乱。 | **🔥 资源处理器**。用一个内聚的`ResourceHandler`取代僵化的分层，自带CRUD能力，逻辑清晰，职责明确。 |
| **CRUD API实现** | **配置驱动**。需要编写一个`ViewSet`类，并配置`queryset`, `serializer_class`等多个属性。 | **手动编写**。需要为`create`, `get`, `list`, `update`, `delete`等每个操作手动编写一个完整的路径操作函数。 | **🔥 完全自动化**。只需定义`Entity`和`Handler`，**无需编写任何代码**，框架自动生成一套完整、高效的RESTful CRUD API。 |
| **自定义API实现** | **需要装饰器**。通过在`ViewSet`中使用`@action`装饰器来添加自定义路由。 | **需要装饰器**。手动使用`@router.get`, `@router.post`等装饰器来定义和注册路由。 | **🔥 智能方法路由**。只需在`Handler`中添加一个符合命名约定的方法（如`get_user_profile`），**无需任何装饰器**，框架自动为其创建并注册API端点。 |
| **异步支持** | **有限/复杂**。Django 4.x后开始支持异步视图，但ORM和大部分生态仍是同步阻塞的，全链路异步改造困难。 | **原生支持**。FastAPI天生就是异步框架，性能卓越。 | **🔥 全面拥抱异步**。继承FastAPI和Tortoise ORM的全部异步优势，并确保框架自身所有组件均为异步设计。 |
| **开发效率** | **中等**。有强大的后台管理和生态，但样板代码多，心智负担重。 | **高**（对于小项目）。但随着项目变大，架构成本和重复劳动会显著增加。 | **🔥 极致**。通过最大程度的自动化，将开发新模块的时间从数小时缩短到几分钟，让开发者能将95%以上的精力聚焦于业务逻辑。 |

---

## ✨ 核心功能与未来规划

### 已实现的核心功能

* **SST实体定义**: 使用 `@entity` 和 `Field` 函数统一数据描述。
* **模型与DTO自动生成**: 框架在启动时，根据实体定义自动生成Tortoise ORM模型和Create, Update, Response三种Pydantic DTO。
* **自动化资源处理器**: 使用 `@resource_handler` 绑定实体，`BaseResourceHandler` 提供开箱即用的异步CRUD能力。
* **全自动路由系统**: 无论是标准CRUD还是自定义业务方法，均可实现“零配置”自动生成API端点。
* **完整的核心套件**: 包含强类型配置、日志、标准化响应和全局异常处理。

### 近期规划 (技术预览)

我们正在积极研发以下两大功能，它们将进一步巩固FastBoot X的领先地位：

* **声明式钩子 (Declarative Hooks)**:
    * **愿景**: 引入一套`@use(Hook)`装饰器系统，允许开发者像搭积木一样，为任意API组合所需的企业级功能，如权限校验、数据缓存、事务管理等，实现业务逻辑与横切关注点的完美分离。
    * **示例**:
      ```python
      from fastboot.hooks import use, Cache, RequiresRoles

      @use(RequiresRoles("admin"))
      @use(Cache(ttl=60))
      async def get_system_report(self):
          # ... 业务逻辑 ...
          pass
      ```

* **JIT查询引擎**:
    * **愿景**: 让数据查询彻底告别手写ORM语句。开发者只需在处理器中定义一个符合命名约定的方法**签名**，框架便能在运行时为其自动生成并执行最优的数据库查询。
    * **示例**:
      ```python
      # 只需定义方法签名，框架自动实现
      async def find_by_author_and_published_year_between(
          self, author: str, start_year: int, end_year: int
      ) -> list[Book]: ...
      ```

---

## 📂 项目结构 (最终版)

```plaintext
your_fastboot_project_root/
├── fastboot/                     # 框架核心代码目录
│   ├── entity/                   # 【核心】SST实体相关
│   │   ├── decorators.py
│   │   ├── fields.py
│   │   └── registry.py
│   ├── resource/                 # 【核心】资源处理器与路由相关
│   │   ├── handler.py
│   │   └── router_factory.py
│   ├── application.py            # FastBootApp: 自动化核心协调器
│   ├── config.py                 # ...其他核心工具...
│   └── ...
├── modules/                      # 业务模块根目录
│   └── product/                  # 示例：一个业务模块
│       ├── entity.py             # 【必须】定义Product实体
│       └── handler.py            # 【必须】定义Product的资源处理器
├── config/                       # 配置文件目录
├── main.py                       # 应用启动入口
└── ...
```

---

## 核心组件详解 (`fastboot/` 目录)

(此部分将对每个核心组件进行详尽的功能和职责说明)

* **`fastboot/entity/registry.py (EntityRegistry)`**:
    这是框架的“大脑”和“工厂”。它是一个在应用启动时被实例化的全局单例。
    1.  **发现与注册**: 它通过`importlib`和`pkgutil`扫描`modules_package`配置的包路径，找到所有定义了`entity.py`和`handler.py`的模块并加载它们。这会触发`@entity`和`@resource_handler`装饰器的执行，从而将实体类和处理器类及其绑定关系全部注册到`EntityRegistry`的内部字典中（如`self._entities`, `self._handlers`）。
    2.  **动态生成ORM模型**: 注册完成后，它会遍历`self._entities`。对每一个实体类，它会读取其类名、`_meta_table_name`属性以及所有用`Field()`定义的字段。然后，它使用`type()`内置函数，动态地创建一个继承自`tortoise.models.Model`的新类。它会将解析出的字段（如`tortoise.fields.CharField(...)`的实例）作为新类的属性，并为其创建一个`Meta`内部类来指定表名，最终将这个新创建的ORM模型类存入`self._orm_models`字典。
    3.  **动态生成Pydantic DTO**: 类似地，它会再次遍历实体类，并根据`Field()`定义中的类型信息、是否可空、以及预留的`api_mutable`等元数据，使用`pydantic.create_model`函数，为每个实体动态创建三种不同的`BaseModel`子类：`CreateSchema`（不含主键，部分字段必填）、`UpdateSchema`（不含主键，所有字段可选）、`ResponseSchema`（包含所有可暴露字段），并将它们存入`self._pydantic_schemas`字典。

* **`fastboot/application.py (FastBootApp)`**:
    这是框架的总指挥。它的 `_discover_and_register_resource_handlers` 方法是自动化路由的核心。
    1.  **获取绑定对**: 它向`EntityRegistry`查询所有已知的“实体-处理器”绑定关系。
    2.  **生成标准路由**: 对每一个“绑定对”，它调用`resource.router_factory.create_generic_crud_router`函数，传入实体类和处理器类。该工厂函数再从`EntityRegistry`获取对应的ORM模型和DTOs，并生成一个包含5个标准CRUD端点的`APIRouter`实例，然后由`FastBootApp`将其挂载到主应用上。
    3.  **生成自定义路由**: 它使用`inspect.getmembers`和`inspect.signature`来反射每一个处理器类，找出所有不属于`BaseResourceHandler`基类、且有特定动词前缀的自定义方法。它会解析方法名来构造URL路径，解析函数签名来确定路径参数、查询参数和请求体。然后，它会动态创建一个包装函数（wrapper），该函数的签名与用户的自定义方法兼容，内部则通过`Depends`注入处理器实例并调用原始方法。最后，它使用`app.add_api_route`将这个包装函数注册为一个新的API端点。

(其他组件如 `config.py`, `database.py` 等的详细说明可在此处补充)

---

## 业务模块开发：极致体验

开发一个完整的`Product`模块，从定义到API可用，只需两步：

**1. 定义实体 (`modules/product/entity.py`)**:
```python
from fastboot.entity.decorators import entity
from fastboot.entity.fields import Field
from tortoise import fields as tfields

@entity
class Product:
    id: int = Field(tfields.IntField, pk=True)
    name: str = Field(tfields.CharField, max_length=200, db_index=True)
    price: float = Field(tfields.DecimalField, max_digits=10, decimal_places=2)
```

**2. 定义处理器 (`modules/product/handler.py`)**:
```python
from .entity import Product
from fastboot.resource.handler import resource_handler, BaseResourceHandler

@resource_handler(Product)
class ProductHandler(BaseResourceHandler[Product]):
    # 自定义一个API，用于按名称模糊搜索商品
    async def get_search(self, keyword: str):
        # 自动生成API: GET /products/search?keyword=xxx
        return await self.orm_model.filter(name__icontains=keyword)
```
**完成！** 启动应用，您将自动获得以下API：
* `POST /products`
* `GET /products`
* `GET /products/{id}`
* `PUT /products/{id}`
* `DELETE /products/{id}`
* `GET /products/search`

---
### **🛠️ 安装与运行**

按照以下步骤，您可以在几分钟内快速启动并运行一个由FastBoot X驱动的项目。

#### **1. 环境要求**

  * **Python**: 3.9+ (推荐 3.10 或更高版本)
  * **依赖管理器**: [pip](https://pip.pypa.io/en/stable/) 或 [Poetry](https://python-poetry.org/)

#### **2. 安装依赖**

1.  在您的项目根目录下，创建一个 `requirements.txt` 文件，并填入核心依赖：

    ```txt
    # requirements.txt

    # 核心框架
    fastapi
    uvicorn[standard]

    # 数据库 ORM
    tortoise-orm

    # 数据库驱动 (根据您的选择)
    # asyncmy  # for MySQL/MariaDB
    # asyncpg  # for PostgreSQL
    aiosqlite # for SQLite

    # 数据校验与配置
    pydantic
    pydantic-settings
    pyyaml

    # 数据库迁移工具
    aerich
    ```

2.  打开终端，运行以下命令安装所有依赖：

    ```bash
    pip install -r requirements.txt
    ```

#### **3. 项目配置**

1.  在项目根目录下创建 `config` 文件夹。

2.  在 `config/` 目录中创建您的配置文件，例如 `config.yaml` (默认) 和 `config.dev.yaml` (开发环境)。

    **`config/config.yaml` 示例:**

    ```yaml
    app:
      name: "MyFastBootXApp"
      version: "1.0.0"
      host: "0.0.0.0"
      port: 8000
      # 【重要】指定框架扫描业务模块的基础包名
      modules_package: "modules" 
      log_level: "INFO"

    db:
      type: "sqlite" # 可选: sqlite, mysql, postgresql
      name: "./app_database.db" # SQLite文件路径或实际数据库名
      # generate_schemas: true # 开发时可设为true，让Tortoise自动创建表结构（生产环境推荐用迁移管理）

      # --- MySQL/PostgreSQL 示例 ---
      # host: "localhost"
      # port: 3306
      # username: "myuser"
      # password: "mypassword"

    cors:
      allow_origins: ["*"] # 生产环境建议设置为您的前端地址，如 ["http://localhost:3000"]
      allow_credentials: true
      allow_methods: ["*"]
      allow_headers: ["*"]
    ```

3.  (可选但推荐) 在项目根目录创建 `.env` 文件，用于存放敏感信息或覆盖YAML中的配置。**请务必将`.env`文件添加到`.gitignore`中。**

    **.env 示例:**

    ```env
    FASTBOOT_DB_PASSWORD=a_very_secret_password
    FASTBOOT_APP_PORT=8001
    ```

#### **4. 数据库迁移 (使用 Aerich)**

这是关键一步，它确保您的数据库表结构与您的 `Entity` 定义保持同步。

1.  **准备迁移配置文件**:
    由于FastBoot X是在运行时动态生成ORM模型的，我们需要一种方式让Aerich能够访问到这些生成的模型类。推荐的做法是在项目根目录的 `main.py` 文件中同时处理应用启动和Aerich配置。

    **`main.py` (用于Aerich的版本):**

    ```python
    # main.py
    from fastboot.application import FastBootApp

    # 【关键步骤】必须先实例化FastBootApp，以触发实体发现和ORM模型的动态生成
    app_builder = FastBootApp() 

    # 为Aerich提供所需的配置字典
    TORTOISE_ORM_CONFIG = {
        "connections": {"default": app_builder.database.db_url}, # 从已初始化的app_builder中获取DB URL
        "apps": {
            "models": {
                # 直接从实体注册中心获取所有动态生成的模型类列表
                "models": app_builder.entity_registry.get_all_orm_models(), 
                "default_connection": "default",
            }
        },
    }

    # ... 应用运行逻辑将在下一步中定义 ...
    ```

2.  **初始化Aerich**:
    在终端中运行以下命令，它会创建一个`migrations`目录和一个`aerich.ini`配置文件。

    ```bash
    aerich init -t main.TORTOISE_ORM_CONFIG
    ```

3.  **生成并应用迁移**:

      * **首次迁移**:
        ```bash
        aerich migrate --name initial
        aerich upgrade
        ```
      * **后续修改**: 每当您修改了任何 `entity.py` 文件（例如添加/删除字段）后，重复以下步骤：
        ```bash
        # 为您的更改创建一个新的迁移文件
        aerich migrate --name "a_descriptive_migration_name"

        # 将更改应用到数据库
        aerich upgrade
        ```

#### **5. 创建并运行应用**

现在，我们来完成 `main.py` 文件，让它可以启动Web服务。

**`main.py` (最终版):**

```python
# main.py
from fastboot.application import FastBootApp
import uvicorn

# --- Aerich 配置部分 (可保留或放在单独的 aerich_config.py 中) ---
# 为了让 `aerich init` 命令能工作，需要一个临时的app_builder实例来生成配置
temp_app_builder = FastBootApp() 
TORTOISE_ORM_CONFIG = {
    "connections": {"default": temp_app_builder.database.db_url},
    "apps": {
        "models": {
            "models": temp_app_builder.entity_registry.get_all_orm_models(),
            "default_connection": "default",
        }
    },
}
# --- 结束 Aerich 配置部分 ---


# --- 应用启动逻辑 ---
# 创建用于运行的最终App实例
app_builder = FastBootApp()
fastapi_app = app_builder.app

if __name__ == "__main__":
    uvicorn.run(
        fastapi_app, 
        host=app_builder.host, 
        port=app_builder.port,
        # 【重要】禁止Uvicorn接管日志配置，以使用我们自定义的Logger
        log_config=None 
    )
```

#### **6. 启动项目！**

一切准备就绪！在终端中运行：

```bash
python main.py
```

您应该会看到来自FastBoot自定义Logger的启动信息，提示服务器正在运行，例如：

```log
INFO: [FastBoot] 应用 'MyFastBootXApp' 准备就绪，将在 http://0.0.0.0:8000 启动服务器...
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     [FastBoot] 应用生命周期事件：启动中...
INFO:     [FastBoot] 数据库连接成功。
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

现在，您可以打开浏览器或API工具，访问 `http://127.0.0.1:8000/docs` 来查看由框架自动生成的、包含所有标准和自定义API的Swagger文档了。

---

## 开发计划 (Roadmap)

* **第一阶段：核心架构重构 (已完成)**
    * ✅ 单一事实来源 (SST) 体系
    * ✅ 资源处理器模式
    * ✅ 全自动化的标准及自定义方法路由
* **第二阶段：核心体验增强 (近期规划)**
    * ⏳ **声明式钩子 (Declarative Hooks)**
    * ⏳ **JIT查询引擎**
* **第三阶段：生态系统与企业功能**
    * [ ] 标准化分页响应
    * [ ] 缓存、安全、异步任务、WebSockets等。
* **第四阶段：AI原生演进**
    * [ ] AI原生开发助手CLI工具。

---
## 贡献与致谢

我们热烈欢迎任何形式的贡献！
**致谢**: FastAPI, Tortoise ORM, Pydantic, 以及所有开源社区的贡献者。