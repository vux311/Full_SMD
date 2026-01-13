from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.system_setting_model import SystemSetting

class SystemSettingRepository:
    def __init__(self, session: Session = session):
        self.session = session

    def get_all(self) -> List[SystemSetting]:
        return self.session.query(SystemSetting).all()

    def get_by_key(self, key: str) -> Optional[SystemSetting]:
        return self.session.query(SystemSetting).filter_by(key=key).first()

    def set_value(self, key: str, value: str, description: str = None, type: str = 'STRING') -> SystemSetting:
        setting = self.get_by_key(key)
        if setting:
            setting.value = value
            if description: setting.description = description
        else:
            setting = SystemSetting(key=key, value=value, type=type, description=description)
            self.session.add(setting)
        self.session.commit()
        self.session.refresh(setting)
        return setting