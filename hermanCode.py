"""
Herman's utility functions commonly used in his projects
"""

import logging
import os
import pandas as pd
import re
import sqlalchemy as sa
import sys
from itertools import islice
from pathlib import Path
from typing import Union

logger = logging.getLogger(__name__)

# SQL Server settings
SERVER = "DWSRSRCH01.shands.ufl.edu"  # AKA `HOST`
DATABASE = "DWS_PROD"
USERDOMAIN = "UFAD"
USERNAME = os.environ["USER"]
UID = fr"{USERDOMAIN}\{USERNAME}"
PWD = os.environ["HFA_UFADPWD"]

connstr = f"mssql+pymssql://{UID}:{PWD}@{SERVER}/{DATABASE}"  # Create connection string
engine = sa.create_engine(connstr)  # Make connection/engine


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    h/t to https://stackoverflow.com/a/39215961/5478086
    """

    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())

    def flush(self):
        pass


class LoggerWriter:
    """
    h/t to https://stackoverflow.com/a/31688396/5478086
    """

    def __init__(self, level):
        self.level = level

    def write(self, message):
        if message != '\n':
            self.level(message)

    def flush(self):
        self.level(sys.stderr)


def make_dir_path(directory_path: str) -> None:
    """
    Check if all directories exists in a path. If not, create them
    """
    path_obj = Path(directory_path)
    paths = list(path_obj.parents)[::-1] + [path_obj]
    for dir in paths:
        if not os.path.exists(dir):
            os.mkdir(dir)


def loglevel2int(loglevel: Union[int, str]) -> int:
    """
    An agnostic converter that takes int or str and returns int. If input is int, output is the same as input"""
    dummy = logging.getLogger("dummy")
    dummy.setLevel(loglevel)
    loglevel = dummy.level
    return loglevel


def replace_sql_query(query: str, old: str, new: str, loglevel: Union[int, str] = "INFO") -> str:
    """
    Replaces text in a SQL query only if it's not commented out. I.e., this function applies string.replace() only if the string doesn't begin with "--".
    """
    loglevel_asnumber = loglevel2int(loglevel)
    logger.setLevel(loglevel_asnumber + 10)

    pattern = r"^\w*--"
    li = query.split("\n")
    result = []
    logger.debug("Starting")
    for line in li:
        logger.debug(f"""  Working on "{line}".""")
        obj = re.search(pattern, line)
        if obj:
            logger.debug("    Passing")
            nline = line
        else:
            nline = line.replace(old, new)
            logger.debug(f"""    Replacing text in "{line}" --> "{nline}".""")
        logger.debug("  Appending...")
        result.append(nline)
    logger.debug("Finished")
    return "\n".join(result)


def patientKey_from_personID(personID, map_={}):
    """
    Assumes "map_" is a dictionary with person IDs as integers that map patient keys as integers.
    """
    if personID in map_.keys():
        patientKey = map_[personID]
        source = 0
    else:
        query = f"""use DWS_OMOP_PROD
        SELECT 
            xref.PERSON_MAPPING.person_id as person_id,
            xref.PERSON_MAPPING.patient_key as patient_key
        FROM
            xref.PERSON_MAPPING
        WHERE
            xref.PERSON_MAPPING.person_id IN ({personID})"""
        results = pd.read_sql(query, engine)
        personID = results["person_id"][0]
        patientKey = results["patient_key"][0]
        source = 1
    return patientKey, source



def float2str(value, navalue=""):
    """
    Converts values to string-type. If a value is NaN it is replaced with a value that can be converted to a string, default empty string, "".
    """
    assert isinstance(navalue, str), """"navalue" is not a string type."""
    if pd.isna(value):
        newValue = str(navalue)
    else:
        newValue = str(int(value))
    return newValue


def str2int(value, navalue=-1):
    """
    Converts values to integer-type. If a value is NaN it is replaced with a value that can be converted to an integer, default is "-1".
    """
    assert isinstance(navalue, int), """"navalue" is not an integer type."""
    if pd.isna(value):
        newValue = int(navalue)
    else:
        newValue = int(float(value))
    return newValue


def str2bool(value, navalue=""):
    """
    Converts values to boolean-type. If a value is missing it is replaced with an empty string.
    """
    if pd.isna(value):
        newValue = int(navalue)
    else:
        newValue = bool(value)
    return newValue
    

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# >>> tree function >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# h/t https://stackoverflow.com/a/59109706/5478086

# prefix components:
space = '    '
branch = '│   '
# pointers:
tee = '├── '
last = '└── '


def tree(dir_path: Path, level: int = -1, limit_to_directories: bool = False,
         length_limit: int = 1000):
    """Given a directory Path object print a visual tree structure"""
    dir_path = Path(dir_path)  # accept string coerceable to Path
    files = 0
    directories = 0

    def inner(dir_path: Path, prefix: str = '', level=-1):
        nonlocal files, directories
        if not level:
            return  # 0, stop iterating
        if limit_to_directories:
            contents = [d for d in dir_path.iterdir() if d.is_dir()]
        else:
            contents = list(dir_path.iterdir())
        pointers = [tee] * (len(contents) - 1) + [last]
        for pointer, path in zip(pointers, contents):
            if path.is_dir():
                yield prefix + pointer + path.name
                directories += 1
                extension = branch if pointer == tee else space
                yield from inner(path, prefix=prefix + extension, level=level - 1)
            elif not limit_to_directories:
                yield prefix + pointer + path.name
                files += 1
    print(dir_path.name)
    iterator = inner(dir_path, level=level)
    for line in islice(iterator, length_limit):
        print(line)
    if next(iterator, None):
        print(f'... length_limit, {length_limit}, reached, counted:')
    print(f'\n{directories} directories' + (f', {files} files' if files else ''))


# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
