# Python stdlib imports
import logging
from os.path import splitext
from pathlib import Path

# Python project imports
from .directories import get_filename_shablon, extension_shablon

# import win32com
from win32com.client import CDispatch

logger = logging.getLogger("PyRastrWin")


def save(
    rastr_win: CDispatch,
    filename: Path,
    name_template: Path or None = None, # type: ignore
) -> Path:
    """
    Сохраняет информацию из рабочей области в файле path_file по шаблону name_template.
    :param rastr_win: Dispatch("Astra.Rastr").
    :param filename: директория и название файла сохранения файла.
    :param name_template: шаблон RastrWin3 для сохранения. Defaults to None.
    :returns: Path(filename)
    """
    if name_template:
        directory_shabl = get_filename_shablon(name_template=name_template)
        rastr_win.Save(filename, directory_shabl)
        logger.info(f'Сохранен файл: "{filename}";\nпо шаблону: "{directory_shabl}".')
        return Path(filename)
    else:
        _, file_extension = splitext(filename)
        directory_shabl = extension_shablon(extension_template=file_extension)
        if directory_shabl:
            if filename:
                rastr_win.Save(filename, directory_shabl)
                logger.info(
                    f'Сохранен файл: "{filename}";\nпо шаблону: "{directory_shabl}".'
                )
                return Path(filename)
        else:
            logger.error(
                f"Error: файл {filename} - не сохранен по причине невозможности подобрать шаблон!"
            )
            return Path(filename)
