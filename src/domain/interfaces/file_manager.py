from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Dict

from src.domain.entities.calibration_frames import CalibrationFrameType
from src.domain.entities.image import Image


class FileManager(ABC):
    """
    Абстрактный интерфейс для управления файлами астрономических изображений
    """
    
    @abstractmethod
    def create_session_directory(self, session_name: str) -> Path:
        """
        Создает директорию для новой сессии
        
        Args:
            session_name: Имя сессии
            
        Returns:
            Path: Путь к созданной директории
        """
        pass
        
    @abstractmethod
    def create_calibration_directory(self, 
                                   session_dir: Path,
                                   frame_type: CalibrationFrameType) -> Path:
        """
        Создает директорию для калибровочных кадров
        
        Args:
            session_dir: Путь к директории сессии
            frame_type: Тип калибровочных кадров
            
        Returns:
            Path: Путь к созданной директории
        """
        pass
        
    @abstractmethod
    def get_calibration_frames(self, 
                             directory: Path,
                             frame_type: CalibrationFrameType) -> List[Image]:
        """
        Получает список калибровочных кадров из директории
        
        Args:
            directory: Путь к директории с кадрами
            frame_type: Тип калибровочных кадров
            
        Returns:
            List[Image]: Список найденных изображений
        """
        pass
        
    @abstractmethod
    def get_light_frames(self, directory: Path) -> List[Image]:
        """
        Получает список световых кадров из директории
        
        Args:
            directory: Путь к директории со световыми кадрами
            
        Returns:
            List[Image]: Список найденных изображений
        """
        pass
        
    @abstractmethod
    def save_master_frame(self,
                         image: Image,
                         frame_type: CalibrationFrameType,
                         output_dir: Path) -> Path:
        """
        Сохраняет мастер-кадр
        
        Args:
            image: Изображение для сохранения
            frame_type: Тип калибровочного кадра
            output_dir: Директория для сохранения
            
        Returns:
            Path: Путь к сохраненному файлу
        """
        pass
        
    @abstractmethod
    def save_calibrated_light(self,
                            image: Image,
                            output_dir: Path,
                            index: Optional[int] = None) -> Path:
        """
        Сохраняет калиброванный световой кадр
        
        Args:
            image: Изображение для сохранения
            output_dir: Директория для сохранения
            index: Опциональный индекс для именования файла
            
        Returns:
            Path: Путь к сохраненному файлу
        """
        pass
        
    @abstractmethod
    def cleanup_temporary_files(self, directory: Path) -> None:
        """
        Очищает временные файлы из директории
        
        Args:
            directory: Директория для очистки
        """
        pass
        
    @abstractmethod
    def get_session_info(self, session_dir: Path) -> Dict:
        """
        Получает информацию о сессии
        
        Args:
            session_dir: Путь к директории сессии
            
        Returns:
            Dict: Словарь с информацией о сессии
        """
        pass
