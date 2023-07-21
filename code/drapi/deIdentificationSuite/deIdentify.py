"""
De-identify files

# NOTE Does not expect data in nested directories (e.g., subfolders of "free_text"). Therefore it uses "Path.iterdir" instead of "Path.glob('*/**')".
# NOTE Expects all files to be CSV files. This is because it uses "pd.read_csv".
# TODO Assign portion name to each path (per OS) so that portion files are stored in their respective folders, this prevents file from being overwritten in the unlikely, but possible, case files from different portions have the same name.
"""

import logging
import sys
from pathlib import Path
# Third-party packages
import pandas as pd
# Local packages
from drapi.constants.constants import DATA_TYPES
from drapi.drapi import getTimestamp, successiveParents, make_dir_path, fileName2variableName, map2di, makeMap
from common import IRB_NUMBER, DATA_REQUEST_ROOT_DIRECTORY_DEPTH, COLUMNS_TO_DE_IDENTIFY, VARIABLE_ALIASES, VARIABLE_SUFFIXES, NOTES_PORTION_DIR_MAC, NOTES_PORTION_DIR_WIN, MODIFIED_OMOP_PORTION_DIR_MAC, MODIFIED_OMOP_PORTION_DIR_WIN, OMOP_PORTION_DIR_MAC, OMOP_PORTION_DIR_WIN, NOTES_PORTION_FILE_CRITERIA, OMOP_PORTION_FILE_CRITERIA, BO_PORTION_DIR, BO_PORTION_FILE_CRITERIA, ZIP_CODE_PORTION_DIR, ZIP_CODE_PORTION_FILE_CRITERIA

# Arguments
CONCATENATED_MAPS_DIR_PATH = Path("data/output/concatenateMaps/...")  # TODO

MAPS_DIR_PATH = CONCATENATED_MAPS_DIR_PATH

# Arguments: OMOP data set selection
USE_MODIFIED_OMOP_DATA_SET = True

# Arguments: Portion Paths and conditions
if USE_MODIFIED_OMOP_DATA_SET:
    OMOPPortionDirMac = MODIFIED_OMOP_PORTION_DIR_MAC
    OMOPPortionDirWin = MODIFIED_OMOP_PORTION_DIR_WIN
else:
    OMOPPortionDirMac = OMOP_PORTION_DIR_MAC
    OMOPPortionDirWin = OMOP_PORTION_DIR_WIN

MAC_PATHS = [BO_PORTION_DIR,
             NOTES_PORTION_DIR_MAC,
             OMOPPortionDirMac,
             ZIP_CODE_PORTION_DIR]
WIN_PATHS = [BO_PORTION_DIR,
             NOTES_PORTION_DIR_WIN,
             OMOPPortionDirWin,
             ZIP_CODE_PORTION_DIR]

LIST_OF_PORTION_CONDITIONS = [BO_PORTION_FILE_CRITERIA,
                              NOTES_PORTION_FILE_CRITERIA,
                              OMOP_PORTION_FILE_CRITERIA,
                              ZIP_CODE_PORTION_FILE_CRITERIA]

# Arguments; General
CHUNK_SIZE = 50000

# Arguments: Meta-variables
CONCATENATED_RESULTS_DIRECTORY_DEPTH = DATA_REQUEST_ROOT_DIRECTORY_DEPTH - 1
PROJECT_DIR_DEPTH = CONCATENATED_RESULTS_DIRECTORY_DEPTH  # The concatenation suite of scripts is considered to be the "project".
IRB_DIR_DEPTH = CONCATENATED_RESULTS_DIRECTORY_DEPTH + 2
IDR_DATA_REQUEST_DIR_DEPTH = IRB_DIR_DEPTH + 3

ROOT_DIRECTORY = "DATA_REQUEST_DIRECTORY"  # TODO One of the following:
                                           # ["IDR_DATA_REQUEST_DIRECTORY",      # noqa
                                           #  "IRB_DIRECTORY",                   # noqa
                                           #  "DATA_REQUEST_DIRECTORY",          # noqa
                                           #  "CONCATENATED_RESULTS_DIRECTORY"]  # noqa

