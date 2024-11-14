from typing import Optional

from src.domain.entities.session import Session
from src.domain.entities.image import Image 
from src.domain.entities.calibration_frames import CalibrationFrameLibrary
from src.application.services.image_processing_service import ImageProcessingService
from src.utils.logging import get_logger

logger = get_logger(__name__)


class ProcessSessionUseCase:
    def __init__(self, image_processing_service: ImageProcessingService):
        self._image_processing_service = image_processing_service

    async def execute(
        self,
        session: Session,
        calibration_library: Optional[CalibrationFrameLibrary] = None,
    ) -> Optional[Image]:
        """
        Обработка сессии астрофотографии
        
        Args:
            session: Сессия для обработки
            calibration_library: Библиотека калибровочных кадров            
        Returns:
            Обработанное финальное изображение или None в случае ошибки
        """
        try:
            if not session.light_frames_dir:
                logger.error("В сессии не указана директория со световыми кадрами")
                return None

            # Обрабатываем световые кадры
            processed_frames = await self._image_processing_service.process_light_frames(
                session,
                calibration_library
            )
            
            if not processed_frames:
                logger.error("Не удалось обработать световые кадры")
                return None
                
            return processed_frames[0] if processed_frames else None

        except Exception as e:
            logger.error(f"Ошибка при обработке сессии: {str(e)}")
            return None
