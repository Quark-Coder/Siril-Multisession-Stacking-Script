from pathlib import Path
from typing import List, Optional

from src.domain.interfaces.image_processor import ImageProcessor
from src.domain.entities.image import Image
from src.infrastructure.siril.siril_wrapper import SirilWrapper
from src.utils.validators import validate_stacking_parameters
from src.utils.logging import get_logger

logger = get_logger(__name__)


class SirilImageProcessor(ImageProcessor):
    """
    Реализация обработчика изображений с использованием Siril
    """
    
    def __init__(self, siril_wrapper: SirilWrapper):
        self._siril = siril_wrapper

    def stack_images(self,
                    images: List[Image],
                    output_path: Path,
                    method: str = 'average',
                    sigma_low: float = 3.0,
                    sigma_high: float = 3.0,
                    normalize: bool = True) -> Optional[Image]:
        """
        Стекирует набор изображений используя Siril
        """
        try:
            # Валидация параметров
            if not validate_stacking_parameters(method, sigma_low, sigma_high):
                logger.error("Некорректные параметры стекинга")
                return None
                
            if not images:
                logger.error("Пустой список изображений для стекинга")
                return None

            # Выполняем стекинг через Siril
            stacked = self._siril.stack_images(
                images=images,
                output_path=output_path,
                method=method,
                sigma_low=sigma_low,
                sigma_high=sigma_high,
                normalize=normalize
            )
            
            return stacked
            
        except Exception as e:
            logger.error(f"Ошибка при стекинге изображений: {str(e)}")
            return None

    def calibrate_image(self,
                       image: Image,
                       master_dark: Optional[Image] = None,
                       master_flat: Optional[Image] = None,
                       master_bias: Optional[Image] = None,
                       output_path: Optional[Path] = None) -> Optional[Image]:
        """
        Калибрует изображение используя мастер-кадры
        """
        try:
            # Выполняем калибровку через Siril
            calibrated = self._siril.calibrate_image(
                image=image,
                master_dark=master_dark,
                master_flat=master_flat,
                master_bias=master_bias,
                output_path=output_path
            )
            
            return calibrated
            
        except Exception as e:
            logger.error(f"Ошибка при калибровке изображения: {str(e)}")
            return None

    def register_images(self,
                       images: List[Image],
                       reference_image: Optional[Image] = None,
                       output_dir: Optional[Path] = None) -> List[Image]:
        """
        Выполняет регистрацию набора изображений
        """
        try:
            # Выполняем регистрацию через Siril
            registered = self._siril.register_images(
                images=images,
                reference_image=reference_image,
                output_dir=output_dir
            )
            
            return registered
            
        except Exception as e:
            logger.error(f"Ошибка при регистрации изображений: {str(e)}")
            return []

    def debayer_image(self,
                     image: Image,
                     output_path: Optional[Path] = None) -> Optional[Image]:
        """
        Выполняет дебайеризацию RAW изображения
        """
        try:
            # Выполняем дебайеризацию через Siril
            debayered = self._siril.debayer_image(
                image=image,
                output_path=output_path
            )
            
            return debayered
            
        except Exception as e:
            logger.error(f"Ошибка при дебайеризации изображения: {str(e)}")
            return None

    def normalize_image(self,
                       image: Image,
                       output_path: Optional[Path] = None) -> Optional[Image]:
        """
        Нормализует изображение
        """
        try:
            # Выполняем нормализацию через Siril
            normalized = self._siril.normalize_image(
                image=image,
                output_path=output_path
            )
            
            return normalized
            
        except Exception as e:
            logger.error(f"Ошибка при нормализации изображения: {str(e)}")
            return None
