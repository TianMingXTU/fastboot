# manage.py
import typer
import os
import importlib
import inspect
from pathlib import Path
from typing import Type, Any, List, Tuple, Optional, Dict # 确保 Dict 也导入了
from tortoise.models import Model
from tortoise import fields as tortoise_fields
from pydantic import BaseModel

# --- 辅助函数和模板字符串 (与之前版本相同，这里省略以保持简洁) ---
# Pydantic Schema 字段类型映射 (可以根据需要扩展)
PYDANTIC_TYPE_MAP = {
    tortoise_fields.IntField: "int",
    tortoise_fields.BigIntField: "int",
    tortoise_fields.SmallIntField: "int",
    tortoise_fields.CharField: "str",
    tortoise_fields.TextField: "str",
    tortoise_fields.BooleanField: "bool",
    tortoise_fields.DecimalField: "float", # Pydantic 通常用 float 表示 Decimal，或使用 Decimal 类型
    tortoise_fields.FloatField: "float",
    tortoise_fields.DateField: "date", # from datetime import date
    tortoise_fields.DatetimeField: "datetime", # from datetime import datetime
    tortoise_fields.JSONField: "Dict[str, Any]", # from typing import Dict, Any
    tortoise_fields.UUIDField: "UUID", # from uuid import UUID
}
PYTHON_TO_PYDANTIC_IMPORT_MAP = {
    "date": "from datetime import date",
    "datetime": "from datetime import datetime",
    "UUID": "from uuid import UUID",
    "Dict": "from typing import Dict", # 确保 Dict 在这里
    "Any": "from typing import Any",
    "List": "from typing import List",
    "Optional": "from typing import Optional",
    "Decimal": "from decimal import Decimal",
}

SCHEMA_TEMPLATE = """\
# {module_path}/schemas.py
from pydantic import BaseModel, Field
# --- AUTO-GENERATED IMPORTS START ---
{imports}
# --- AUTO-GENERATED IMPORTS END ---

class {model_name}Base(BaseModel):
{base_fields}

class {model_name}Create({model_name}Base):
    pass

class {model_name}Update(BaseModel): # 更新时所有字段可选
{update_fields}

class {model_name}Schema({model_name}Base):
{response_id_field}
    # (可选) 添加 ORM 模型中其他希望在响应中包含的字段，例如 created_at, updated_at
    # created_at: datetime
    # updated_at: datetime

    class Config:
        from_attributes = True # Pydantic V2 (旧版 orm_mode = True)
"""

REPOSITORY_TEMPLATE = """\
# {module_path}/repositories.py
from typing import Optional, List # 添加 typing 导入
from fastboot.crud.base_repository import BaseRepositoryDI # 确保路径正确
from .models import {model_orm_name} # 导入当前模块的ORM模型

class {model_name}Repository(BaseRepositoryDI[{model_orm_name}]):
    model_class = {model_orm_name} # 指定此仓库操作的ORM模型类

    # --- (可选) 在这里添加特定于 {model_name} 的自定义数据访问方法 ---
    # async def find_by_custom_field(self, field_value: str) -> Optional[{model_orm_name}]:
    #     return await self.model_class.get_or_none(custom_field=field_value)
"""

SERVICE_TEMPLATE = """\
# {module_path}/services.py
from fastapi import Depends, HTTPException, status
from typing import List, Optional

from fastboot.crud.base_service import BaseServiceDI # 确保路径正确
from .models import {model_orm_name}
from .repositories import {model_name}Repository
from .schemas import {model_name}Create, {model_name}Update, {model_name}Schema

class {model_name}Service(BaseServiceDI[{model_orm_name}, {model_name}Repository]):
    # BaseServiceDI 的 __init_subclass__ 会尝试自动注入仓库，
    # 因此通常不需要显式定义 __init__ 方法，除非需要自定义初始化逻辑。
    # 如果需要自定义，请取消注释下面的代码：
    # def __init__(self, repo: {model_name}Repository = Depends({model_name}Repository)):
    #     super().__init__(repo)

    # --- (可选) 重写或扩展通用的CRUD方法以添加特定业务逻辑 ---
    # async def create(self, create_data_dict: dict) -> {model_orm_name}:
    #     # 示例：创建前的特定校验
    #     # if "name" in create_data_dict and hasattr(self._repo, 'find_by_name') and await self._repo.find_by_name(create_data_dict.get("name")): # 假设有find_by_name和name字段
    #     #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{model_name_base} name '{{create_data_dict.get(\"name\")}}' already exists.")
    #     return await super().create(create_data_dict)

    # --- (可选) 在这里添加特定于 {model_name} 的自定义业务逻辑方法 ---
    # async def get_special_{model_name_plural}(self) -> List[{model_name}Schema]:
    #     # items_orm = await self._repo.some_custom_query()
    #     # return [({model_name}Schema.model_validate(item)) for item in items_orm]
    pass
"""

