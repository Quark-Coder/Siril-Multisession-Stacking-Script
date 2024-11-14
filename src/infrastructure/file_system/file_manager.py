import shutil

from pathlib import Path
from typing import List, Optional, Dict

from src.domain.interfaces.file_manager import FileManager
from src.domain.entities.calibration_frames import CalibrationFrameType
from src.domain.entities.image import Image
from src.utils.logging import get_logger
from config.settings import SUPPORTED_EXTENSIONS, FOLDER_NAMES

logger = get_logger(__name__)


class FileSystemManager(FileManager):
    """
    Реализация FileManager для работы с файловой системой
    """
    
    def create_session_directory(self, session_name: str) -> Path:
        """
        Создает директорию для новой сессии
        """
        session_dir = Path.cwd() / session_name
        try:
            session_dir.mkdir(parents=True, exist_ok=True)
            for folder in FOLDER_NAMES.values():
                (session_dir / folder).mkdir(exist_ok=True)
            logger.info(f"Создана директория сессии: {session_dir}")
            return session_dir
        except Exception as e:
            logger.error(f"Ошибка при создании директории сессии: {e}")
            raise
            
    def create_calibration_directory(self, 
                                   session_dir: Path,
                                   frame_type: CalibrationFrameType) -> Path:
        """
        Создает директорию для калибровочных кадров
        """
        calibration_dir = session_dir / FOLDER_NAMES[frame_type.value]
        try:
            calibration_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Создана директория для {frame_type.value}: {calibration_dir}")
            return calibration_dir
        except Exception as e:
            logger.error(f"Ошибка при создании директории калибровки: {e}")
            raise
            
    def get_calibration_frames(self,
                             directory: Path,
                             frame_type: CalibrationFrameType) -> List[Image]:
        """
        Получает список калибровочных кадров из директории
        """
        frames = []
        try:
            for file in directory.glob("*"):
                if file.suffix.lower() in SUPPORTED_EXTENSIONS:
                    frames.append(Image(file_path=file))
            logger.info(f"Найдено {len(frames)} {frame_type.value} кадров")
            return frames
        except Exception as e:
            logger.error(f"Ошибка при получении калибровочных кадров: {e}")
            return []
            
    def get_light_frames(self, directory: Path) -> List[Image]:
        """
        Получает список световых кадров из директории
        """
        frames = []
        try:
            for file in directory.glob("*"):
                if file.suffix.lower() in SUPPORTED_EXTENSIONS:
                    frames.append(Image(file_path=file))
            logger.info(f"Найдено {len(frames)} световых кадров")
            return frames
        except Exception as e:
            logger.error(f"Ошибка при получении световых кадров: {e}")
            return []
            
    def save_master_frame(self,
                         image: Image,
                         frame_type: CalibrationFrameType,
                         output_dir: Path) -> Path:
        """
        Сохраняет мастер-кадр
        """
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"master_{frame_type.value}.fit"
            shutil.copy2(image.file_path, output_path)
            logger.info(f"Сохранен мастер-кадр: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Ошибка при сохранении мастер-кадра: {e}")
            raise
            
    def save_calibrated_light(self,
                            image: Image,
                            output_dir: Path,
                            index: Optional[int] = None) -> Path:
        """
        Сохраняет калиброванный световой кадр
        """
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            if index is not None:
                output_path = output_dir / f"calibrated_light_{index:04d}.fit"
            else:
                output_path = output_dir / f"calibrated_{image.name}"
            shutil.copy2(image.file_path, output_path)
            logger.info(f"Сохранен калиброванный кадр: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Ошибка при сохранении калиброванного кадра: {e}")
            raise
            
    def cleanup_temporary_files(self, directory: Path) -> None:
        """
        Очищает временные файлы из директории
        """
        try:
            if directory.exists():
                for file in directory.iterdir():
                    if file.is_file() and file.suffix in ['.tmp', '.seq']:
                        file.unlink()
            logger.info(f"Очищены временные файлы в {directory}")
        except Exception as e:
            logger.error(f"Ошибка при очистке временных файлов: {e}")
            
    def get_session_info(self, session_dir: Path) -> Dict:
        """
        Получает информацию о сессии
        """
        try:
            info = {
                'name': session_dir.name,
                'lights_count': len(list(self.get_light_frames(session_dir / FOLDER_NAMES['lights']))),
                'has_darks': (session_dir / FOLDER_NAMES['darks']).exists(),
                'has_flats': (session_dir / FOLDER_NAMES['flats']).exists(),
                'has_biases': (session_dir / FOLDER_NAMES['biases']).exists()
            }
            logger.info(f"Получена информация о сессии: {info}")
            return info
        except Exception as e:
            logger.error(f"Ошибка при получении информации о сессии: {e}")
            return {}
