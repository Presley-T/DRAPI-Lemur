"""
Makes de-identification maps, building on existing maps.

# NOTE Does not expect data in nested directories (e.g., subfolders of "free_text"). Therefore it uses "Path.iterdir" instead of "Path.glob('*/**')".
# NOTE Expects all files to be CSV files. This is because it uses "pd.read_csv".
"""

import logging
import re
from pathlib import Path
# Third-party packages
import pandas as pd
# Local packages
from drapi.drapi import getPercentDifference


def main(NEW_MAPS_DIR_PATH, OLD_MAPS_DIR_PATH, thisFilePath, ROOT_DIRECTORY, rootDirectory, runOutputDir):
    """
    """

    logging.info(f"""Begin running "{thisFilePath}".""")
    logging.info(f"""All other paths will be reported in debugging relative to `{ROOT_DIRECTORY}`: "{rootDirectory}".""")

    # Map new maps to variable names
    logging.info("""Mapping new maps to variable names.""")
    pattern = r"^([a-zA-Z_0-9\(\) ]+) map"
    newMapsFileDict = {}
    for fpath in NEW_MAPS_DIR_PATH.iterdir():
        fname = fpath.stem
        obj = re.match(pattern, fname)
        if obj:
            variableName = obj.groups()[0]
        else:
            raise
        newMapsFileDict[variableName] = [fpath]

    # Match old and new maps by variable name
    logging.info("""Matching old and new maps by variable name.""")
    variableNameSet = set()
    variableNameSet.update(OLD_MAPS_DIR_PATH.keys())
    variableNameSet.update(newMapsFileDict.keys())
    matchedMaps = {variableName: [] for variableName in sorted(list(variableNameSet))}
    for variableName, li in OLD_MAPS_DIR_PATH.items():
        matchedMaps[variableName].extend(li)
    for variableName, li in newMapsFileDict.items():
        matchedMaps[variableName].extend(li)

    # Load, concatenate, and save maps by variable names
    logging.info("""Loading, concatenating, and saving maps by variable names.""")
    concatenatedMapsDict = {}
    for variableName, li in matchedMaps.items():
        logging.info(f"""  Working on variable "{variableName}".""")
        concatenatedMap = pd.DataFrame()
        for fpath in li:
            fpath = Path(fpath)
            logging.info(f"""    Working on map located at "{fpath.absolute().relative_to(rootDirectory)}".""")
            df = pd.read_csv(fpath)
            columns = df.columns[:-1].to_list()
            columns = columns + [f"deid_{variableName}_id"]  # NOTE: Hack. Conform de-identified column name to this format.
            df.columns = columns
            concatenatedMap = pd.concat([concatenatedMap, df])
        concatenatedMapsDict[variableName] = concatenatedMap
        fpath = runOutputDir.joinpath(f"{variableName} map.csv")
        concatenatedMap.to_csv(fpath, index=False)

    # Quality control
    results = {}
    for variableName, df in concatenatedMapsDict.items():
        uniqueIDs = len(df.iloc[:, 0].unique())
        numIDs = len(df)
        percentDifference = getPercentDifference(uniqueIDs, numIDs)
        results[variableName] = {"Unique IDs": uniqueIDs,
                                 "Total IDs": numIDs,
                                 "Percent Similarity": percentDifference}
    resultsdf = pd.DataFrame.from_dict(results, orient="index")
    logging.debug(f"Concatenation summary:\n{resultsdf.to_string()}")

    # Clean up
    # TODO If input directory is empty, delete
    # TODO Delete intermediate run directory

    # Output location summary
    logging.info(f"""Script output is located in the following directory: "{runOutputDir.absolute().relative_to(rootDirectory)}".""")

    # End script
    logging.info(f"""Finished running "{thisFilePath.absolute().relative_to(rootDirectory)}".""")
