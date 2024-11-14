from pathlib import Path
from typing import List, Optional, Dict

from src.domain.interfaces.image_processor import ImageProcessor
from src.domain.interfaces.file_manager import FileManager
from src.domain.entities.image import Image
from src.domain.entities.calibration_frames import (
    CalibrationFrame, 
    CalibrationFrameType,
    CalibrationFrameLibrary
)
from src.utils.logging import get_logger, log_execution_time

logger = get_logger(__name__)


class CalibrationService:
    """
    Сервис для калибровки астрономических изображений
    """
    
    def __init__(self, 
                 image_processor: ImageProcessor,
                 file_manager: FileManager):
        self.image_processor = image_processor
        self.file_manager = file_manager
        self.calibration_library = CalibrationFrameLibrary()
        
    @log_execution_time()
    def create_master_frames(self, 
                           session_dir: Path,
                           output_dir: Path) -> Dict[CalibrationFrameType, Optional[Path]]:
        """
        Создает мастер-кадры из калибровочных кадров сессии
        
        Args:
            session_dir: Директория сессии
            output_dir: Директория для сохранения мастер-кадров
            
        Returns:
            Dict[CalibrationFrameType, Optional[Path]]: Словарь с путями к мастер-кадрам
        """
        master_frames = {}
        
        try:
            # Обрабатываем каждый тип калибровочных кадров
            for frame_type in CalibrationFrameType:
                frame_set = self.calibration_library.get_frame_set(frame_type)
                
                if not frame_set.frames:
                    # Получаем кадры из директории
                    frames = self.file_manager.get_calibration_frames(session_dir, frame_type)
                    for frame in frames:
                        cal_frame = CalibrationFrame(
                            type=frame_type,
                            file_path=frame.file_path,
                            exposure_time=frame.exposure_time,
                            temperature=frame.temperature,
                            gain=frame.gain
                        )
                        frame_set.add_frame(cal_frame)
                
                if frame_set.frames:
                    # Создаем мастер-кадр
                    images = [Image(file_path=f.file_path) for f in frame_set.frames]
                    master = self.image_processor.stack_images(
                        images=images,
                        output_path=output_dir / f"master_{frame_type.value}.fit",
                        method='sigma_clip'
                    )
                    
                    if master:
                        frame_set.master_frame = master.file_path
                        master_frames[frame_type] = master.file_path
                        logger.info(f"Создан мастер-кадр {frame_type.value}")
                    else:
                        logger.warning(f"Не удалось создать мастер-кадр {frame_type.value}")
                        
            return master_frames
            
        except Exception as e:
            logger.error(f"Ошибка при создании мастер-кадров: {str(e)}")
            raise

    @log_execution_time()
    def calibrate_light_frames(self,
                             light_frames: List[Image],
                             output_dir: Path) -> List[Image]:
        """
        Калибрует световые кадры используя доступные мастер-кадры
        
        Args:
            light_frames: Список световых кадров
            output_dir: Директория для сохранения результатов
            
        Returns:
            List[Image]: Список калиброванных кадров
        """
        calibrated_frames = []
        
        try:
            for i, light in enumerate(light_frames):
                # Получаем подходящие мастер-кадры
                master_dark = None
                master_flat = None
                master_bias = None
                
                if self.calibration_library.has_master_frame(CalibrationFrameType.DARK):
                    dark_set = self.calibration_library.get_frame_set(CalibrationFrameType.DARK)
                    matching_darks = dark_set.get_matching_frames(
                        exposure_time=light.exposure_time,
                        temperature=light.temperature
                    )
                    if matching_darks:
                        master_dark = Image(file_path=dark_set.master_frame)
                
                if self.calibration_library.has_master_frame(CalibrationFrameType.FLAT):
                    flat_set = self.calibration_library.get_frame_set(CalibrationFrameType.FLAT)
                    master_flat = Image(file_path=flat_set.master_frame)
                    
                if self.calibration_library.has_master_frame(CalibrationFrameType.BIAS):
                    bias_set = self.calibration_library.get_frame_set(CalibrationFrameType.BIAS)
                    master_bias = Image(file_path=bias_set.master_frame)
                
                # Калибруем кадр
                output_path = output_dir / f"calibrated_light_{i:04d}.fit"
                calibrated = self.image_processor.calibrate_image(
                    image=light,
                    master_dark=master_dark,
                    master_flat=master_flat,
                    master_bias=master_bias,
                    output_path=output_path
                )
                
                if calibrated:
                    calibrated_frames.append(calibrated)
                    logger.info(f"Калиброван кадр {light.name}")
                else:
                    logger.warning(f"Не удалось калибровать кадр {light.name}")
                    
            return calibrated_frames
            
        except Exception as e:
            logger.error(f"Ошибка при калибровке световых кадров: {str(e)}")
            raise
            
    def clear_calibration_library(self) -> None:
        """
        Очищает библиотеку калибровочных кадров
        """
        for frame_type in CalibrationFrameType:
            frame_set = self.calibration_library.get_frame_set(frame_type)
            frame_set.clear()
