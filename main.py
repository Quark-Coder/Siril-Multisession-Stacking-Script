import asyncio

import click

from pathlib import Path

from src.interface.cli.commands import cli
from src.interface.cli.console_ui import run_console_ui
from src.infrastructure.persistence.settings_repository import SettingsRepository
from src.utils.logging import setup_logging
from config.settings import SETTINGS_DIR, DEFAULT_SIRIL_PATH


async def init_app():
    """
    Инициализация приложения
    """
    # Настройка логирования
    logger = setup_logging()
    
    # Проверка и создание директории настроек
    settings_dir = Path(SETTINGS_DIR)
    if not settings_dir.exists():
        settings_dir.mkdir(parents=True)
        
    # Инициализация репозитория настроек
    settings_repo = SettingsRepository()
    
    # Проверка наличия Siril
    settings = settings_repo.load_settings()
    if not settings:
        siril_path = Path(DEFAULT_SIRIL_PATH)
        if siril_path.exists():
            settings_repo.save_settings({
                'siril_path': str(siril_path),
                'bit_depth': '32'
            })
        else:
            logger.warning("Siril не найден в стандартном расположении")
            return False
            
    return True


@click.command()
@click.option('--interactive', '-i', is_flag=True, help='Запустить в интерактивном режиме')
def main(interactive):
    """
    Точка входа в приложение
    """
    try:
        # Инициализация приложения
        if not asyncio.run(init_app()):
            click.echo("Ошибка инициализации приложения. Проверьте наличие Siril.")
            return
        
        if interactive:
            # Запуск интерактивного режима
            run_console_ui()
        else:
            # Запуск CLI интерфейса
            cli()
        
    except Exception as e:
        click.echo(f"Критическая ошибка: {str(e)}")
        return


if __name__ == "__main__":
    main()
