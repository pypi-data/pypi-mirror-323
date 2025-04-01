import h5py


def copy_hdf5_file(h5_file: h5py.File, output_path: str) -> h5py.File:
    file_contents = h5py.File(output_path, "w")
    for key in h5_file.keys():
        h5_file.copy(key, file_contents)
    return file_contents