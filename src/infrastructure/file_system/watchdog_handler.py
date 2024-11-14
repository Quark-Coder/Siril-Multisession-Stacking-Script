from pathlib import Path
from typing import Optional, Callable

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from src.utils.logging import get_logger
from src.domain.entities.image import Image
from config.settings import FILE_PREFIXES

logger = get_logger(__name__)


class AstroImageEventHandler(FileSystemEventHandler):
    """
    Обработчик событий файловой системы для астрономических изображений
    """
    def __init__(self, 
                 directory: Path,
                 prefix_to_watch: str,
                 on_image_created: Optional[Callable[[Image], None]] = None):
        """
        Инициализация обработчика событий
        
        Args:
            directory: Директория для мониторинга
            prefix_to_watch: Префикс файлов для отслеживания
            on_image_created: Callback-функция, вызываемая при создании нового изображения
        """
        self.directory = Path(directory)
        self.prefix_to_watch = prefix_to_watch
        self.on_image_created = on_image_created
        
    def on_created(self, event: FileCreatedEvent) -> None:
        """
        Обработка события создания файла
        
        Args:
            event: Событие создания файла
        """
        if not event.is_directory:
            file_path = Path(event.src_path)
            
            # Проверяем, соответствует ли файл ожидаемому префиксу
            if file_path.name.startswith(self.prefix_to_watch):
                try:
                    logger.debug(f"Обнаружен новый файл: {file_path}")
                    
                    # Создаем объект изображения
                    image = Image(file_path=file_path)
                    
                    # Если задан callback, вызываем его
                    if self.on_image_created:
                        self.on_image_created(image)
                        
                except Exception as e:
                    logger.error(f"Ошибка при обработке файла {file_path}: {str(e)}")


class FileSystemWatcher:
    """
    Класс для мониторинга файловой системы
    """
    def __init__(self):
        self.observer = Observer()
        self._handlers = []
        
    def watch_directory(self, 
                       directory: Path,
                       prefix: str,
                       callback: Optional[Callable[[Image], None]] = None) -> None:
        """
        Начать мониторинг директории
        
        Args:
            directory: Директория для мониторинга
            prefix: Префикс файлов для отслеживания
            callback: Функция обратного вызова для новых файлов
        """
        try:
            handler = AstroImageEventHandler(directory, prefix, callback)
            self.observer.schedule(handler, str(directory), recursive=False)
            self._handlers.append(handler)
            
            if not self.observer.is_alive():
                self.observer.start()
                logger.info(f"Начат мониторинг директории: {directory}")
                
        except Exception as e:
            logger.error(f"Ошибка при настройке мониторинга директории {directory}: {str(e)}")
            
    def stop(self) -> None:
        """
        Остановить мониторинг всех директорий
        """
        try:
            if self.observer.is_alive():
                self.observer.stop()
                self.observer.join()
                logger.info("Мониторинг файловой системы остановлен")
                
        except Exception as e:
            logger.error(f"Ошибка при остановке мониторинга: {str(e)}")
