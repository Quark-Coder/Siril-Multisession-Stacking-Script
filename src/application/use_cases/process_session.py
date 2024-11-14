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
            if not session.validate():
                logger.error("Сессия не прошла валидацию")
                return None

            # Обрабатываем световые кадры
            processed_frames = await self._image_processing_service.process_light_frames(
                session,
                calibration_library or (session.calibration_library if session.has_calibration_frames() else None)
            )
            
            if not processed_frames:
                logger.error("Не удалось обработать световые кадры")
                return None
                
            # Очищаем временные файлы после обработки
            session.cleanup()
                
            return processed_frames[0] if processed_frames else None

        except Exception as e:
            logger.error(f"Ошибка при обработке сессии: {str(e)}")
            return None
