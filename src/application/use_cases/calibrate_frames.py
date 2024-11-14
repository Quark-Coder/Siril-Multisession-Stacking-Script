from typing import List, Optional
from pathlib import Path

from src.domain.entities.image import Image
from src.domain.entities.calibration_frames import CalibrationFrameLibrary, CalibrationFrameType
from src.application.services.image_processing_service import ImageProcessingService
from src.utils.logging import get_logger

logger = get_logger(__name__)


class CalibrateFramesUseCase:
    def __init__(self, image_processing_service: ImageProcessingService):
        self._image_processing_service = image_processing_service

    async def execute(
        self,
        frames: List[Image],
        calibration_library: Optional[CalibrationFrameLibrary] = None,
        output_dir: Optional[Path] = None
    ) -> List[Image]:
        """
        Калибровка набора кадров с использованием калибровочной библиотеки
        
        Args:
            frames: Список кадров для калибровки
            calibration_library: Библиотека калибровочных кадров
            output_dir: Директория для сохранения результатов
            
        Returns:
            Список откалиброванных кадров
        """
        try:
            if not frames:
                logger.error("Не предоставлены кадры для калибровки")
                return []

            if not calibration_library:
                logger.warning("Не предоставлена библиотека калибровочных кадров")
                return frames

            # Применяем калибровку к каждому кадру
            calibrated_frames = []
            for frame in frames:
                calibrated = await self._image_processing_service._image_processor.calibrate_image(
                    frame,
                    master_dark=calibration_library.dark_frames.master_frame,
                    master_flat=calibration_library.flat_frames.master_frame,
                    master_bias=calibration_library.bias_frames.master_frame,
                    output_path=output_dir / f"calibrated_{frame.file_path.name}" if output_dir else None
                )
                
                if calibrated:
                    calibrated_frames.append(calibrated)
                else:
                    logger.warning(f"Ошибка при калибровке кадра {frame.file_path}")
                    
            return calibrated_frames

        except Exception as e:
            logger.error(f"Ошибка при калибровке кадров: {str(e)}")
            return []
