from typing import List, Optional
from infrastructure.repositories.system_setting_repository import SystemSettingRepository

class SystemSettingService:
    def __init__(self, repository: SystemSettingRepository):
        self.repository = repository

    def get_all_settings(self) -> List:
        return self.repository.get_all()

    def update_setting(self, key: str, value: str, description: str = None):
        return self.repository.set_value(key, value, description)