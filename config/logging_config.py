import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging():
    # Создаем директорию для логов, если она не существует
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Настраиваем основной логгер
    logger = logging.getLogger('siril_processor')
    logger.setLevel(logging.DEBUG)

    # Создаем форматтер для логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Настраиваем вывод в файл
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'siril_processor.log'),
        maxBytes=5*1024*1024,  # 5 МБ максимальный размер
        backupCount=3
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Настраиваем вывод в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Добавляем обработчики к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
