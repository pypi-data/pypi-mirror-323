# Python stdlib imports
from dataclasses import dataclass
from os.path import expanduser
from pathlib import Path


DIR_RASTR_WIN = Path(expanduser("~/Documents/RastrWin3"))
DIR_RASTR_WIN_SHABLON = Path(expanduser("~/Documents/RastrWin3/SHABLON"))
DIR_RASTR_WIN_TEST_9 = DIR_RASTR_WIN / Path("test-rastr/RUSTab/test9.rst")
DIR_RASTR_WIN_MDP = DIR_RASTR_WIN / Path("test-rastr/MDP/cx195_10_11.os")


def get_filename_shablon(name_template: str = "") -> Path:
    """
    Формирует полный путь к Шаблону.
    :param name_template: название шаблона (пример: 'режим'). По умолчанию None.
    :return: Path(.../Documents/RastrWin3/SHABLON/poisk.os)
    """
    if name_template and name_template != "":
        try:
            if name_template == "без шаблона":
                return Path(
                    TemplateFileNames.dict_russian_names_shabl[name_template]
                ).name
            else:
                return Path(DIR_RASTR_WIN_SHABLON) / Path(
                    TemplateFileNames.dict_russian_names_shabl[name_template]
                )
        except KeyError:
            return Path(name_template).name
    elif name_template == "":
        return Path(name_template).name


def extension_shablon(extension_template: str) -> Path:
    """
    Формирует полный путь к Шаблону по расширению шаблона.
    :param extension_template: Path('.rg2') расширение шаблона.
    :return: Path() полный путь к файлу шаблона.
    """
    if extension_template and extension_template != "":
        try:
            if extension_template == "":
                return Path(TemplateFileNames.dict_russian_names_shabl["без шаблона"])
            else:
                return Path(DIR_RASTR_WIN_SHABLON) / Path(
                    TemplateFileNames.dict_extension_shabl[extension_template]
                )
        except KeyError:
            return Path("")


@dataclass(frozen=True, slots=True)
class TemplateFileNames:
    """Все названия файлов шаблонов с расширениями"""

    without_template: str = ""
    transformers_trn: str = "трансформаторы.trn"
    weighting_trajectory_ut2: str = "траектория утяжеления.ut2"
    dot_pnt: str = "точка.pnt"
    lookup_table_ms: str = "таблица соответвия.ms"
    script_scn: str = "сценарий.scn"
    compared_data_sv: str = "сравниваемые данные.sv"
    sections_sch: str = "сечения.sch"
    regime_rg2: str = "режим.rg2"
    substation_mk4: str = "подстанции.mk4"
    optimization_p_opf: str = "оптимизация p.opf"
    merge_schemas_sxm: str = "объединение схем.sxm"
    equipment_brd: str = "оборудование.brd"
    modifications_AIP_gmm: str = "модификации АИП.gmm"
    megadot_smzu_mpt: str = "мегаточка_смзу.mpt"
    megadot_mpt: str = "мегаточка.mpt"
    jacobi_matrix_mc: str = "матрица якоби.mc"
    paw_old_lpn: str = "лапну_old.lpn"
    paw_lpn: str = "лапну.lpn"
    check_value_kpr: str = "контр-е величины.kpr"
    single_schema_pnt: str = "единая схема.pnt"
    dynamic_rst: str = "динамика.rst"
    graphics_areas_gra: str = "графика-районы.gra"
    graphics_grf: str = "графика.grf"
    generators_rstgen: str = "генераторы.rstgen"
    vrdo_vrd: str = "врдо.vrd"
    option_vrn: str = "вариант-е р-ты.vrn"
    base_mode_mt_rg2: str = "базовый режим мт.rg2"
    antsapf_anc: str = "анцапфы.anc"
    update_sp: str = "актуализация.sp"
    automation_dfw: str = "автоматика.dfw"
    automation_amt: str = "автоматика.amt"
    poisk_os: str = "poisk.os"

    dict_russian_names_shabl = {
        "без шаблона": without_template,
        "трансформаторы": transformers_trn,
        "траектория утяжеления": weighting_trajectory_ut2,
        "точка": dot_pnt,
        "таблица соответвия": lookup_table_ms,
        "сценарий": script_scn,
        "сравниваемые данные": compared_data_sv,
        "сечения": sections_sch,
        "режим": regime_rg2,
        "подстанции": substation_mk4,
        "оптимизация p": optimization_p_opf,
        "объединение схем": merge_schemas_sxm,
        "оборудование": equipment_brd,
        "модификации АИП": modifications_AIP_gmm,
        "мегаточка_смзу": megadot_smzu_mpt,
        "мегаточка": megadot_mpt,
        "матрица якоби": jacobi_matrix_mc,
        "лапну_old": paw_old_lpn,
        "лапну": paw_lpn,
        "контр-е величины": check_value_kpr,
        "единая схема": single_schema_pnt,
        "динамика": dynamic_rst,
        "графика-районы": graphics_areas_gra,
        "графика": graphics_grf,
        "генераторы": generators_rstgen,
        "врдо": vrdo_vrd,
        "вариант-е р-ты": option_vrn,
        "базовый режим мт": base_mode_mt_rg2,
        "анцапфы": antsapf_anc,
        "актуализация": update_sp,
        "автоматика": automation_dfw,
        "автоматика.amt": automation_amt,
        "poisk.os": poisk_os,
    }

    dict_extension_shabl = {
        ".trn": transformers_trn,
        ".ut2": weighting_trajectory_ut2,
        ".pnt": dot_pnt,
        ".ms": lookup_table_ms,
        ".scn": script_scn,
        ".sv": compared_data_sv,
        ".sch": sections_sch,
        ".rg2": regime_rg2,
        ".mk4": substation_mk4,
        ".opf": optimization_p_opf,
        ".sxm": merge_schemas_sxm,
        ".brd": equipment_brd,
        ".gmm": modifications_AIP_gmm,
        ".mpt": megadot_mpt,
        ".mc": jacobi_matrix_mc,
        ".lpn": paw_lpn,
        ".kpr": check_value_kpr,
        ".rst": dynamic_rst,
        ".gra": graphics_areas_gra,
        ".grf": graphics_grf,
        ".rstgen": generators_rstgen,
        ".vrd": vrdo_vrd,
        ".vrn": option_vrn,
        ".anc": antsapf_anc,
        ".sp": update_sp,
        ".dfw": automation_dfw,
        ".amt": automation_amt,
        ".os": poisk_os,
    }
