from dataclasses import dataclass
from enum import Enum
from typing import Union, Any, Optional

from .table_types import RegisterFlag
from ..generated import Signal, SolventElement


class PType(Enum):
    STR = "str"
    NUM = "num"


@dataclass
class Param:
    ptype: PType
    val: Union[float, int, str, Any]
    chemstation_key: Union[RegisterFlag, list[RegisterFlag]]


@dataclass
class HPLCMethodParams:
    organic_modifier: int
    flow: float
    maximum_run_time: int


@dataclass
class TimeTableEntry:
    start_time: float
    organic_modifer: float
    flow: Optional[float] = None


@dataclass
class MethodTimetable:
    first_row: HPLCMethodParams
    subsequent_rows: list[TimeTableEntry]
    dad_wavelengthes: Optional[list[Signal]] = None
    organic_modifier: Optional[SolventElement] = None
    modifier_a: Optional[SolventElement] = None
