import os

# Настройки путей
DEFAULT_SIRIL_PATH = "C:\\Program Files\\Siril\\bin\\siril.exe"
SETTINGS_DIR = os.path.join(os.environ['APPDATA'], 'multisession-script')
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "settings.txt")

# Настройки обработки изображений
DEFAULT_BIT_DEPTH = "32"  # Можно выбрать "16" или "32"
IMAGE_EXTENSION = "fit"   # Расширение для сохранения файлов

# Параметры стекинга
STACK_SETTINGS = {
    'sigma_low': 3,
    'sigma_high': 3,
    'norm_type': 'addscale',
    'output_norm': True,
    'rgb_equal': True
}

# Параметры калибровки
CALIBRATION_SETTINGS = {
    'cfa': True,
    'equalize_cfa': True,
    'debayer': None  # Будет установлено в зависимости от типа изображений
}

# Названия папок
FOLDER_NAMES = {
    'lights': "lights",
    'darks': "darks",
    'flats': "flats",
    'biases': "biases",
    'process': "process",
    'calibrated': "calibrated"
}

# Префиксы файлов
FILE_PREFIXES = {
    'light': "light",
    'dark': "dark",
    'flat': "flat",
    'bias': "bias",
    'pp': "pp",
    'stacked': "stacked"
}

# Поддерживаемые форматы файлов
SUPPORTED_EXTENSIONS = ('.fit', '.FIT', '.fits', '.FITS', '.raw', '.nef', '.cr2', '.cr3', '.arw')
