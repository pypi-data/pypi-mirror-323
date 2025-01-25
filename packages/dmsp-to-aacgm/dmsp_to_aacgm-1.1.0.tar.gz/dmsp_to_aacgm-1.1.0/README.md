# Overview

A tool for converting geomagnetic coordinates in DMSP data files to AACGM coordinates. The [aacgmv2 Python library](https://github.com/aburrell/aacgmv2) is leveraged for the conversion.


# Supported Files
The tool currently supports conversions of the following data files:

| **Source**                     | **File Type** | **Contents**                                | **Example**                   |
|--------------------------------|---------------|--------------------------------------------|--------------------------------|
| [Cedar Madrigal Database](http://cedar.openmadrigal.org)        | HDF5          | 1-second resolution for Ion Drift, Magnetometer, and Electron Density | `dms_20150410_16s1.001.hdf5`  |
| [Cedar Madrigal Database](http://cedar.openmadrigal.org)        | HDF5          | Flux/Energy values                         | `dms_20150410_16e.001.hdf5`   |

To add support for additional files, please reach out to offillcarson@gmail.com, or submit a pull request.

## Installation

```pip install dmsp-to-aacgm```

## Command-line Usage

```dmsp-to-aacgm <input file/directory> [<output directory>]```

If the output directory is not specified, or the output directory is the same as the input directory, the input files will be modified.

### Examples

| **Command**                                        | **Description**                                      |
|---------------------------------------------------|------------------------------------------------------|
| `dmsp-to-aacgm dms_20150410_16s1.001.hdf5`        | Convert a single file                                |
| `dmsp-to-aacgm dms_20150410_16s1.001.hdf5 aacgm_conversions` | Convert a single file, output to `aacgm_conversions` |
| `dmsp-to-aacgm dmsp_data`                         | Convert all files in `dmsp_data`                     |
| `dmsp-to-aacgm dmsp_data aacgm_conversions`       | Convert all files in `dmsp_data`, output to `aacgm_conversions` |
| `dmsp-to-aacgm dms_20150410_16s1.001.hdf5 aacgm_conversions --aacgm-csv` | Create a csv file containing time and aacgm data, output to `aacgm_conversions` |

## Usage in Python

```python
from dmsp_to_aacgm import get_dataset, build_csv

# Convert a file
data_set = get_dataset("dms_20150410_16s1.001.hdf5")
data_set.convert()
data_set.close()

# Create a converted file in "aacgm_conversions"
data_set = get_dataset("dms_20150410_16s1.001.hdf5", "aacgm_conversions/dms_20150410_16s1.001.hdf5")
data_set.convert()
data_set.close()

# Create a minimal aacgm csv file in the current directory
data_set = get_dataset("dms_20150410_16s1.001.hdf5")
build_csv(data_set, file_name="aacgm_csv_file")
data_set.close()
```

## Acknowledgements

The software was written by Carson O'Ffill and the project was guided by Simon Wing. We also acknowledge the following grants:

**NASA Grants**:
- 80NSSC20K0704
- 80NSSC22K0515
- 80NSSC23K0899
- 80NSSC23K0904

**NSF CEDAR Grants**:
- 2431665

This software is distributed for free under an MIT license. If you find it useful, please acknowledge our work in your publications or projects.

## Contact Info

Simon Wing: simon.wing@jhuapl.edu

Carson O'Ffill: offillcarson@gmail.com