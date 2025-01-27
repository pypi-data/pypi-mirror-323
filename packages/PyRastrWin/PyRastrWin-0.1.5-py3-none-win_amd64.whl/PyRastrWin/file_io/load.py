# Python stdlib imports
import logging
from os.path import splitext
from pathlib import Path

# import win32com
from win32com.client import CDispatch

# Python project imports
from .directories import get_filename_shablon, extension_shablon


logger = logging.getLogger("PyRastrWin")


def load(
    rastr_win: CDispatch,
    filename: Path,
    name_template: str = "",
    kod_rg: int = 1,
) -> Path:
    """
    Загружает файл данных path_file в рабочую область в соответствии с шаблоном типа "path_or_name_shabl".
    - если не задано название или путь шаблона: name_template, то загружается - шаблон по расширению файла;
    - если не задано название или путь к файлу: path_file, то загружается только шаблон (пустой шаблон).

    Args:
        rastr_win: Dispatch("Astra.Rastr").
        kod_rg: Числовое значение, определяет режим загрузки при наличии таблицы в рабочей области.
            kod_rg = 0 - Таблица добавляется к имеющейся в рабочей области, совпадение ключевых полей не контролируются
                (соответствует режиму «Присоединить» в меню);
            kod_rg = 1 - Таблица в рабочей области замещается (соответствует режиму «Загрузить» в меню);
            kod_rg = 2 - Данные в таблице, имеющие одинаковые ключевые поля, заменяются. Если ключ не найден,
                то данные игнорируются (соответствует режиму «Обновить» в меню);
            kod_rg = 3 - Данные в таблице, имеющие одинаковые ключевые поля, заменяются. Если ключ не найден,
                то данные вставляются (соответствует режиму «Объединить»);

        filename: абсолютный путь с именем файла (пример: Path("C:\\Folder\\ДРМ.rst").
        name_template: Шаблон RastrWin3 для загрузки пример:
            - если задаем шаблон через название: "режим", "динамика", "сценарий" итд.
            - если задаем шаблон через путь: C:\\Users\\User\\Documents\\RastrWin3\\SHABLON\\динамика.rst
    Returns: Path(filename)
    """
    if name_template:
        directory_shabl = get_filename_shablon(name_template=name_template)
        try:
            rastr_win.Load(kod_rg, filename, directory_shabl)
            logger.info(
                f'Загружен файл: "{filename}";\nпо шаблону: "{directory_shabl}".'
            )
            return Path(filename)
        except Exception as e:
            logger.error(f"При загрузке файла возникла следующая ошибка: {e}")
            return Path(filename)
    else:
        _, file_extension = splitext(filename)
        directory_shabl = extension_shablon(extension_template=file_extension)
        if directory_shabl:
            try:
                rastr_win.Load(kod_rg, filename, directory_shabl)
                logger.info(
                    f'Загружен файл: "{filename}";'
                    f'\nпо шаблону: "{directory_shabl}".'
                )
                return Path(filename)
            except Exception as e:
                logger.error(f"При загрузке файла возникла следующая ошибка: {e}")
                return Path(filename)
