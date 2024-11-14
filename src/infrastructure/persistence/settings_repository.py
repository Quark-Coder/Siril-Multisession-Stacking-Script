import json

from pathlib import Path
from typing import Dict, Optional

from config.settings import SETTINGS_DIR, SETTINGS_FILE


class SettingsRepository:
    """
    Репозиторий для управления настройками приложения
    """
    
    def __init__(self):
        self._settings_dir = Path(SETTINGS_DIR)
        self._settings_file = Path(SETTINGS_FILE)
        self._ensure_settings_dir_exists()
        
    def _ensure_settings_dir_exists(self) -> None:
        """
        Создает директорию настроек, если она не существует
        """
        if not self._settings_dir.exists():
            self._settings_dir.mkdir(parents=True)
            
    def save_settings(self, settings: Dict) -> None:
        """
        Сохраняет настройки в файл
        
        Args:
            settings: Словарь с настройками для сохранения
        """
        try:
            with open(self._settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            raise IOError(f"Ошибка при сохранении настроек: {str(e)}")
            
    def load_settings(self) -> Optional[Dict]:
        """
        Загружает настройки из файла
        
        Returns:
            Dict: Словарь с настройками или None, если файл не существует
        """
        if not self._settings_file.exists():
            return None
            
        try:
            with open(self._settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise IOError(f"Ошибка при загрузке настроек: {str(e)}")
            
    def update_setting(self, key: str, value: any) -> None:
        """
        Обновляет конкретную настройку
        
        Args:
            key: Ключ настройки
            value: Новое значение
        """
        settings = self.load_settings() or {}
        settings[key] = value
        self.save_settings(settings)
        
    def get_setting(self, key: str, default: any = None) -> any:
        """
        Получает значение конкретной настройки
        
        Args:
            key: Ключ настройки
            default: Значение по умолчанию
            
        Returns:
            Значение настройки или default, если настройка не найдена
        """
        settings = self.load_settings() or {}
        return settings.get(key, default)
        
    def delete_setting(self, key: str) -> None:
        """
        Удаляет настройку
        
        Args:
            key: Ключ настройки для удаления
        """
        settings = self.load_settings() or {}
        if key in settings:
            del settings[key]
            self.save_settings(settings)
            
    def clear_settings(self) -> None:
        """
        Удаляет все настройки
        """
        if self._settings_file.exists():
            self._settings_file.unlink()
