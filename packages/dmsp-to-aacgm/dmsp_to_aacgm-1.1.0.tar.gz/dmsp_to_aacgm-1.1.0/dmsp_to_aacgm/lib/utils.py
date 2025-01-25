from typing import List, Optional
import os
from .dataset_model import DataSet


def get_files(path: str) -> List[str]:
    """
    Takes a file path or directory path and returns a list of files.
    If the path refers to a file, returns a list with that file.
    If the path refers to a directory, returns a list of files within that directory (non-recursive).

    Args:
        path (str): The file or directory path.

    Returns:
        List[str]: A list of file paths.
    """
    if os.path.isfile(path):
        return [path]
    elif os.path.isdir(path):
        return [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    return []


def build_output_path(file_path: str, output_dir: str) -> str:
    """
    Constructs a new file path using the specified output directory and the filename of the original file path.

    Args:
        file_path (str): The original file path.
        output_dir (str): The directory where the new file path should reside.

    Returns:
        str: The new file path in the output directory.
    """
    filename = os.path.basename(file_path)
    return os.path.join(output_dir, filename)


def build_csv(
        data_set: DataSet,
        file_name: str,
        output_dir: str = "",
    ):
    """
    Creates a csv file containing time data and AACGM coordinates.

    Args:
        data_set (DataSet): The data set to use.
        file_name (str): The csv file name.
        output_dir (str): The output directory od the csv file.
    """
    csv_lines = []
    for timestamp, mlat, mlon, mlt in data_set.get_aacgm_data():
        csv_lines.append(
            ",".join([
                str(item) for item in [
                    timestamp.year, timestamp.month, timestamp.day,
                    timestamp.hour, timestamp.minute, timestamp.second,
                    mlat, mlon, mlt
                ]
            ])
        )
    csv_data = "\n".join(csv_lines)
    output_path = os.path.join(output_dir, file_name+".csv")
    with open(output_path, "w") as file:
        file.write(csv_data)



    