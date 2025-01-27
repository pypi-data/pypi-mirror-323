"""
Модуль для пересчета тока нагрузки по различным параметрам в RastrWin3.

Этот модуль предоставляет функциональность для работы с системой RastrWin3,
включая пересчет допустимых токов нагрузки (ТНВ) на основе температуры воздуха и процента перегрузки по току.

В GUI RastrWin3 - это функция работает с помощью нажатия кнопки F9 -> Расчет T доп от Т

Основная функция:
- calc_i_dop: Пересчет допустимых токов нагрузки (ТНВ) для модели в RastrWin3.
"""

# import Python
import logging
from dataclasses import dataclass

# import win32com
from win32com.client import CDispatch

logger = logging.getLogger("PyRastrWin")


@dataclass(frozen=True, slots=True)
class ResultCalcIdop:
    """
    Допустимые токи нагрузки (ТНВ) на основе температуры воздуха и процента перегрузки по току.

    Args:
        temperature_air (float): Температура воздуха в градусах Цельсия.
        emergency_load (float): Процент перегрузки по току (например, 20.0 для 20%).
        viborka (str): Выборка по которой.
    """

    temperature_air: float
    emergency_load: float
    viborka: str


def calc_i_dop(
    rastr_win: CDispatch, t_air: float, i_overload_percent: float, viborka: str
) -> ResultCalcIdop:
    """Пересчитывает допустимые токи нагрузки (ТНВ) на основе температуры воздуха и процента перегрузки по току.

    Args:
        rastr_win (CDispatch): Dispatch("Astra.Rastr").
        t_air (float): Температура воздуха в градусах Цельсия.
        i_overload_percent (float): Процент перегрузки по току (например, 20.0 для 20%).
        viborka (str): Название выборки для расчета в системе RastrWin3.

    Returns:
        ResultCalcIdop: Результат расчета допустимых токов нагрузки.
   """
    rastr_win.CalcIdop(t_air, i_overload_percent, viborka)
    logger.info("Выставлена температура %s, по выборке %s", t_air, viborka)
    return ResultCalcIdop(
        temperature_air=t_air, emergency_load=i_overload_percent, viborka=viborka
    )
