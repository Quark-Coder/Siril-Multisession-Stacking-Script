import os
import click

from pathlib import Path
from typing import Optional
from datetime import datetime

from src.domain.entities.session import SessionMetadata
from src.utils.logging import get_logger
from src.interface.cli.commands import (
    init_services, process_session, stack_images, calibrate_frames
)

logger = get_logger(__name__)


class ConsoleUI:
    """Интерактивный консольный интерфейс приложения"""
    
    def __init__(self):
        self.image_processing_service = init_services()
        
    def clear_screen(self):
        """Очистка экрана консоли"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print_header(self, title: str):
        """Вывод заголовка меню"""
        self.clear_screen()
        click.echo("=" * 50)
        click.echo(f"{title:^50}")
        click.echo("=" * 50)
        click.echo()
        
    def get_path_input(self, prompt: str, must_exist: bool = True) -> Optional[Path]:
        """Получение пути от пользователя"""
        while True:
            path_str = click.prompt(prompt, type=str, default='')
            if path_str.lower() == 'отмена':
                return None
                
            path = Path(path_str)
            if must_exist and not path.exists():
                click.echo("Указанный путь не существует. Попробуйте снова или введите 'отмена'")
                continue

            if not must_exist and len(path_str) == 0:
                return None
            
            return path
            
    def get_session_metadata(self) -> SessionMetadata:
        """Интерактивный ввод метаданных сессии"""
        click.echo("\nВведите метаданные сессии:")
        name = click.prompt("Название сессии", type=str)
        target = click.prompt("Название объекта съёмки", type=str)
        date_str = click.prompt("Дата съёмки (ГГГГ-ММ-ДД)", type=str, default='')
        
        date = None
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                click.echo("Неверный формат даты. Используется значение по умолчанию.")
        
        return SessionMetadata(
            name=name,
            target_name=target,
            date=date
        )
        
    def show_main_menu(self):
        """Отображение главного меню"""
        while True:
            self.print_header("Главное меню")
            click.echo("1. Обработать сессию")
            click.echo("2. Выполнить стекинг кадров")
            click.echo("3. Калибровать кадры")
            click.echo("4. Настройки")
            click.echo("0. Выход")
            click.echo()
            
            choice = click.prompt("Выберите действие", type=int)
            
            if choice == 0:
                break
            elif choice == 1:
                self.show_process_session_menu()
            elif choice == 2:
                self.show_stack_frames_menu()
            elif choice == 3:
                self.show_calibration_menu()
            elif choice == 4:
                self.show_settings_menu()
                
    def show_process_session_menu(self):
        """Меню обработки сессии"""
        self.print_header("Обработка сессии")
        
        # Получаем необходимые пути
        session_path = self.get_path_input("Путь к директории сессии")
        if not session_path:
            return
            
        calibration_dir = self.get_path_input(
            "Путь к директории с калибровочными кадрами (Enter для пропуска)",
            must_exist=False
        )
        
        output_dir = self.get_path_input(
            "Путь для сохранения результатов (Enter для пропуска)",
            must_exist=False
        )
        
        # Запускаем обработку через CLI команду
        ctx = click.Context(process_session)
        process_session.invoke(ctx, str(session_path),
                             calibration_dir=str(calibration_dir) if calibration_dir else None,
                             output_dir=str(output_dir) if output_dir else None)
                             
        click.pause()
        
    def show_stack_frames_menu(self):
        """Меню стекинга кадров"""
        self.print_header("Стекинг кадров")
        
        frames_dir = self.get_path_input("Путь к директории с кадрами")
        if not frames_dir:
            return
            
        output_dir = self.get_path_input(
            "Путь для сохранения результата (Enter для пропуска)",
            must_exist=False
        )
        
        methods = ['average', 'median', 'sigma_clip']
        click.echo("\nДоступные методы стекинга:")
        for i, method in enumerate(methods, 1):
            click.echo(f"{i}. {method}")
            
        method_idx = click.prompt("Выберите метод", type=click.IntRange(1, len(methods))) - 1
        
        # Запускаем стекинг через CLI команду
        ctx = click.Context(stack_images)
        stack_images.invoke(ctx, str(frames_dir),
                          output_dir=str(output_dir) if output_dir else None,
                          method=methods[method_idx])
                          
        click.pause()
        
    def show_calibration_menu(self):
        """Меню калибровки кадров"""
        self.print_header("Калибровка кадров")
        
        frames_dir = self.get_path_input("Путь к директории с кадрами")
        if not frames_dir:
            return
            
        output_dir = self.get_path_input(
            "Путь для сохранения результатов (Enter для пропуска)",
            must_exist=False
        )
        
        # Получаем пути к мастер-кадрам
        master_dark = self.get_path_input(
            "Путь к master dark (Enter для пропуска)",
            must_exist=False
        )
        
        master_flat = self.get_path_input(
            "Путь к master flat (Enter для пропуска)",
            must_exist=False
        )
        
        master_bias = self.get_path_input(
            "Путь к master bias (Enter для пропуска)",
            must_exist=False
        )
        
        # Запускаем калибровку через CLI команду
        ctx = click.Context(calibrate_frames)
        calibrate_frames.invoke(ctx, str(frames_dir),
                              output_dir=str(output_dir) if output_dir else None,
                              master_dark=str(master_dark) if master_dark else None,
                              master_flat=str(master_flat) if master_flat else None,
                              master_bias=str(master_bias) if master_bias else None)
                              
        click.pause()
        
    def show_settings_menu(self):
        """Меню настроек"""
        self.print_header("Настройки")
        # TODO: Добавить управление настройками
        click.echo("Раздел в разработке")
        click.pause()


def run_console_ui():
    """Запуск интерактивного консольного интерфейса"""
    ui = ConsoleUI()
    try:
        ui.show_main_menu()
    except KeyboardInterrupt:
        click.echo("\nРабота программы завершена")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {str(e)}")
        click.echo(f"Произошла ошибка: {str(e)}")


if __name__ == '__main__':
    run_console_ui()
