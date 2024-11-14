from typing import List, Optional
from pathlib import Path

from src.domain.entities.image import Image
from src.application.services.image_processing_service import ImageProcessingService
from src.utils.logging import get_logger

logger = get_logger(__name__)


class StackImagesUseCase:
    def __init__(self, image_processing_service: ImageProcessingService):
        self._image_processing_service = image_processing_service

    async def execute(
        self,
        frames: List[Image],
        output_dir: Optional[Path] = None
    ) -> Optional[Image]:
        """
        Стекинг набора кадров
        
        Args:
            frames: Список кадров для стекинга
            output_dir: Директория для сохранения результата
            
        Returns:
            Стекнутое изображение или None в случае ошибки
        """
        try:
            if not frames:
                logger.error("Не предоставлены кадры для стекинга")
                return None

            # Создаем рабочую директорию если не указана
            work_dir = output_dir or Path("temp_stacking")
            if not work_dir.exists():
                work_dir.mkdir(parents=True)

            # Выполняем стекинг
            stacked = await self._image_processing_service._stack_images(frames, work_dir)
            
            if not stacked:
                logger.error("Ошибка при стекинге изображений")
                return None

            # Выполняем пост-обработку
            final = await self._image_processing_service._post_process(stacked)

            return final

        except Exception as e:
            logger.error(f"Ошибка при стекинге изображений: {str(e)}")
            return None
