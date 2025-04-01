from abc import ABC, abstractmethod
from datetime import datetime
import os
from typing import Any, Iterator, Optional, Tuple
import h5py
import numpy as np



class DataSet(ABC):

    @abstractmethod
    def match(data: Any) -> bool: ...

    @abstractmethod
    def get_aacgm_data(self) -> Iterator[Tuple[datetime, float, float, float]]: ...

    @abstractmethod
    def close(self): ...

    @abstractmethod
    def _full_conversion(self, output_path: Optional[str] = None): ...

    def convert(self, output_path: Optional[str] = None, minimal: bool = False):
        if minimal:
            if not output_path:
                raise Exception("Must specify output_path when generating a minimal h5 file.")
            self._minimal_h5_file(output_path)
        else:
            self._full_conversion(output_path)

    def _minimal_h5_file(self, output_path: str):
        """
        Creates an h5 file containing time data and AACGM coordinates.

        Args:
            output_path (str): The output path of the h5 file.
        """
        dtype = np.dtype([
            ('year', 'u2'), ('month', 'u1'), ('day', 'u1'),
            ('hour', 'u1'), ('min', 'u1'), ('sec', 'u1'),
            ('mlat', 'f8'), ('mlon', 'f8'), ('mlt', 'f8')
        ])
        
        data = []
        for timestamp, mlat, mlon, mlt in self.get_aacgm_data():
            data.append((
                timestamp.year, timestamp.month, timestamp.day,
                timestamp.hour, timestamp.minute, timestamp.second,
                mlat, mlon, mlt
            ))
        
        data = np.array(data, dtype=dtype)
        with h5py.File(output_path, "w") as h5f:
            h5f.create_dataset("/Data", data=data)