ROUTING_INIT_TEMPLATE = """\
# {module_path}/__init__.py
from fastapi import APIRouter, Depends # 添加 Depends (如果自定义端点需要)

# 1. 导入您的通用CRUD路由工厂函数
from fastboot.crud.generic_router_factory import create_generic_crud_router # 确保路径正确

# 2. 导入当前模块的组件
from .models import {model_orm_name}
from .services import {model_name}Service
from .schemas import {model_name}Schema, {model_name}Create, {model_name}Update

# 3. 使用工厂函数为 {model_name} 创建标准的CRUD路由
_crud_router = create_generic_crud_router(
    model_cls={model_orm_name},
    service_cls={model_name}Service,
    create_schema={model_name}Create,
    update_schema={model_name}Update,
    response_schema={model_name}Schema
)

# 4. 创建并导出此业务模块的主 APIRouter 实例
router = APIRouter(
    prefix="/{module_name_plural}",  # 模块下所有路由的统一前缀 (例如 /books)
    tags=["{model_name_tag}"]    # OpenAPI文档中的标签 (例如 Books)
)

router.include_router(_crud_router) # 包含由工厂生成的CRUD路由

# (可选) 在此模块的 router 上定义其他自定义的、非CRUD的API端点
# @router.get("/special-info", summary="获取特殊{model_name_tag}信息")
# async def get_special_data(service: {model_name}Service = Depends({model_name}Service)):
#     # return await service.get_special_{model_name_plural}()
#     return {{"message": "特殊{model_name_tag}数据"}}
"""

# --- Typer 应用和命令 ---
app = typer.Typer(
    help="FastBoot 命令行脚手架工具，用于快速生成业务模块的CRUD基础代码。",
    add_completion=False # 可以禁用shell补全提示，如果不需要
)

def _get_pydantic_field_definition(field_name: str, field_obj: tortoise_fields.Field) -> Tuple[str, str, List[str]]:
    """
    根据Tortoise字段生成Pydantic字段定义字符串 (用于Base和Update Schema) 和所需导入。
    返回: (base_field_definition, update_field_definition, imports_needed)
    """
    field_imports = set()
    # 修正：使用 field_obj.field_type 来获取字段的原始Tortoise类型
    pydantic_type_py = PYDANTIC_TYPE_MAP.get(type(field_obj.field_type), "Any") 
    
    if pydantic_type_py == "Any" and "Any" in PYTHON_TO_PYDANTIC_IMPORT_MAP:
        field_imports.add(PYTHON_TO_PYDANTIC_IMPORT_MAP["Any"])
    elif pydantic_type_py in PYTHON_TO_PYDANTIC_IMPORT_MAP:
        field_imports.add(PYTHON_TO_PYDANTIC_IMPORT_MAP[pydantic_type_py])

    is_pk = field_obj.pk
    is_nullable = field_obj.null
    has_default = field_obj.default is not None
    
    if is_pk: # 主键不应由用户在创建时提供
        return "", "", list(field_imports)

    # Base Schema 字段定义 (通常用于Create)
    base_pydantic_type_str = pydantic_type_py
    base_default_value_str = "..." # Pydantic V2中表示必需字段 (除非可空或有默认)

    if is_nullable or has_default:
        base_pydantic_type_str = f"Optional[{pydantic_type_py}]"
        if "Optional" in PYTHON_TO_PYDANTIC_IMPORT_MAP: # 确保 Optional 被导入
             field_imports.add(PYTHON_TO_PYDANTIC_IMPORT_MAP["Optional"])
        base_default_value_str = "None"
    
    base_field_definition = f"    {field_name}: {base_pydantic_type_str} = {base_default_value_str}"
    
    # Update Schema 字段定义 (所有字段都是Optional且默认为None)
    update_pydantic_type_str = f"Optional[{pydantic_type_py}]"
    if "Optional" in PYTHON_TO_PYDANTIC_IMPORT_MAP and pydantic_type_py != "Any": # 避免 Optional[Any]
         field_imports.add(PYTHON_TO_PYDANTIC_IMPORT_MAP["Optional"])
    elif pydantic_type_py == "Any": # Optional[Any] 通常就是 Any
        update_pydantic_type_str = "Any"


    update_field_definition = f"    {field_name}: {update_pydantic_type_str} = None"
    
    return base_field_definition, update_field_definition, list(field_imports)


