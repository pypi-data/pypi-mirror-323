"""
Каждой физической величине, хранимой в программе, соответствует единица измерения,
задаваемая в настройках программы (Файлы – Настройки – Данные).
Существуют основные и альтернативные единицы измерения.
В основных единицах измерения осуществляется хранение и обработка информации в программе.
Для задания альтернативных единиц измерения необходимо описать преобразование между
основными и альтернативными единицами в специальной таблице, в этом случае ввод и отображение данных
осуществляется в альтернативных, а хранение и обработка по-прежнему в основных единицах.

Для задания альтернативных единиц измерения служит таблица «Ед. Измерения» (Расчеты – Параметры)

«A» - признак активности (пересчет в альтернативные единицы происходит только для строк с установленным признаком;
«ЕИ» - основные единицы измерения;
«Альт.ЕИ» - альтернативные единицы измерения;
«Формула» - формула для пересчета основных единиц в альтернативные;
«Точность» - точность отображения альтернативных единиц измерения;
«Табл» - ограничение действия альтернативных единиц конкретной таблицей.
"""

# import Python
import logging

# import win32com
from win32com.client import CDispatch

logger = logging.getLogger("PyRastrWin")


def settings_for_alt_unit(rastr_win: CDispatch) -> None:
    """
    Заполняет таблицу Ед.Измерения для переключения единиц измерения.
    :param rastr_win: Dispatch("Astra.Rastr).
    :return: List[AltUnit]
    """
    logger.info("Задана таблица Ед.Измерения для переключения единиц измерения")
    tb_alt_unit = rastr_win.Tables("AltUnit")
    tb_alt_unit.DelRowS()
    tb_alt_unit.Size = 2
    tb_alt_unit.Cols("Activ").SetZ(0, 1)
    tb_alt_unit.Cols("Unit").SetZ(0, "Ом")
    tb_alt_unit.Cols("Alt").SetZ(0, "о.е.")
    tb_alt_unit.Cols("Formula").SetZ(0, "nonz(Pnom/nonz((Ugnom*Ugnom*nonz(cosFi))))")
    tb_alt_unit.Cols("Prec").SetZ(0, 4)
    tb_alt_unit.Cols("Tabl").SetZ(0, "Generator,SynchronousMotor")

    tb_alt_unit.Cols("Activ").SetZ(1, 1)
    tb_alt_unit.Cols("Unit").SetZ(1, "МВт*с")
    tb_alt_unit.Cols("Alt").SetZ(1, "с")
    tb_alt_unit.Cols("Formula").SetZ(1, "1/nonz(Pnom)")
    tb_alt_unit.Cols("Prec").SetZ(1, 3)
    tb_alt_unit.Cols("Tabl").SetZ(1, "Generator,SynchronousMotor")
