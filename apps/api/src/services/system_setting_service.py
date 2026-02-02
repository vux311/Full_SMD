from typing import List, Optional
from infrastructure.repositories.system_setting_repository import SystemSettingRepository

class SystemSettingService:
    def __init__(self, repository: SystemSettingRepository):
        self.repository = repository

    def get_all_settings(self) -> List:
        return self.repository.get_all()

    def get_setting(self, key: str, default=None):
        setting = self.repository.get_by_key(key)
        if not setting:
            return default
        
        val = setting.value
        dt = setting.data_type.upper() if setting.data_type else "STRING"
        
        if dt == "NUMBER":
            try: return int(val)
            except: 
                try: return float(val)
                except: return val
        elif dt == "BOOLEAN":
            return val.lower() in ("true", "1", "yes", "on")
        elif dt == "JSON":
            import json
            try: return json.loads(val)
            except: return val
        return val

    def update_setting(self, key: str, value: str, description: str = None, data_type: str = None):
        return self.repository.set_value(key, value, description, data_type)