@app.command(name="scaffold") # <--- 明确指定命令名称
def scaffold_cmd( # <--- 修改函数名以避免与可能的模块名冲突，并添加 ctx
    ctx: typer.Context, # <--- 关键修改：添加 typer.Context 作为第一个参数
    model_path: str,    # <--- 这是我们的主要位置参数
    module_root: str = typer.Option(
        "modules", 
        "--module-root", "-mr",
        help="业务模块的根目录 (相对于项目根目录)",
        show_default=True
    ),
    overwrite: bool = typer.Option(
        False, 
        "--overwrite", "-o", 
        help="如果文件已存在，则覆盖它们。",
        show_default=False
    )
):
    """
    为指定的Tortoise ORM模型类自动生成CRUD相关的Schemas, Repository, Service和路由配置文件。
    
    MODEL_PATH: 要生成CRUD组件的ORM模型类的Python路径 (例如: 'modules.product.models.ProductOrm')
    
    用户需要先在对应的 models.py 文件中定义好ORM模型。
    
    例如:\n
    python manage.py scaffold modules.book.models.BookOrm
    """
    # typer.echo(f"CTX command: {ctx.command.name}, params: {ctx.params}") # 调试信息
    typer.echo(f"ℹ️  接收到模型路径: {model_path}")

    try:
        module_name_str, model_class_name = model_path.rsplit('.', 1)
    except ValueError:
        typer.secho(f"错误: 模型路径 '{model_path}' 格式不正确。应为 'package.subpackage.module.{model_class_name}'。", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    try:
        model_module = importlib.import_module(module_name_str)
        model_cls: Type[Model] = getattr(model_module, model_class_name)
    except ImportError:
        typer.secho(f"错误: 无法导入模型模块 '{module_name_str}'。请确保路径正确且模块在PYTHONPATH中。", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    except AttributeError:
        typer.secho(f"错误: 在模块 '{module_name_str}' 中未找到模型类 '{model_class_name}'。", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    if not issubclass(model_cls, Model):
        typer.secho(f"错误: '{model_path}' 指向的类 '{model_class_name}' 不是 Tortoise ORM Model 的子类。", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    typer.echo(f"✅ 成功加载模型: {model_class_name} from {module_name_str}")

    path_parts = module_name_str.split('.')
    if len(path_parts) < 3 or path_parts[0] != module_root or path_parts[-1] != "models":
        typer.secho(
            f"错误: 模型路径 '{model_path}' 结构不符合预期。期望结构如 '{module_root}.<business_module_name>.models.{model_class_name}'。", 
            fg=typer.colors.RED, err=True
        )
        typer.echo(f"当前解析的模块根: {path_parts[0]}, 业务模块名部分: {path_parts[1:-1]}, 模型文件名部分: {path_parts[-1]}")
        raise typer.Exit(code=1)
    
    business_module_name = path_parts[1]
    model_name_base = model_class_name.replace("Orm", "").replace("Model", "") 
    
    project_root_dir = Path(os.getcwd())
    module_dir = project_root_dir / module_root / business_module_name
    
    typer.echo(f"业务模块名称: {business_module_name}")
    typer.echo(f"模型基础名称: {model_name_base}")
    typer.echo(f"目标模块目录: {module_dir}")

    module_dir.mkdir(parents=True, exist_ok=True)

    # --- 1. 生成 Schemas (schemas.py) ---
    typer.echo(f"  - 正在生成 schemas.py for {model_name_base}...")
    base_fields_str_list = []
    update_fields_str_list = []
    schema_imports_set = set() 
    
    pk_field_obj = model_cls._meta.pk
    pk_field_name = pk_field_obj.model_field_name if pk_field_obj else "id"
    pk_pydantic_type = "int"
    if pk_field_obj:
        # 修正：应该使用 pk_field_obj.field_type (字段的原始Tortoise类型) 来查找映射
        pk_raw_type = PYDANTIC_TYPE_MAP.get(type(pk_field_obj.field_type), "Any") 
        if pk_raw_type in PYTHON_TO_PYDANTIC_IMPORT_MAP:
            schema_imports_set.add(PYTHON_TO_PYDANTIC_IMPORT_MAP[pk_raw_type])
        pk_pydantic_type = pk_raw_type

    for name, field in model_cls._meta.fields_map.items():
        if field.pk: continue
        if isinstance(field, (tortoise_fields.ForeignKeyFieldInstance, tortoise_fields.OneToOneFieldInstance)):
            fk_id_name = f"{name}_id"
            try:
                related_model_cls = field.related_model 
                related_model_pk_field = related_model_cls._meta.pk
                # 修正：应该使用 related_model_pk_field.field_type
                fk_id_type = PYDANTIC_TYPE_MAP.get(type(related_model_pk_field.field_type), "int")
            except Exception: 
                fk_id_type = "int"

            if fk_id_type in PYTHON_TO_PYDANTIC_IMPORT_MAP:
                schema_imports_set.add(PYTHON_TO_PYDANTIC_IMPORT_MAP[fk_id_type])
            
            base_fields_str_list.append(f"    {fk_id_name}: {fk_id_type} # 外键关联 {field.related_model.__name__}")
            update_fields_str_list.append(f"    {fk_id_name}: Optional[{fk_id_type}] = None")
            if "Optional" in PYTHON_TO_PYDANTIC_IMPORT_MAP: # 确保Optional被导入
                 schema_imports_set.add(PYTHON_TO_PYDANTIC_IMPORT_MAP["Optional"])
            continue
        if isinstance(field, tortoise_fields.ManyToManyFieldInstance): continue

        base_def, update_def, imports_for_field = _get_pydantic_field_definition(name, field)
        if base_def: base_fields_str_list.append(base_def)
        if update_def: update_fields_str_list.append(update_def)
        schema_imports_set.update(imports_for_field)

    response_id_field_str = f"    {pk_field_name}: {pk_pydantic_type}"
    
    final_imports_str = ""
    # 确保基础的Pydantic和typing导入在最前面
    core_imports = ["from pydantic import BaseModel, Field", "from typing import Optional, List, Dict, Any"]
    for core_imp in core_imports: # 从集合中移除，以避免重复，并保证顺序
        if core_imp in schema_imports_set:
            schema_imports_set.remove(core_imp)
    
    final_imports_str += "\n".join(core_imports) + "\n"
    
    # 其他按字母顺序排序的导入
    sorted_other_imports = sorted(list(schema_imports_set))
    if sorted_other_imports:
        final_imports_str += "\n".join(sorted_other_imports) + "\n"


    schemas_content = SCHEMA_TEMPLATE.format(
        module_path=str(module_dir.relative_to(project_root_dir)),
        model_name=model_name_base,
        imports=final_imports_str.strip(),
        base_fields="\n".join(base_fields_str_list) if base_fields_str_list else "    pass",
        update_fields="\n".join(update_fields_str_list) if update_fields_str_list else "    pass",
        response_id_field=response_id_field_str,
    )
    schemas_content = os.linesep.join([s for s in schemas_content.splitlines() if s.strip() or s == ""]) # 移除多余空行

    schemas_file = module_dir / "schemas.py"
    if schemas_file.exists() and not overwrite:
        typer.secho(f"警告: '{schemas_file}' 已存在。使用 --overwrite 选项进行覆盖。", fg=typer.colors.YELLOW, err=True)
    else:
        schemas_file.write_text(schemas_content, encoding="utf-8")
        typer.secho(f"成功: 已生成 '{schemas_file}'。", fg=typer.colors.GREEN)

    # --- 后续生成 Repository, Service, __init__.py 的逻辑 (与之前相同) ---
    typer.echo(f"  - 正在生成 repositories.py for {model_name_base}...")
    repo_content = REPOSITORY_TEMPLATE.format(
        module_path=str(module_dir.relative_to(project_root_dir)),
        model_name=model_name_base,
        model_orm_name=model_class_name
    )
    repo_file = module_dir / "repositories.py"
    if repo_file.exists() and not overwrite:
        typer.secho(f"警告: '{repo_file}' 已存在。使用 --overwrite 选项进行覆盖。", fg=typer.colors.YELLOW, err=True)
    else:
        repo_file.write_text(repo_content, encoding="utf-8")
        typer.secho(f"成功: 已生成 '{repo_file}'。", fg=typer.colors.GREEN)

    typer.echo(f"  - 正在生成 services.py for {model_name_base}...")
    service_content = SERVICE_TEMPLATE.format(
        module_path=str(module_dir.relative_to(project_root_dir)),
        model_name=model_name_base,
        model_orm_name=model_class_name,
        model_name_plural=f"{model_name_base.lower()}s" # 用于模板中的示例代码
    )
    service_file = module_dir / "services.py"
    if service_file.exists() and not overwrite:
        typer.secho(f"警告: '{service_file}' 已存在。使用 --overwrite 选项进行覆盖。", fg=typer.colors.YELLOW, err=True)
    else:
        service_file.write_text(service_content, encoding="utf-8")
        typer.secho(f"成功: 已生成 '{service_file}'。", fg=typer.colors.GREEN)

    typer.echo(f"  - 正在生成/更新 __init__.py for {business_module_name} 模块...")
    routing_content = ROUTING_INIT_TEMPLATE.format(
        module_path=str(module_dir.relative_to(project_root_dir)),
        model_orm_name=model_class_name,
        model_name=model_name_base,
        module_name_plural=f"{business_module_name.lower()}", 
        model_name_tag=model_name_base.capitalize()
    )
    module_init_file = module_dir / "__init__.py"
    
    # 确保模块根目录 (例如 modules/) 和业务模块目录 (例如 modules/product/) 都有 __init__.py
    (project_root_dir / module_root).mkdir(parents=True, exist_ok=True)
    (project_root_dir / module_root / "__init__.py").touch(exist_ok=True)
    module_dir.mkdir(parents=True, exist_ok=True) # 确保业务模块目录存在

    if module_init_file.exists() and not overwrite:
        typer.secho(f"警告: '{module_init_file}' 已存在。此脚手架尚不支持智能合并，请手动集成路由或使用 --overwrite。", fg=typer.colors.YELLOW, err=True)
    else:
        module_init_file.write_text(routing_content, encoding="utf-8")
        typer.secho(f"成功: 已生成 '{module_init_file}'。", fg=typer.colors.GREEN)

    typer.secho(f"\n🎉 CRUD组件为模型 '{model_path}' 生成完毕！", fg=typer.colors.CYAN, bold=True)
    typer.echo("下一步建议:")
    typer.echo(f"  1. 仔细检查并完善 '{schemas_file}' 中的Pydantic模型定义。")
    typer.echo(f"  2. 在 '{repo_file}' 和 '{service_file}' 中根据需要添加或修改特定于业务的逻辑。")
    typer.echo(f"  3. 检查 '{module_init_file}' 中的路由前缀和标签。")
    typer.echo(f"  4. 运行数据库迁移: `aerich migrate --name add_{business_module_name}_module` 和 `aerich upgrade`。")
    typer.echo(f"  5. 启动应用并测试新的API端点。")


if __name__ == "__main__":
    app()