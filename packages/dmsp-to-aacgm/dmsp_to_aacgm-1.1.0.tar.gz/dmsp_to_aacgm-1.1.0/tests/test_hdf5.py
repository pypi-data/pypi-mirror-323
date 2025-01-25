import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List
import unittest
from click.testing import CliRunner
import h5py
from dmsp_to_aacgm.cli import cli
from math import isnan, isclose



class TestHdf5(unittest.TestCase):

    input_dir = "tests/data/inputs"
    output_dir = "tests/data/outputs"
    flux_filename = "dms_19970525_12e.001.hdf5"
    mag_filename = "dms_19970525_12e.001.hdf5"

    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()

    def run_tool(self, args: List[str] = []):
        return self.runner.invoke(cli, args)
    
    def test_hdf5_convert_existing_file(self):
        with TemporaryDirectory() as temp_output_dir:
            input_file = os.path.join(self.input_dir, self.mag_filename)
            expected_output_file = os.path.join(self.output_dir, self.mag_filename)

            new_file_name = os.path.join(temp_output_dir, self.mag_filename)
            self._create_copy(input_file, new_file_name)

            result = self.run_tool([new_file_name])
            assert result.exit_code == 0, f"CLI failed: {result.output}"

            self._compare_hdf5_files(new_file_name, expected_output_file)

    def test_hdf5_mag_conversion(self):
        with TemporaryDirectory() as temp_output_dir:
            input_file = os.path.join(self.input_dir, self.mag_filename)
            expected_output_file = os.path.join(self.output_dir, self.mag_filename)

            result = self.run_tool([input_file, temp_output_dir])
            assert result.exit_code == 0, f"CLI failed: {result.output}"

            output_file_path = os.path.join(temp_output_dir, self.mag_filename)
            assert os.path.exists(output_file_path), "Output file was not created"

            self._compare_hdf5_files(output_file_path, expected_output_file)

    def test_hdf5_mag_csv(self):
        with TemporaryDirectory() as temp_output_dir:
            input_file = os.path.join(self.input_dir, self.mag_filename)
            csv_file_name = Path(self.mag_filename).stem + ".csv"
            expected_output_file = os.path.join(self.output_dir, csv_file_name)

            result = self.run_tool([input_file, temp_output_dir, "-ac"])
            assert result.exit_code == 0, f"CLI failed: {result.output}"

            output_file_path = os.path.join(temp_output_dir, csv_file_name)
            assert os.path.exists(output_file_path), "Output file was not created"

            self._compare_csv_files(output_file_path, expected_output_file)

    def test_hdf5_flux_conversion(self):
        with TemporaryDirectory() as temp_output_dir:
            input_file = os.path.join(self.input_dir, self.flux_filename)
            expected_output_file = os.path.join(self.output_dir, self.flux_filename)

            result = self.run_tool([input_file, temp_output_dir])
            assert result.exit_code == 0, f"CLI failed: {result.output}"

            output_file_path = os.path.join(temp_output_dir, self.flux_filename)
            assert os.path.exists(output_file_path), "Output file was not created"

            self._compare_hdf5_files(output_file_path, expected_output_file)

    def _compare_hdf5_files(self, input_path: str, expected_file_path: str):
        with h5py.File(input_path, "r") as actual, h5py.File(expected_file_path, "r") as expected:
            actual_values = actual["Data"]["Table Layout"][()]
            expected_values = expected["Data"]["Table Layout"][()]
            for a, e, in zip(actual_values, expected_values):
                for a_item, e_item in zip(a, e):
                    if not isnan(a_item) and not isnan(e_item):
                        assert isclose(a_item, e_item, rel_tol=1e-12, abs_tol=1e-12), \
                        f"Values in record do not match. Actual: {a} Expected: {e}"

    def _create_copy(self, file_path: str, output_path: str):
        input_file = h5py.File(file_path, "r")
        output_file = h5py.File(output_path, "w")
        for key in input_file.keys():
            input_file.copy(key, output_file)
        input_file.close()
        output_file.close()

    def _compare_csv_files(self, input_path: str, expected_file_path: str):
        with open(input_path, "r") as actual, open(expected_file_path, "r") as expected:
            for a_line, e_line, in zip(actual.readlines(), expected.readlines()):
                for a_item, e_item in zip(a_line.split(","), e_line.split(",")):
                    a_item = float(a_item)
                    e_item = float(e_item)
                    if not isnan(a_item) and not isnan(e_item):
                        assert isclose(a_item, e_item, rel_tol=1e-12, abs_tol=1e-12), \
                        f"Values in record do not match. Actual: {a_line} Expected: {e_line}"

    