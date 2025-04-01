from typing import List
import h5py
from ...dataset_model import DataSet
from .datasets.mag import MagHdf5
from .datasets.flux import FluxHdf5


def hdf5_dataset_factory(file_path: str) -> DataSet:
    hdf5_file = h5py.File(file_path, "r+")
    data_sets: List[DataSet] = [MagHdf5, FluxHdf5]
    for data_set in data_sets:
        if data_set.match(hdf5_file):
            return data_set(hdf5_file)
        
    raise Exception("Unknown hdf5 dataset")