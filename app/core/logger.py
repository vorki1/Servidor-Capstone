import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Crear carpeta logs
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Archivo único
LOG_FILE = LOG_DIR / "app.log"

# Formato
FORMAT = "%(asctime)s [%(levelname)s] %(name)s -> %(message)s"

# Formatter
formatter = logging.Formatter(FORMAT)

# Handler consola
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Handler archivo
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=5 * 1024 * 1024,
    backupCount=3,
    encoding="utf-8"
)

file_handler.setFormatter(formatter)

def crear_logger(nombre: str):

    logger = logging.getLogger(nombre)

    # Evitar duplicados
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger