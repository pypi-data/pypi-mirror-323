"""
Модуль для запуска расчетов электромеханических переходных процессов (ЭМехПП) на ПВК RastrWin3 (RUSTab)
"""

# Python stdlib imports
import logging
from dataclasses import dataclass
from time import time

# import win32com
from win32com.client import CDispatch

logger = logging.getLogger("PyRastrWin")


@dataclass(frozen=True, slots=True)
class ResultDynamic:
    """
    Результаты расчета Динамики

    :param result_ast_ok: Результат функции RunEMSMode:
        - result_ast_ok = 0 – успешное завершение (т.е. Успешно запущен расчет RunEMSMode и в модели нет ошибок).
        - result_ast_ok = 1 – ошибка в модели;

    :param result_start: Результат функции RunEMSMode:
        - result = True – успешное завершение (т.е. Успешно запущен расчет RunEMSMode и в модели нет ошибок).
        - result = False – ошибка в модели;

    :param result_time_reached: время (Динамики), до которого был рассчитан ЭМПП в EMS-режиме;
    :param runtime: время расчета в секундах;
    :param runtime_format: время расчета в формате: 14h:20m:51s;

    :param result_sync_loss_cause: текстовое сообщение, которое соответствует выведенному в протоколе
        в процессе расчета в EMS-режиме при фиксации причины потери синхронизма доступной в свойстве SyncLossCause:
        - 0 – расчет завершен успешно, потери синхронизма не выявлено;
        - 1 – выявлено превышение угла по ветви значения 180°;
        - 2 – выявлено превышение угла по сопротивлению генератора значения 180°;
        - 4 – выявлено превышение допустимой скорости вращения одного или нескольких генераторов.
        Допустимая скорость вращения задается уставкой автомата безопасности в настройках динамики.

    :param result_message: Результат расчета ЭМПП в EMS-режиме;
    :param system_stable: система устойчива.
    """

    result_ast_ok: int
    result_start: bool
    result_time_reached: float
    runtime: float
    runtime_format: str
    result_sync_loss_cause: int
    result_message: str
    system_stable: bool

    def __str__(self):
        return (
            f"Запуск модели: {"Успешно" if self.result_start else "ошибка в модели"}\n"
            f"Время расчета (ЭМехПП) RUSTab: {self.result_time_reached}\n"
            f"Время расчета: {self.runtime_format}\n"
            f"{"Система устойчива" if self.system_stable else "Система не устойчива"}\n"
            f"Сообщение: {self.result_message}\n"
        )


def run(rastr_win: CDispatch) -> ResultDynamic:
    """
    Запускает расчет ЭМПП в режиме аналогичном, используемому командой пользовательского интерфейса «Динамика».
    В процессе расчета результаты сохраняются в *.sna – файл в соответствии с настройками,
    заданными в параметрах динамики. Расчет выполняется в синхронном режиме – то есть функция
    возвращает управление после завершения расчета.

    :param rastr_win: Dispatch("Astra.Rastr").
    :returns: ResultDynamic
    """
    logger.info("Расчет ЭМехПП запущен в режиме Run().")
    fw_dynamic = rastr_win.FWDynamic()
    start_timer = time()
    result_ast_ok = fw_dynamic.Run()
    stop_timer = time()
    result_time_reached = fw_dynamic.TimeReached
    result_sync_loss_cause = fw_dynamic.SyncLossCause
    result_message = fw_dynamic.ResultMessage
    if result_sync_loss_cause > 0:
        system_stable: bool = False
    else:
        system_stable: bool = True
    if result_ast_ok > 0:
        result_start: bool = False
    else:
        result_start: bool = True

    runtime = stop_timer - start_timer
    hours = int(runtime // (60 * 60))
    minutes = int(runtime % (60 * 60)) // 60
    seconds = int(runtime % 60)
    runtime_format = f"{hours}h:{minutes}m:{seconds}s"

    results = ResultDynamic(
        result_ast_ok=result_ast_ok,
        result_start=result_start,
        result_time_reached=result_time_reached,
        runtime=runtime,
        runtime_format=runtime_format,
        result_sync_loss_cause=result_sync_loss_cause,
        result_message=result_message,
        system_stable=system_stable,
    )

    logger.info("Расчет ЭМехПП окончен.\n%s", results)

    return results


def run_ems(rastr_win: CDispatch) -> ResultDynamic:
    """
    Проводит расчет и возвращает результат расчета ЭМПП в EMS-режиме.

    Args:
        rastr_win: Dispatch("Astra.Rastr").
    Returns
        ResultDynamic
    """
    logger.info("Расчет ЭМехПП запущен в режиме RunEMS().")
    fw_dynamic = rastr_win.FWDynamic()
    start_timer = time()
    result_ast_ok = fw_dynamic.RunEMSMode()
    stop_timer = time()
    result_time_reached = fw_dynamic.TimeReached
    result_message = fw_dynamic.ResultMessage
    result_sync_loss_cause = fw_dynamic.SyncLossCause
    if result_ast_ok > 0:
        result_start: bool = False
    else:
        result_start: bool = True
    runtime = stop_timer - start_timer
    hours = int(runtime // (60 * 60))
    minutes = int(runtime % (60 * 60)) // 60
    seconds = int(runtime % 60)
    runtime_format = f"{hours}h:{minutes}m:{seconds}s"
    if int(result_sync_loss_cause) > 0:
        system_stable: bool = False
    else:
        system_stable: bool = True

    results = ResultDynamic(
        result_ast_ok=result_ast_ok,
        result_start=result_start,
        result_time_reached=result_time_reached,
        runtime=runtime,
        runtime_format=runtime_format,
        result_sync_loss_cause=result_sync_loss_cause,
        result_message=result_message,
        system_stable=system_stable,
    )

    logger.info("Расчет ЭМехПП окончен.\n%s", results)
    return results