LOG_LEVEL = "INFO"

# Variables: Path construction: General
runTimestamp = getTimestamp()
thisFilePath = Path(__file__)
thisFileStem = thisFilePath.stem
projectDir, _ = successiveParents(thisFilePath.absolute(), PROJECT_DIR_DEPTH)
dataRequestDir, _ = successiveParents(thisFilePath.absolute(), DATA_REQUEST_ROOT_DIRECTORY_DEPTH)
IRBDir, _ = successiveParents(thisFilePath.absolute(), IRB_DIR_DEPTH)
IDRDataRequestDir, _ = successiveParents(thisFilePath.absolute(), IDR_DATA_REQUEST_DIR_DEPTH)
dataDir = projectDir.joinpath("data")
if dataDir:
    inputDataDir = dataDir.joinpath("input")
    intermediateDataDir = dataDir.joinpath("intermediate")
    outputDataDir = dataDir.joinpath("output")
    if intermediateDataDir:
        runIntermediateDataDir = intermediateDataDir.joinpath(thisFileStem, runTimestamp)
    if outputDataDir:
        runOutputDir = outputDataDir.joinpath(thisFileStem, runTimestamp)
logsDir = projectDir.joinpath("logs")
if logsDir:
    runLogsDir = logsDir.joinpath(thisFileStem)
sqlDir = projectDir.joinpath("sql")

if ROOT_DIRECTORY == "CONCATENATED_RESULTS_DIRECTORY":
    rootDirectory = projectDir
elif ROOT_DIRECTORY == "DATA_REQUEST_DIRECTORY":
    rootDirectory = dataRequestDir
elif ROOT_DIRECTORY == "IRB_DIRECTORY":
    rootDirectory = IRBDir
elif ROOT_DIRECTORY == "IDR_DATA_REQUEST_DIRECTORY":
    rootDirectory = IDRDataRequestDir

# Variables: Path construction: OS-specific
isAccessible = all([path.exists() for path in MAC_PATHS]) or all([path.exists() for path in WIN_PATHS])
if isAccessible:
    # If you have access to either of the below directories, use this block.
    operatingSystem = sys.platform
    if operatingSystem == "darwin":
        omopPortionDir = OMOP_PORTION_DIR_MAC
        listOfPortionDirs = MAC_PATHS[:]
    elif operatingSystem == "win32":
        omopPortionDir = OMOP_PORTION_DIR_WIN
        listOfPortionDirs = WIN_PATHS[:]
    else:
        raise Exception("Unsupported operating system")
else:
    # If the above option doesn't work, manually copy the database to the `input` directory.
    notesPortionDir = None
    omopPortionDir = None

# Directory creation: General
make_dir_path(runIntermediateDataDir)
make_dir_path(runOutputDir)
make_dir_path(runLogsDir)

