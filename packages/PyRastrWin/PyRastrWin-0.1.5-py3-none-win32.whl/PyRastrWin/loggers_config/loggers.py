# Python stdlib imports
from datetime import datetime

# Python stdlib imports
import logging


def configure_logging_save_file(level=logging.DEBUG) -> None:
    """
    Config вывода logging

    :param level:
    :return: None
    """
    logger = logging.getLogger("PyRastrWin")
    logger.setLevel(level)
    logger.propagate = False
    if not logger.hasHandlers():
        file_handler = logging.FileHandler(
            filename=f'C:/tmp/logs_{datetime.now().strftime("%d.%m.%Y %Hh%Mm%Ss")}.log',
            mode="a",
        )
        file_handler.setLevel(level)
        formatter = logging.Formatter(
            fmt="[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)

        # Обработчик для вывода логов в консоль
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)

        # Добавляем обработчики к логгеру
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
