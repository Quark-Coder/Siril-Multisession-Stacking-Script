import logging

from functools import lru_cache
from typing import Optional

from config.logging_config import setup_logging


@lru_cache()
def get_logger(name: str) -> logging.Logger:
    """
    Возвращает настроенный логгер для указанного модуля.
    Использует кэширование для предотвращения повторной инициализации.
    
    Args:
        name: Имя модуля/компонента для логгера
        
    Returns:
        logging.Logger: Настроенный экземпляр логгера
    """
    logger = logging.getLogger(name)
    
    # Если логгер еще не настроен
    if not logger.handlers:
        setup_logging()
        
    return logger


def log_execution_time(logger: Optional[logging.Logger] = None):
    """
    Декоратор для логирования времени выполнения функций.
    
    Args:
        logger: Опциональный логгер. Если не указан, будет создан новый.
    """
    import time
    from functools import wraps
    
    def decorator(func):
        nonlocal logger
        if logger is None:
            logger = get_logger(func.__module__)
            
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.debug(
                    f"Функция {func.__name__} выполнена за {execution_time:.2f} секунд"
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"Ошибка в функции {func.__name__} после {execution_time:.2f} "
                    f"секунд выполнения: {str(e)}"
                )
                raise
        return wrapper
    return decorator


def log_error(logger: Optional[logging.Logger] = None):
    """
    Декоратор для логирования ошибок функций.
    
    Args:
        logger: Опциональный логгер. Если не указан, будет создан новый.
    """
    def decorator(func):
        nonlocal logger
        if logger is None:
            logger = get_logger(func.__module__)
            
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Ошибка в функции {func.__name__}: {str(e)}",
                    exc_info=True
                )
                raise
        return wrapper
    return decorator
