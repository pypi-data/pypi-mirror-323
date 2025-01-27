# Python stdlib imports
import logging
from pathlib import Path

# Local imports
from .tables.node import get_node, change_node
from .file_io import load, save, DIR_RASTR_WIN_TEST_9
from .calculations import rgm, run, run_ems
from .settings import settings_for_alt_unit, settings_for_dynamic, settings_for_mdn, settings_for_equivalent, settings_for_regim

# import pywin32
from win32com.client import Dispatch, CDispatch

class RastrWin:
    def __init__(self):
        self.RASTR = Dispatch("Astra.Rastr")
        self.filename = None
    
    def __str__(self):
        """
        Возвращает строковое представление объекта RastrWin.
        """
        return self.RASTR

    def load(self, filename: Path) -> Path:
        """
        Загружает файл в RastrWin.

        Args:
            filename (Path): Путь к файлу.

        Returns:
            Path: Путь к загруженному файлу.
        """  
        self.filename = filename
        return load(rastr_win=self.RASTR, filename=filename)

    def save(self, filename: Path | str | None = None) -> Path:
        """
        Сохраняет текущий файл RastrWin3.

        Returns:
            Path: Путь к сохраненному файлу.
        """
        if filename is not None:
            return save(rastr_win=self.RASTR, filename=filename)
        return save(rastr_win=self.RASTR, filename=self.filename)

    def rgm(self) -> bool:
        """
        Выполняет операцию расчета режима в ПВК RastrWin3.

        Returns:
            bool: Результат операции rgm.
        """
        return rgm(rastr_win=self.RASTR)

    def get_node(self, param: str, row: int) -> float | str | int | None:
        """
        Возвращает значение параметра узла в таблице RastrWin.

        Args:
            param (str): Параметр узла, значение которого нужно получить.
            row (int): Номер строки в таблице узлов.

        Returns:
            float | str | int | None: Значение параметра узла или None, если произошла ошибка.
        """
        return get_node(rastr_win=self.RASTR, param=param, row=row)

    def chenge_node(self, param: str, row: int, value: float | str | int, rastr_win: CDispatch | None = None) -> bool:
        """
        Изменяет значение параметра узла в таблице RastrWin.

        Args:
            param (str): Параметр узла, который нужно изменить.
            row (int): Номер строки в таблице узлов.
            value (float | str | int): Новое значение параметра.
            rastr_win (CDispatch | None): Объект RastrWin, который нужно использовать для изменения параметра. Если не указан, используется текущий объект RastrWin.

        Returns:
            bool: True, если изменение прошло успешно, False в про тивном случае.
        """
        if rastr_win is not None:
            return change_node(rastr_win=rastr_win, param=param, row=row, value=value)
        return change_node(rastr_win=self.RASTR, param=param, row=row, value=value)