if __name__ == "__main__":
    # Logging block
    logpath = runLogsDir.joinpath(f"log {runTimestamp}.log")
    fileHandler = logging.FileHandler(logpath)
    fileHandler.setLevel(LOG_LEVEL)
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(LOG_LEVEL)

    logging.basicConfig(format="[%(asctime)s][%(levelname)s](%(funcName)s): %(message)s",
                        handlers=[fileHandler, streamHandler],
                        level=LOG_LEVEL)

    logging.info(f"""Begin running "{thisFilePath}".""")
    logging.info(f"""All other paths will be reported in debugging relative to `{ROOT_DIRECTORY}`: "{rootDirectory}".""")

    # Load de-identification maps for each variable that needs to be de-identified
    logging.info("""Loading de-identification maps for each variable that needs to be de-identified.""")
    mapsDi = {}
    mapsColumnNames = {}
    variablesCollected = [fileName2variableName(fname) for fname in MAPS_DIR_PATH.iterdir()]
    for varName in variablesCollected:
        if varName in VARIABLE_ALIASES.keys():
            map_ = makeMap(IDset=set(), IDName=varName, startFrom=1, irbNumber=IRB_NUMBER, suffix=VARIABLE_SUFFIXES[varName]["deIdIDSuffix"], columnSuffix=varName, deIdentifiedIDColumnHeaderFormatStyle="lemur")
            mapsColumnNames[varName] = map_.columns[-1]
        else:
            varPath = MAPS_DIR_PATH.joinpath(f"{varName} map.csv")
            map_ = pd.read_csv(varPath)
            mapDi = map2di(map_)
            mapsDi[varName] = mapDi
            mapsColumnNames[varName] = map_.columns[-1]

    # De-identify columns
    logging.info("""De-identifying files.""")
    for directory, fileConditions in zip(listOfPortionDirs, LIST_OF_PORTION_CONDITIONS):
        # Act on directory
        logging.info(f"""Working on directory "{directory.absolute().relative_to(rootDirectory)}".""")
        for file in directory.iterdir():
            logging.info(f"""  Working on file "{file.absolute().relative_to(rootDirectory)}".""")
            conditions = [condition(file) for condition in fileConditions]
            if all(conditions):
                # Set file options
                exportPath = runOutputDir.joinpath(file.name)
                fileMode = "w"
                fileHeaders = True
                # Read file
                logging.info("""    File has met all conditions for processing.""")
                logging.info("""  ..  Reading file to count the number of chunks.""")
                numChunks = sum([1 for _ in pd.read_csv(file, chunksize=CHUNK_SIZE)])
                logging.info(f"""  ..  This file has {numChunks} chunks.""")
                dfChunks = pd.read_csv(file, chunksize=CHUNK_SIZE)
                for it, dfChunk in enumerate(dfChunks, start=1):
                    dfChunk = pd.DataFrame(dfChunk)
                    # Work on chunk
                    logging.info(f"""  ..  Working on chunk {it} of {numChunks}.""")
                    for columnName in dfChunk.columns:
                        # Work on column
                        logging.info(f"""  ..    Working on column "{columnName}".""")
                        if columnName in COLUMNS_TO_DE_IDENTIFY:  # Keep this reference to `COLUMNS_TO_DE_IDENTIFY` as a way to make sure that all variables were collected during `getIDValues` and the `makeMap` scripts.
                            variableDataType = DATA_TYPES[columnName]
                            logging.info(f"""  ..  ..  Column must be de-identified. De-identifying values. Values are being treated as the following data type: "{variableDataType}".""")
                            if columnName in VARIABLE_ALIASES.keys():
                                mapsDiLookUpName = VARIABLE_ALIASES[columnName]
                            else:
                                mapsDiLookUpName = columnName
                            # Look up values in de-identification maps according to data type. NOTE We are relying on pandas assigning the correct data type to the look-up values in the de-identification map.
                            if variableDataType.lower() == "numeric":
                                dfChunk[columnName] = dfChunk[columnName].apply(lambda IDNum: mapsDi[mapsDiLookUpName][IDNum] if not pd.isna(IDNum) else IDNum)
                            elif variableDataType.lower() == "string":
                                dfChunk[columnName] = dfChunk[columnName].apply(lambda IDvalue: mapsDi[mapsDiLookUpName][str(IDvalue)] if not pd.isna(IDvalue) else IDvalue)
                            else:
                                msg = "The table column is expected to have a data type associated with it."
                                logging.error(msg)
                                raise ValueError(msg)
                            dfChunk = dfChunk.rename(columns={columnName: mapsColumnNames[columnName]})
                    # Save chunk
                    dfChunk.to_csv(exportPath, mode=fileMode, header=fileHeaders, index=False)
                    fileMode = "a"
                    fileHeaders = False
                    logging.info(f"""  ..  Chunk saved to "{exportPath.absolute().relative_to(rootDirectory)}".""")
            else:
                logging.info("""    This file does not need to be processed.""")

    # Output location summary
    logging.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logging.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
