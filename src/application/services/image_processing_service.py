from typing import List, Optional
from pathlib import Path

from src.domain.entities.image import Image
from src.domain.entities.session import Session
from src.domain.entities.calibration_frames import CalibrationFrameLibrary, CalibrationFrameType
from src.domain.interfaces.image_processor import ImageProcessor
from src.domain.interfaces.file_manager import FileManager
from src.infrastructure.siril.siril_wrapper import SirilWrapper
from src.utils.logging import get_logger

logger = get_logger(__name__)


class ImageProcessingService:
    def __init__(
        self,
        image_processor: ImageProcessor,
        file_manager: FileManager,
        siril_wrapper: SirilWrapper
    ):
        self._image_processor = image_processor
        self._file_manager = file_manager
        self._siril_wrapper = siril_wrapper

    async def process_light_frames(
        self,
        session: Session,
        calibration_library: Optional[CalibrationFrameLibrary] = None
    ) -> List[Image]:
        """
        Обработка световых кадров с применением калибровочных кадров
        """
        # Создаём рабочую директорию для сессии
        work_dir = self._file_manager.create_session_directory(f"processing_{session.name}")
        
        try:
            # Получаем световые кадры
            light_frames = self._file_manager.get_light_frames(session.light_frames_dir)
            if not light_frames:
                logger.error("Не найдены световые кадры для обработки")
                return []

            # Применяем калибровку если есть библиотека калибровочных кадров
            if calibration_library and self._has_valid_calibration(calibration_library):
                processed_frames = await self._apply_calibration(
                    light_frames,
                    calibration_library,
                    work_dir,
                    session.exposure_time,
                    session.temperature,
                    session.gain
                )
            else:
                processed_frames = light_frames
            
            # Стекинг и пост-обработка
            stacked_image = await self._stack_images(processed_frames, work_dir)
            final_image = await self._post_process(stacked_image)
            
            # Сохраняем результат
            output_path = self._file_manager.save_calibrated_light(
                final_image,
                work_dir / "result"
            )
            
            return [Image(file_path=output_path)]
            
        finally:
            # Очищаем временные файлы
            self._file_manager.cleanup_temporary_files(work_dir)

    def _has_valid_calibration(self, library: CalibrationFrameLibrary) -> bool:
        """Проверяет наличие необходимых калибровочных кадров"""
        return all([
            library.has_master_frame(CalibrationFrameType.BIAS) or 
            library.has_calibration_frames(CalibrationFrameType.BIAS),
            
            library.has_master_frame(CalibrationFrameType.DARK) or 
            library.has_calibration_frames(CalibrationFrameType.DARK),
            
            library.has_master_frame(CalibrationFrameType.FLAT) or 
            library.has_calibration_frames(CalibrationFrameType.FLAT)
        ])

    async def _apply_calibration(
        self,
        light_frames: List[Image],
        library: CalibrationFrameLibrary,
        work_dir: Path,
        exposure_time: Optional[float] = None,
        temperature: Optional[float] = None,
        gain: Optional[int] = None
    ) -> List[Image]:
        """Применение калибровочных кадров"""
        
        # Создаём директории для калибровочных кадров
        bias_dir = self._file_manager.create_calibration_directory(
            work_dir, CalibrationFrameType.BIAS
        )
        dark_dir = self._file_manager.create_calibration_directory(
            work_dir, CalibrationFrameType.DARK
        )
        flat_dir = self._file_manager.create_calibration_directory(
            work_dir, CalibrationFrameType.FLAT
        )
        
        # Получаем или создаём мастер-кадры
        bias_frames = self._prepare_calibration_frames(
            library.bias_frames,
            bias_dir
        )
        
        dark_frames = self._prepare_calibration_frames(
            library.dark_frames,
            dark_dir
        )
        
        flat_frames = self._prepare_calibration_frames(
            library.flat_frames,
            flat_dir
        )
        
        # Применяем калибровку через Siril
        calibrated_images = await self._siril_wrapper.calibrate_lights(
            [img.file_path for img in light_frames],
            [img.file_path for img in dark_frames],
            [img.file_path for img in flat_frames],
            [img.file_path for img in bias_frames],
            work_dir
        )
        
        return [Image(file_path=path) for path in calibrated_images]

    def _prepare_calibration_frames(
        self,
        frame_set,
        target_dir: Path
    ) -> List[Image]:
        """Подготовка калибровочных кадров определённого типа"""
        if frame_set.master_frame:
            return [Image(file_path=frame_set.master_frame)]
        
        return self._file_manager.get_calibration_frames(
            target_dir,
            frame_set.frame_type
        )

    async def _stack_images(
        self,
        frames: List[Image],
        work_dir: Path
    ) -> Image:
        """Стекинг обработанных кадров"""
        stacked = self._image_processor.stack_images(
            frames,
            output_path=work_dir / "stacked.fit",
            method='sigma_clip',
            sigma_low=2.0,
            sigma_high=2.0,
            normalize=True
        )
        
        if not stacked:
            raise RuntimeError("Ошибка при стекинге изображений")
            
        return stacked

    async def _post_process(self, image: Image) -> Image:
        """
        Пост-обработка изображения:
        1. Нормализация для улучшения динамического диапазона
        2. Дебайеризация, если изображение в формате RAW
        """
        # Нормализация
        normalized = self._image_processor.normalize_image(image)

        if not normalized:
            logger.warning("Ошибка при нормализации изображения")
            normalized = image
            
        # Дебайеризация если необходимо (проверка на RAW формат должна быть в реализации метода)
        final = self._image_processor.debayer_image(normalized)

        if not final:
            logger.warning("Ошибка при дебайеризации изображения")
            final = normalized
            
        return final