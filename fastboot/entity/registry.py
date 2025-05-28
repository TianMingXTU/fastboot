# fastboot/entity/registry.py
import pkgutil
import importlib
from typing import Dict, Type, List, Optional
from tortoise import models, fields as tortoise_fields
from pydantic import BaseModel, create_model
from fastboot.logger import Logger
from fastboot.entity.fields import FieldDefinition

# Tortoise字段类型到Python类型的映射，用于生成Pydantic模型
DB_TO_PYTHON_TYPE_MAP = {
    tortoise_fields.IntField: int,
    tortoise_fields.BigIntField: int,
    tortoise_fields.SmallIntField: int,
    tortoise_fields.CharField: str,
    tortoise_fields.TextField: str,
    tortoise_fields.BooleanField: bool,
    tortoise_fields.DecimalField: float,
    tortoise_fields.DatetimeField: importlib.import_module("datetime").datetime,
    tortoise_fields.DateField: importlib.import_module("datetime").date,
    tortoise_fields.FloatField: float,
    tortoise_fields.JSONField: dict,
}

class EntityRegistry:
    def __init__(self, logger: Logger):
        self.logger = logger
        self._entities: Dict[str, Type] = {}
        self._orm_models: Dict[str, Type[models.Model]] = {}
        self._pydantic_schemas: Dict[str, Dict[str, Type[BaseModel]]] = {}
        self._handlers: Dict[str, Type] = {}

    def discover_entities(self, base_package_name: str):
        if not base_package_name:
            self.logger.warning("实体扫描：未提供基础包名，跳过。")
            return
        self.logger.info(f"实体扫描：开始扫描基础包 '{base_package_name}'...")
        try:
            package = importlib.import_module(base_package_name)
        except ImportError:
            self.logger.error(f"实体扫描：无法导入基础包 '{base_package_name}'。")
            return
        for module_info in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
            module_name_parts = module_info.name.split('.')
            # 扫描 'entity', 'entities' 和 'handler', 'handlers' 文件，确保所有相关模块被加载
            if module_name_parts[-1] in ('entity', 'entities', 'handler', 'handlers'):
                try:
                    importlib.import_module(module_info.name)
                    self.logger.debug(f"扫描：成功导入模块 '{module_info.name}'。")
                except Exception as e:
                    self.logger.error(f"扫描：导入模块 '{module_info.name}' 时出错: {e}", exc_info=True)
        
        self.logger.info(f"模块扫描完成。共发现 {len(self._entities)} 个实体和 {len(self._handlers)} 个处理器。")
        self._generate_models()
        self._generate_pydantic_schemas()

    def register(self, cls: Type):
        name = cls.__name__
        if name in self._entities:
            self.logger.warning(f"实体注册：实体 '{name}' 已存在，将被覆盖。")
        self._entities[name] = cls
        self.logger.debug(f"实体注册：实体 '{name}' 已成功注册。")

    def register_handler(self, entity_cls: Type, handler_cls: Type):
        entity_name = entity_cls.__name__
        if entity_name in self._handlers:
            self.logger.warning(f"处理器注册：实体 '{entity_name}' 的处理器将被 '{handler_cls.__name__}' 覆盖。")
        self._handlers[entity_name] = handler_cls
        self.logger.debug(f"处理器注册：实体 '{entity_name}' 已绑定到处理器 '{handler_cls.__name__}'。")

    def _generate_models(self):
        self.logger.info("模型生成：开始根据实体定义生成ORM模型...")
        for name, entity_cls in self._entities.items():
            orm_model_name = f"{name}Orm"
            table_name = getattr(entity_cls, '_meta_table_name', name.lower() + 's')
            orm_attrs = {'__module__': entity_cls.__module__, 'Meta': type('Meta', (), {'table': table_name})}
            field_definitions = {k: v for k, v in entity_cls.__dict__.items() if isinstance(v, FieldDefinition)}
            for field_name, field_def in field_definitions.items():
                kwargs = {'pk': field_def.pk, 'null': field_def.nullable, 'index': field_def.db_index, 'unique': field_def.unique}
                if field_def.max_length is not None: kwargs['max_length'] = field_def.max_length
                kwargs.update(field_def.extra_db_args)
                orm_attrs[field_name] = field_def.db_type(**kwargs)
            self._orm_models[name] = type(orm_model_name, (models.Model,), orm_attrs)
        self.logger.info(f"模型生成：共生成了 {len(self._orm_models)} 个ORM模型。")

    def _generate_pydantic_schemas(self):
        self.logger.info("DTO生成：开始根据实体定义生成Pydantic Schemas...")
        for name, entity_cls in self._entities.items():
            self._pydantic_schemas[name] = {}
            field_definitions = {k: v for k, v in entity_cls.__dict__.items() if isinstance(v, FieldDefinition)}
            response_fields = {f_name: (DB_TO_PYTHON_TYPE_MAP.get(f_def.db_type, str), ...) for f_name, f_def in field_definitions.items() if f_def.api_expose}
            self._pydantic_schemas[name]['response'] = create_model(f'{name}ResponseSchema', __config__={'from_attributes': True}, **response_fields)
            create_fields = {f_name: (DB_TO_PYTHON_TYPE_MAP.get(f_def.db_type, str), None if f_def.nullable else ...) for f_name, f_def in field_definitions.items() if f_def.api_mutable and not f_def.pk}
            self._pydantic_schemas[name]['create'] = create_model(f'{name}CreateSchema', **create_fields)
            update_fields = {f_name: (Optional[DB_TO_PYTHON_TYPE_MAP.get(f_def.db_type, str)], None) for f_name, f_def in field_definitions.items() if f_def.api_mutable and not f_def.pk}
            self._pydantic_schemas[name]['update'] = create_model(f'{name}UpdateSchema', **update_fields)
        self.logger.info(f"DTO生成：Pydantic Schemas生成完毕。")

    def get_entity(self, name: str) -> Optional[Type]:
        return self._entities.get(name)
        
    def get_orm_model(self, name: str) -> Optional[Type[models.Model]]:
        return self._orm_models.get(name)

    def get_pydantic_schema(self, entity_name: str, schema_type: str) -> Optional[Type[BaseModel]]:
        return self._pydantic_schemas.get(entity_name, {}).get(schema_type)
        
    def get_all_entities(self) -> List[Type]:
        return list(self._entities.values())
        
    def get_handler_for_entity(self, entity_cls: Type) -> Optional[Type]:
        return self._handlers.get(entity_cls.__name__)

    def get_all_orm_models(self) -> List[Type[models.Model]]:
        aerich_models_module = importlib.import_module("aerich.models")
        return list(self._orm_models.values()) + [getattr(aerich_models_module, 'Aerich')]

# 创建一个全局单例
default_registry = EntityRegistry(Logger(name="EntityRegistry"))