"""
Stuff for OMOP
"""

import os
import sys
import yaml
from pathlib import Path


def interpretPath(pathAsString: str) -> str:
    """
    Makes sure path separators are appropriate for the current operating system.
    """
    operatingSystem = sys.platform
    if operatingSystem == "darwin":
        newPathAsString = pathAsString.replace("\\", "/")
    elif operatingSystem == "win32":
        newPathAsString = pathAsString.replace("/", "\\")
    else:
        raise Exception("Unsupported operating system")
    return newPathAsString


def editConfig(inputPath: Path, outputPath: Path, timestamp):
    """
    Edits a YAML config file so that the output paths end with a timestamp
    """
    with open(inputPath) as file:
        configFile = yaml.safe_load(file)

    # Get paths as strings
    identified_file_location_str = configFile["data_output"]["identified_file_location"]
    deidentified_file_location_str = configFile["data_output"]["deidentified_file_location"]
    mapping_location_str = configFile["data_output"]["mapping_location"]
    print(identified_file_location_str)
    print(deidentified_file_location_str)
    print(mapping_location_str)

    # Make sure path separators are OS-appropriate
    identified_file_location_str2 = interpretPath(identified_file_location_str)
    deidentified_file_location_str2 = interpretPath(deidentified_file_location_str)
    mapping_location_str2 = interpretPath(mapping_location_str)
    print(identified_file_location_str2)
    print(deidentified_file_location_str2)
    print(mapping_location_str2)

    # Add timestamp to path as subfolder
    identified_file_location = Path(identified_file_location_str2).joinpath(timestamp)
    deidentified_file_location = Path(deidentified_file_location_str2).joinpath(timestamp)
    mapping_location = Path(mapping_location_str2).joinpath(timestamp)
    print(identified_file_location)
    print(deidentified_file_location)
    print(mapping_location)

    sep = os.sep

    configFile["data_output"]["identified_file_location"] = identified_file_location.__str__() + sep
    configFile["data_output"]["deidentified_file_location"] = deidentified_file_location.__str__() + sep
    configFile["data_output"]["mapping_location"] = mapping_location.__str__() + sep

    with open(outputPath, "w") as file:
        yaml.dump(configFile, file)
