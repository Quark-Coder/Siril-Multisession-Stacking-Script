from pathlib import Path
from typing import List, Optional, Union

from src.domain.entities.image import Image
from src.domain.entities.calibration_frames import CalibrationFrameType
from config.settings import SUPPORTED_EXTENSIONS


def validate_path(path: Union[str, Path]) -> bool:
    """
    Проверяет валидность пути
    
    Args:
        path: Путь для проверки
        
    Returns:
        bool: True если путь валиден, иначе False
    """
    path_str = str(path)
    return (
        path_str 
        and not any(char in path_str for char in ['<', '>', ':', '"', '|', '?', '*'])
        and ' ' not in path_str
    )


def validate_image_file(file_path: Path) -> bool:
    """
    Проверяет, является ли файл поддерживаемым изображением
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        bool: True если файл является поддерживаемым изображением
    """
    return (
        file_path.exists() 
        and file_path.is_file()
        and file_path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def validate_calibration_frames(
    frames: List[Image],
    frame_type: CalibrationFrameType,
    exposure_time: Optional[float] = None,
    temperature: Optional[float] = None
) -> bool:
    """
    Проверяет набор калибровочных кадров на соответствие параметрам
    
    Args:
        frames: Список калибровочных кадров
        frame_type: Тип калибровочных кадров
        exposure_time: Время экспозиции для проверки
        temperature: Температура для проверки
        
    Returns:
        bool: True если кадры валидны
    """
    if not frames:
        return False
        
    # Проверяем наличие файлов
    if not all(validate_image_file(frame.file_path) for frame in frames):
        return False
        
    # Для dark кадров проверяем соответствие времени экспозиции и температуры
    if frame_type == CalibrationFrameType.DARK and exposure_time is not None:
        if not all(frame.exposure_time == exposure_time for frame in frames):
            return False
            
        if temperature is not None:
            if not all(frame.temperature == temperature for frame in frames):
                return False
                
    return True


def validate_stacking_parameters(
    method: str,
    sigma_low: float,
    sigma_high: float
) -> bool:
    """
    Проверяет параметры стекинга
    
    Args:
        method: Метод стекинга
        sigma_low: Нижний порог сигма
        sigma_high: Верхний порог сигма
        
    Returns:
        bool: True если параметры валидны
    """
    valid_methods = {'average', 'median', 'sigma_clip'}
    
    return (
        method in valid_methods
        and isinstance(sigma_low, (int, float))
        and isinstance(sigma_high, (int, float))
        and sigma_low > 0
        and sigma_high > 0
    )


def validate_session_directory(directory: Path) -> bool:
    """
    Проверяет структуру директории сессии
    
    Args:
        directory: Путь к директории сессии
        
    Returns:
        bool: True если структура валидна
    """
    if not directory.exists() or not directory.is_dir():
        return False
        
    required_dirs = {'lights', 'process'}
    optional_dirs = {'darks', 'flats', 'biases'}
    
    existing_dirs = {d.name for d in directory.iterdir() if d.is_dir()}
    
    # Проверяем наличие обязательных директорий
    if not all(d in existing_dirs for d in required_dirs):
        return False
        
    # Проверяем что все директории входят в список разрешенных
    if not existing_dirs.issubset(required_dirs | optional_dirs):
        return False
        
    return True
