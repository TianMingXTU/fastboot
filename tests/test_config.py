from fastboot.config import ConfigManager

config = ConfigManager()

print(config.get("database.host"))  # 输出 localhost
print(config.get("server.port"))    # 输出 8000
print(config.get("not.exist", default="N/A"))  # 输出 N/A
