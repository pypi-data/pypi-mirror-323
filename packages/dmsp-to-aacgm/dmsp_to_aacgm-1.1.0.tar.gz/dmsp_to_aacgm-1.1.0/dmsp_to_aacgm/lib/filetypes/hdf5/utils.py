from typing import Optional
import h5py


def read_hdf5_file(file_path: str, output_path: Optional[str] = None) -> h5py.File:
    output_path = output_path or file_path
    
    if file_path != output_path:
        input_file = h5py.File(file_path, "r")
        file_contents = h5py.File(output_path, "w")
        for key in input_file.keys():
            input_file.copy(key, file_contents)
        input_file.close()
    else:
        file_contents = h5py.File(file_path, "r+")

    return file_contents