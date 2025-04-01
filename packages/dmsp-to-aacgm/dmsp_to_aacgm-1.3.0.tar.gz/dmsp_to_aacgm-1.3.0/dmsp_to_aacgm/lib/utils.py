from typing import List
import os


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