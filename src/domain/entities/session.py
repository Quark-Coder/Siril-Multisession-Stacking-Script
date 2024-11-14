from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

from src.domain.entities.calibration_frames import CalibrationFrameLibrary
from src.domain.entities.image import Image
from config.settings import FOLDER_NAMES, SUPPORTED_EXTENSIONS


@dataclass
class SessionMetadata:
    """Метаданные сессии"""
    name: str
    date: str
    target: Optional[str] = None
    exposure_time: Optional[float] = None
    temperature: Optional[float] = None
    gain: Optional[int] = None


class Session:
    """
    Класс, представляющий сессию астрофотосъемки
    """
    def __init__(self, 
                 directory: Path,
                 metadata: SessionMetadata):
        self.directory = directory
        self.metadata = metadata
        self.calibration_library = CalibrationFrameLibrary()
        self._light_frames: List[Image] = []
        self._calibrated_frames: List[Image] = []
        
        # Загружаем световые кадры при инициализации
        if self.lights_directory.exists():
            for ext in SUPPORTED_EXTENSIONS:
                for file_path in self.lights_directory.glob(f'*{ext}'):
                    image = Image(file_path)
                    self.add_light_frame(image)
        
        # Загружаем калиброванные кадры при инициализации
        if self.process_directory.exists():
            for ext in SUPPORTED_EXTENSIONS:
                for file_path in self.process_directory.glob(f'*{ext}'):
                    image = Image(file_path)
                    self.add_calibrated_frame(image)
        
    @property
    def light_frames(self) -> List[Image]:
        """Получить список световых кадров"""
        return self._light_frames
        
    @property
    def calibrated_frames(self) -> List[Image]:
        """Получить список калиброванных кадров"""
        return self._calibrated_frames
    
    def add_light_frame(self, image: Image) -> None:
        """Добавить световой кадр"""
        if not image.file_path.exists():
            raise FileNotFoundError(f"Image file not found: {image.file_path}")
        self._light_frames.append(image)
        
    def add_calibrated_frame(self, image: Image) -> None:
        """Добавить калиброванный кадр"""
        if not image.file_path.exists():
            raise FileNotFoundError(f"Image file not found: {image.file_path}")
        self._calibrated_frames.append(image)

    @property
    def lights_directory(self) -> Path:
        """Получить путь к директории световых кадров"""
        return self.directory / FOLDER_NAMES['lights']
        
    @property
    def darks_directory(self) -> Path:
        """Получить путь к директории темновых кадров"""
        return self.directory / FOLDER_NAMES['darks']
        
    @property
    def flats_directory(self) -> Path:
        """Получить путь к директории плоских кадров"""
        return self.directory / FOLDER_NAMES['flats']
        
    @property
    def biases_directory(self) -> Path:
        """Получить путь к директории bias кадров"""
        return self.directory / FOLDER_NAMES['biases']
        
    @property
    def process_directory(self) -> Path:
        """Получить путь к директории обработки"""
        return self.directory / FOLDER_NAMES['process']
        
    def has_calibration_frames(self) -> bool:
        """Проверить наличие калибровочных кадров"""
        return (self.darks_directory.exists() and any(self.darks_directory.iterdir())) or \
               (self.flats_directory.exists() and any(self.flats_directory.iterdir())) or \
               (self.biases_directory.exists() and any(self.biases_directory.iterdir()))
               
    def validate(self) -> bool:
        """
        Проверить валидность сессии
        """
        if not self.directory.exists():
            return False
            
        if not self.lights_directory.exists() or not any(self.lights_directory.iterdir()):
            return False
            
        return True
        
    def cleanup(self) -> None:
        """
        Очистить временные файлы сессии
        """
        if self.process_directory.exists():
            for file in self.process_directory.iterdir():
                if file.is_file():
                    file.unlink()
