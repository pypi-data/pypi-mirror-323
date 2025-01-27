"""
Данный модуль предназначен для запуска встроенного алгоритма МДП в RastrWin3 (СМЗУ).
"""

# import Python lib
import logging

# import win32com
from win32com.client import CDispatch


logger = logging.getLogger("PyRastrWin")


def mdp(rastr_win: CDispatch) -> bool:
    """
    Функция для расчета МДП.

    Args:
        rastr_win: Dispatch("Astra.Rastr").
    Return:
        True - yспешный расчет МДП; False - Аварийное завершение расчета МДП.
    """
    _kod = rastr_win.Emergencies("")
    kod = _kod[0]
    if kod > 0:
        logger.info(f"Расчет МДП завершен успешно.")
        return True
    else:
        logger.warning(f"Расчет МДП завершен аварийно.")
        return False
