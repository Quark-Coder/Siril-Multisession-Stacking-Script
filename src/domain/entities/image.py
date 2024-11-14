from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any


@dataclass
class Image:
    """
    Класс, представляющий астрономическое изображение
    """
    file_path: Path
    exposure_time: Optional[float] = None
    temperature: Optional[float] = None
    gain: Optional[int] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """
        Проверяет существование файла и инициализирует метаданные
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"Файл изображения не найден: {self.file_path}")
        
        if self.metadata is None:
            self.metadata = {}
            
    @property
    def name(self) -> str:
        """
        Возвращает имя файла изображения
        """
        return self.file_path.name
        
    @property
    def directory(self) -> Path:
        """
        Возвращает директорию, содержащую изображение
        """
        return self.file_path.parent
        
    def is_calibrated(self) -> bool:
        """
        Проверяет, было ли изображение калибровано
        """
        return self.name.startswith('pp_') or self.name.startswith('r_')
        
    def is_master_frame(self) -> bool:
        """
        Проверяет, является ли изображение мастер-кадром
        """
        return 'stacked' in self.name
        
    def get_frame_type(self) -> Optional[str]:
        """
        Определяет тип кадра (light, dark, flat, bias)
        """
        name = self.name.lower()
        if 'light' in name:
            return 'light'
        elif 'dark' in name:
            return 'dark'
        elif 'flat' in name:
            return 'flat'
        elif 'bias' in name:
            return 'bias'
        return None
        
    def __str__(self) -> str:
        """
        Строковое представление изображения
        """
        return f"Image({self.name})"
