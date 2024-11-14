from typing import Optional

from src.utils.logging import get_logger

logger = get_logger(__name__)


class SirilCommands:
    """
    Класс, содержащий команды для работы с Siril
    """
    
    @staticmethod
    def cd(directory: str) -> str:
        """
        Команда смены директории
        """
        return f"cd {directory}"
        
    @staticmethod
    def convert(prefix: str, out: Optional[str] = None) -> str:
        """
        Команда конвертации файлов
        """
        command = f"convert {prefix}"
        if out:
            command += f" -out={out}"
        return command
        
    @staticmethod
    def stack(prefix: str,
              type: str = 'rej',
              sigma_low: float = 3.0,
              sigma_high: float = 3.0,
              norm: str = 'no',
              output_norm: bool = False,
              rgb_equal: bool = False,
              out: Optional[str] = None) -> str:
        """
        Команда стекинга изображений
        """
        command = f"stack {prefix} -type={type}"
        command += f" -sigma_low={sigma_low} -sigma_high={sigma_high}"
        command += f" -norm={norm}"
        
        if output_norm:
            command += " -output_norm"
        if rgb_equal:
            command += " -rgb_equal"
        if out:
            command += f" -out={out}"
            
        return command
        
    @staticmethod
    def calibrate(prefix: str, **kwargs) -> str:
        """
        Команда калибровки изображений
        
        Поддерживаемые параметры:
        - bias: str - путь к master bias
        - dark: str - путь к master dark
        - flat: str - путь к master flat
        - cc: str - цветовая коррекция
        - cfa: bool - использовать CFA
        - equalize_cfa: bool - выровнять CFA
        - debayer: bool - выполнить дебайеризацию
        """
        command = f"calibrate {prefix}"
        
        for key, value in kwargs.items():
            if isinstance(value, bool):
                if value:
                    command += f" -{key}"
            else:
                command += f" -{key}={value}"
                
        return command
        
    @staticmethod
    def register(prefix: str,
                reference: Optional[str] = None,
                min_stars: int = 100,
                max_stars: int = 500) -> str:
        """
        Команда регистрации изображений
        """
        command = f"register {prefix}"
        
        if reference:
            command += f" -reference={reference}"
        command += f" -min_stars={min_stars} -max_stars={max_stars}"
        
        return command
        
    @staticmethod
    def setext(extension: str) -> str:
        """
        Установка расширения для выходных файлов
        """
        return f"setext {extension}"
        
    @staticmethod
    def set32bits() -> str:
        """
        Установка 32-битной обработки
        """
        return "set32bits"
        
    @staticmethod
    def set16bits() -> str:
        """
        Установка 16-битной обработки
        """
        return "set16bits"
