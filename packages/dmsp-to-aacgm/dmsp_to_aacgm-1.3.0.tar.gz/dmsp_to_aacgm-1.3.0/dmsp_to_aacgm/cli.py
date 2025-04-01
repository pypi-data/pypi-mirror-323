import os
from pathlib import Path
import click
from .lib.filetypes.factory import dataset_factory
from .lib.utils import get_files



@click.command(
    name="dmsp-to-aacgm",
    help="Converts geomagnetic coordinates in DMSP data files to AACGM coordinates.\n\n"
         "input_path: Path of a dmsp file or directory containing dmsp files for conversion.\n\n"
         "output_dir: Optional directory to save converted files. If not supplied, the input files will be modified."
)
@click.argument(
    "input_path",
    type=click.Path(exists=True),
    metavar="<input path>"
)
@click.argument(
    "output_dir",
    type=click.Path(file_okay=False),
    required=False,
    metavar="<output dir>"
)
@click.option(
    "-r", "--reduced",
    is_flag=True,
    help="Create a h5 file with time and AACGM coordinates only"
)
def cli(input_path, output_dir, reduced):
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    for file_path in get_files(input_path):
        print(f"Converting {file_path}...")
        try:
            data_set = dataset_factory(file_path)

            if reduced:
                file_name = Path(file_path).stem + "_aacgm.hdf5"
                output_path = os.path.join(output_dir or "", file_name)
                data_set.convert(output_path, minimal=True)
            else:
                output_path = None
                if output_dir:
                    output_path = os.path.join(
                        output_dir, os.path.basename(file_path)
                    )
                data_set.convert(output_path)

            data_set.close()
            print("Conversion complete!")
        except Exception as e:
            print(f"Could not process {file_path} due to: {str(e)}")