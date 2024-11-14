from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path

from src.domain.entities.image import Image


class ImageProcessor(ABC):
    """
    Интерфейс для обработки астрономических изображений
    """
    
    @abstractmethod
    def stack_images(self, 
                    images: List[Image], 
                    output_path: Path,
                    method: str = 'average',
                    sigma_low: float = 3.0,
                    sigma_high: float = 3.0,
                    normalize: bool = True) -> Optional[Image]:
        """
        Стекирует набор изображений
        
        Args:
            images: Список изображений для стекинга
            output_path: Путь для сохранения результата
            method: Метод стекинга ('average', 'median', 'sigma_clip')
            sigma_low: Нижний порог сигма для отбраковки
            sigma_high: Верхний порог сигма для отбраковки
            normalize: Нормализовать ли изображения перед стекингом
            
        Returns:
            Стекированное изображение или None в случае ошибки
        """
        pass

    @abstractmethod
    def calibrate_image(self,
                       image: Image,
                       master_dark: Optional[Image] = None,
                       master_flat: Optional[Image] = None,
                       master_bias: Optional[Image] = None,
                       output_path: Optional[Path] = None) -> Optional[Image]:
        """
        Калибрует изображение используя мастер-кадры
        
        Args:
            image: Изображение для калибровки
            master_dark: Мастер dark кадр
            master_flat: Мастер flat кадр
            master_bias: Мастер bias кадр
            output_path: Путь для сохранения результата
            
        Returns:
            Откалиброванное изображение или None в случае ошибки
        """
        pass
        
    @abstractmethod
    def register_images(self,
                       images: List[Image],
                       reference_image: Optional[Image] = None,
                       output_dir: Optional[Path] = None) -> List[Image]:
        """
        Выполняет регистрацию (совмещение) набора изображений
        
        Args:
            images: Список изображений для регистрации
            reference_image: Опорное изображение (если None, будет выбрано автоматически)
            output_dir: Директория для сохранения результатов
            
        Returns:
            Список зарегистрированных изображений
        """
        pass
        
    @abstractmethod
    def debayer_image(self,
                     image: Image,
                     output_path: Optional[Path] = None) -> Optional[Image]:
        """
        Выполняет дебайеризацию RAW изображения
        
        Args:
            image: RAW изображение для дебайеризации
            output_path: Путь для сохранения результата
            
        Returns:
            Дебайеризованное изображение или None в случае ошибки
        """
        pass
        
    @abstractmethod
    def normalize_image(self,
                       image: Image,
                       output_path: Optional[Path] = None) -> Optional[Image]:
        """
        Нормализует изображение
        
        Args:
            image: Изображение для нормализации
            output_path: Путь для сохранения результата
            
        Returns:
            Нормализованное изображение или None в случае ошибки
        """
        pass
