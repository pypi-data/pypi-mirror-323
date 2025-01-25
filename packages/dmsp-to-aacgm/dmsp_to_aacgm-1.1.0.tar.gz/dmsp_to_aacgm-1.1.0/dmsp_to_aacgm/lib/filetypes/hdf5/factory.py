from typing import List, Optional
from .utils import read_hdf5_file
from ...dataset_model import DataSet
from .datasets.mag import MagHdf5
from .datasets.flux import FluxHdf5


def hdf5_dataset_factory(file_path: str, output_path: Optional[str] = None) -> DataSet:
    hdf5_file = read_hdf5_file(file_path, output_path)
    data_sets: List[DataSet] = [MagHdf5, FluxHdf5]
    for data_set in data_sets:
        if data_set.match(hdf5_file):
            return data_set(hdf5_file)
        
    raise Exception("Unknown hdf5 dataset")