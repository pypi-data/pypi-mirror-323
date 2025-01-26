import random

from pychemstation.utils.method_types import *
from pychemstation.utils.sequence_types import *

DEFAULT_METHOD = "GENERAL-POROSHELL-OPT"
DEFAULT_SEQUENCE = "LLETest"

# CONSTANTS: paths only work in Hein group HPLC machine in room 242
DEFAULT_COMMAND_PATH = "C:\\Users\\User\\Desktop\\Lucy\\"
DEFAULT_METHOD_DIR = "C:\\ChemStation\\1\\Methods\\"
DATA_DIR = "C:\\Users\\Public\\Documents\\ChemStation\\3\\Data"
SEQUENCE_DIR = "C:\\USERS\\PUBLIC\\DOCUMENTS\\CHEMSTATION\\3\\Sequence"

HEIN_LAB_CONSTANTS = [DEFAULT_COMMAND_PATH,
                      DEFAULT_METHOD_DIR,
                      DATA_DIR,
                      SEQUENCE_DIR]

# these CONSTANTS work in rm 254
DEFAULT_COMMAND_PATH_254 = "D:\\\git_repositories\\\hplc_comm\\"
DEFAULT_METHOD_DIR_254 = "D:\\Chemstation\\1\\Methods\\"
DATA_DIR_254 = "D:\\Chemstation\\1\\Data\\2024-12\\"
SEQUENCE_DIR_254 = "C:\\1\\Sequence\\"

HEIN_LAB_CONSTANTS_254 = [DEFAULT_COMMAND_PATH_254,
                          DEFAULT_METHOD_DIR_254,
                          DATA_DIR_254,
                          SEQUENCE_DIR_254]


def room(num: int):
    if num == 242:
        return HEIN_LAB_CONSTANTS
    elif num == 254:
        return HEIN_LAB_CONSTANTS_254


def gen_rand_method():
    org_modifier = int(random.random() * 10)
    max_run_time = int(random.random() * 10)
    return MethodTimetable(
        first_row=HPLCMethodParams(
            organic_modifier=org_modifier,
            flow=round(random.random(), 2),
            maximum_run_time=max_run_time),
        subsequent_rows=[
            TimeTableEntry(
                start_time=0.10,
                organic_modifer=org_modifier,
                flow=0.34),
            TimeTableEntry(
                start_time=1,
                organic_modifer=100 - int(random.random() * 10),
                flow=0.55)])


seq_entry = SequenceEntry(
    vial_location=TenColumn.ONE,
    method=DEFAULT_METHOD,
    num_inj=int(random.random() * 10),
    inj_vol=int(random.random() * 10),
    sample_name="Test",
    sample_type=SampleType(int(random.random() * 3)),
)
