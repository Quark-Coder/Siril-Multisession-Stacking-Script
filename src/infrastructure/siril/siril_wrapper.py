import logging

from pathlib import Path
from typing import List, Optional

from pysiril.siril import Siril
from pysiril.wrapper import Wrapper

from src.domain.interfaces.image_processor import ImageProcessor
from src.domain.entities.image import Image
from config.settings import (
    DEFAULT_SIRIL_PATH,
    STACK_SETTINGS,
    CALIBRATION_SETTINGS,
    IMAGE_EXTENSION
)

logger = logging.getLogger(__name__)

class SirilWrapper(ImageProcessor):
    """
    Реализация ImageProcessor с использованием Siril
    """
    
    def __init__(self, siril_path: str = DEFAULT_SIRIL_PATH):
        """
        Инициализация обертки Siril
        
        Args:
            siril_path: Путь к исполняемому файлу Siril
        """
        try:
            self.app = Siril(siril_exe=siril_path)
            self.cmd = Wrapper(self.app)
            self.app.Open()
            self._configure_siril()
            logger.info("Siril успешно инициализирован")
        except Exception as e:
            logger.error(f"Ошибка при инициализации Siril: {e}")
            raise
            
    def _configure_siril(self):
        """Настройка базовых параметров Siril"""
        self.cmd.setext(IMAGE_EXTENSION)
        
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
        if not images:
            logger.error("Пустой список изображений для стекинга")
            return None
            
        try:
            # Переходим в директорию с изображениями
            work_dir = images[0].directory
            self.cmd.cd(str(work_dir))
            
            # Подготавливаем параметры стекинга
            stack_params = {
                'type': method,
                'sigma_low': sigma_low,
                'sigma_high': sigma_high,
                'norm': 'addscale' if normalize else 'no',
                'output_norm': STACK_SETTINGS['output_norm'],
                'rgb_equal': STACK_SETTINGS['rgb_equal']
            }
            
            # Выполняем стекинг
            prefix = images[0].name.split('_')[0]
            self.cmd.stack(prefix, **stack_params)
            
            # Создаем объект Image для результата
            result_path = output_path / f"{prefix}_stacked.{IMAGE_EXTENSION}"
            if result_path.exists():
                return Image(file_path=result_path)
                
            logger.error("Результат стекинга не найден")
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при стекинге изображений: {e}")
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
            self.cmd.cd(str(image.directory))
            
            calibration_params = {
                'cfa': CALIBRATION_SETTINGS['cfa'],
                'equalize_cfa': CALIBRATION_SETTINGS['equalize_cfa'],
                'debayer': CALIBRATION_SETTINGS['debayer']
            }
            
            # Добавляем мастер-кадры если они есть
            if master_dark:
                calibration_params['dark'] = master_dark.name
            if master_flat:
                calibration_params['flat'] = master_flat.name
            if master_bias:
                calibration_params['bias'] = master_bias.name
                
            # Выполняем калибровку
            prefix = image.name.split('.')[0]
            self.cmd.calibrate(prefix, **calibration_params)
            
            # Возвращаем откалиброванное изображение
            if output_path:
                result_path = output_path
            else:
                result_path = image.directory / f"pp_{image.name}"
                
            if result_path.exists():
                return Image(file_path=result_path)
                
            logger.error("Результат калибровки не найден")
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при калибровке изображения: {e}")
            return None
            
    def register_images(self,
                       images: List[Image],
                       reference_image: Optional[Image] = None,
                       output_dir: Optional[Path] = None) -> List[Image]:
        """
        Выполняет регистрацию набора изображений
        """
        if not images:
            logger.error("Пустой список изображений для регистрации")
            return []
            
        try:
            work_dir = images[0].directory
            self.cmd.cd(str(work_dir))
            
            # Выполняем регистрацию
            prefix = images[0].name.split('_')[0]
            self.cmd.register(prefix)
            
            # Собираем зарегистрированные изображения
            registered_images = []
            for image in images:
                reg_path = image.directory / f"r_{image.name}"
                if reg_path.exists():
                    registered_images.append(Image(file_path=reg_path))
                    
            return registered_images
            
        except Exception as e:
            logger.error(f"Ошибка при регистрации изображений: {e}")
            return []
            
    def debayer_image(self,
                     image: Image,
                     output_path: Optional[Path] = None) -> Optional[Image]:
        """
        Выполняет дебайеризацию RAW изображения
        """
        try:
            self.cmd.cd(str(image.directory))
            
            # Выполняем дебайеризацию
            prefix = image.name.split('.')[0]
            self.cmd.debayer(prefix)
            
            # Возвращаем дебайеризованное изображение
            if output_path:
                result_path = output_path
            else:
                result_path = image.directory / f"debayer_{image.name}"
                
            if result_path.exists():
                return Image(file_path=result_path)
                
            logger.error("Результат дебайеризации не найден")
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при дебайеризации изображения: {e}")
            return None
            
    def normalize_image(self,
                       image: Image,
                       output_path: Optional[Path] = None) -> Optional[Image]:
        """
        Нормализует изображение
        """
        try:
            self.cmd.cd(str(image.directory))
            
            # Выполняем нормализацию
            prefix = image.name.split('.')[0]
            self.cmd.normalize(prefix)
            
            # Возвращаем нормализованное изображение
            if output_path:
                result_path = output_path
            else:
                result_path = image.directory / f"norm_{image.name}"
                
            if result_path.exists():
                return Image(file_path=result_path)
                
            logger.error("Результат нормализации не найден")
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при нормализации изображения: {e}")
            return None
