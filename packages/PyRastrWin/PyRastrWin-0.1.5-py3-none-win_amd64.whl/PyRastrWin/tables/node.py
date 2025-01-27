# import Python
import logging

# import win32com
from win32com.client import CDispatch

logger = logging.getLogger("PyRastrWin")


def change_node(rastr_win: CDispatch, param: str, row: int, value: float | str | int) -> bool:
    """
    Изменяет значение параметра узла в таблице RastrWin.

    Args:
        rastr_win (CDispatch): Объект RastrWin.
        param (str): Параметр узла, который нужно изменить.
        row (int): Номер строки в таблице узлов.
        value (float | str | int): Новое значение параметра.

    Returns:
        bool: True, если изменение прошло успешно, False в противном случае.
    """
    try:
        tb_node = rastr_win.Tables("node")
        tb_node.Cols(param).SetZ(row, value)
        return True
    except Exception as e:
        logger.error(e)
        return False
    

def get_node(rastr_win: CDispatch, param: str, row: int) -> float | str | int | None:
    """
    Возвращает значение параметра узла в таблице RastrWin.

    Args:
        rastr_win (CDispatch): Объект RastrWin.
        param (str): Параметр узла, значение которого нужно получить.
        row (int): Номер строки в таблице узлов.

    Returns:
        float | str | int | None: Значение параметра узла или None, если произошла ошибка.
    """
    try:
        tb_node = rastr_win.Tables("node")
        return tb_node.Cols(param).Z(row)
    except Exception as e:
        logger.error(e)
        return None