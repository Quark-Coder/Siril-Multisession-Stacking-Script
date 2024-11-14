import asyncio

import click

from pathlib import Path
from typing import Optional

from src.application.use_cases.calibrate_frames import CalibrateFramesUseCase
from src.application.use_cases.process_session import ProcessSessionUseCase
from src.application.use_cases.stack_images import StackImagesUseCase
from src.domain.entities.session import Session, SessionMetadata
from src.domain.entities.calibration_frames import CalibrationFrameLibrary
from src.application.services.image_processing_service import ImageProcessingService
from src.infrastructure.siril.siril_wrapper import SirilWrapper
from src.infrastructure.file_system.file_manager import FileSystemManager
from src.infrastructure.image_processing.image_processor import SirilImageProcessor
from src.infrastructure.persistence.settings_repository import SettingsRepository
from src.utils.validators import validate_path, validate_session_directory
from src.utils.logging import get_logger

logger = get_logger(__name__)


def init_services():
    """Инициализация сервисов"""
    settings_repo = SettingsRepository()
    settings = settings_repo.load_settings()
    
    file_manager = FileSystemManager()
    image_processor = SirilImageProcessor()
    siril_wrapper = SirilWrapper(settings.get('siril_path') if settings else None)
    
    return ImageProcessingService(image_processor, file_manager, siril_wrapper)


@click.group()
def cli():
    """Утилита для обработки астрофотографий"""
    pass


@cli.command()
@click.argument('session_path', type=click.Path(exists=True))
@click.option('--calibration-dir', type=click.Path(exists=True), help='Директория с калибровочными кадрами')
@click.option('--output-dir', type=click.Path(), help='Директория для результатов')
def process_session(session_path: str, calibration_dir: Optional[str], output_dir: Optional[str]):
    """Обработка сессии астрофотографии"""
    try:
        # Валидация путей
        session_path = Path(session_path)
        if not validate_session_directory(session_path):
            click.echo("Неверная структура директории сессии")
            return

        # Инициализация сервисов
        image_processing_service = init_services()
        
        # Создание сессии
        metadata = SessionMetadata(
            name=session_path.name,
            target_name=session_path.name,
            date=None
        )
        session = Session(session_path, metadata)
        
        # Загрузка калибровочной библиотеки
        calibration_library = None
        if calibration_dir:
            calibration_library = CalibrationFrameLibrary(Path(calibration_dir))
        
        # Создание выходной директории
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Выполнение обработки
        use_case = ProcessSessionUseCase(image_processing_service)
        result = asyncio.run(use_case.execute(session, calibration_library))
        
        if result:
            click.echo(f"Обработка завершена успешно. Результат сохранен: {result.file_path}")
        else:
            click.echo("Ошибка при обработке сессии")
            
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        click.echo(f"Произошла ошибка: {str(e)}")


@cli.command()
@click.argument('frames_dir', type=click.Path(exists=True))
@click.option('--output-dir', type=click.Path(), help='Директория для результата')
@click.option('--method', type=click.Choice(['average', 'median', 'sigma_clip']), default='sigma_clip')
def stack_images(frames_dir: str, output_dir: Optional[str], method: str):
    """Стекинг набора кадров"""
    try:
        frames_path = Path(frames_dir)
        if not validate_path(frames_path):
            click.echo("Неверный путь к директории с кадрами")
            return

        # Инициализация сервисов
        image_processing_service = init_services()
        
        # Получение списка кадров
        file_manager = FileSystemManager()
        frames = file_manager.get_light_frames(frames_path)
        
        if not frames:
            click.echo("Не найдены кадры для стекинга")
            return
            
        # Создание выходной директории
        output_path = Path(output_dir) if output_dir else None
        if output_path:
            output_path.mkdir(parents=True, exist_ok=True)
        
        # Выполнение стекинга
        use_case = StackImagesUseCase(image_processing_service)
        result = asyncio.run(use_case.execute(frames, output_path))
        
        if result:
            click.echo(f"Стекинг выполнен успешно. Результат сохранен: {result.file_path}")
        else:
            click.echo("Ошибка при стекинге изображений")
            
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        click.echo(f"Произошла ошибка: {str(e)}")


@cli.command()
@click.argument('frames_dir', type=click.Path(exists=True))
@click.option('--output-dir', type=click.Path(), help='Директория для результатов')
@click.option('--master-dark', type=click.Path(exists=True), help='Путь к master dark')
@click.option('--master-flat', type=click.Path(exists=True), help='Путь к master flat')
@click.option('--master-bias', type=click.Path(exists=True), help='Путь к master bias')
def calibrate_frames(frames_dir: str, output_dir: Optional[str], 
                    master_dark: Optional[str], master_flat: Optional[str], 
                    master_bias: Optional[str]):
    """Калибровка набора кадров"""
    try:
        frames_path = Path(frames_dir)
        if not validate_path(frames_path):
            click.echo("Неверный путь к директории с кадрами")
            return

        # Инициализация сервисов
        image_processing_service = init_services()
        
        # Получение списка кадров
        file_manager = FileSystemManager()
        frames = file_manager.get_light_frames(frames_path)
        
        if not frames:
            click.echo("Не найдены кадры для калибровки")
            return
            
        # Создание выходной директории
        output_path = Path(output_dir) if output_dir else None
        if output_path:
            output_path.mkdir(parents=True, exist_ok=True)
        
        # Создание калибровочной библиотеки
        calibration_library = CalibrationFrameLibrary()
        if master_dark:
            calibration_library.add_master_dark(Path(master_dark))
        if master_flat:
            calibration_library.add_master_flat(Path(master_flat))
        if master_bias:
            calibration_library.add_master_bias(Path(master_bias))
        
        # Выполнение калибровки
        use_case = CalibrateFramesUseCase(image_processing_service)
        results = asyncio.run(use_case.execute(frames, calibration_library, output_path))
        
        if results:
            click.echo(f"Калибровка выполнена успешно. Обработа��о кадров: {len(results)}")
        else:
            click.echo("Ошибка при калибровке кадров")
            
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        click.echo(f"Произошла ошибка: {str(e)}")


if __name__ == '__main__':
    cli()
