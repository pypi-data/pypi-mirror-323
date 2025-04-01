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

    input_dir = "tests/data/inputs/"
    output_dir = "tests/data/outputs/"

    test_data = [
        ("mag", input_dir+"dms_20150410_16s1.001.hdf5", output_dir+"dms_20150410_16s1.001.hdf5"),
        ("flux", input_dir+"dms_19970525_12e.001.hdf5", output_dir+"dms_19970525_12e.001.hdf5")
    ]

    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()

    def run_tool(self, args: List[str] = []):
        return self.runner.invoke(cli, args)
    
    def test_hdf5_convert_existing_file(self):
        for test_name, input_file_path, expected_output_file_path in self.test_data:
            with self.subTest(test_name=test_name):
                with TemporaryDirectory() as temp_output_dir:
                    new_file_path = os.path.join(temp_output_dir, os.path.basename(input_file_path))
                    self._create_copy(input_file_path, new_file_path)

                    result = self.run_tool([new_file_path])
                    assert result.exit_code == 0, f"CLI failed: {result.output}"

                    self._compare_hdf5_files(new_file_path, expected_output_file_path, "Data", "Table Layout")

    def test_hdf5_converted_copy(self):
        for test_name, input_file_path, expected_output_file_path in self.test_data:
            with self.subTest(test_name=test_name):
                with TemporaryDirectory() as temp_output_dir:
                    result = self.run_tool([input_file_path, temp_output_dir])
                    assert result.exit_code == 0, f"CLI failed: {result.output}"

                    actual_output_file_path = os.path.join(temp_output_dir, os.path.basename(input_file_path))
                    assert os.path.exists(actual_output_file_path), "Output file was not created"

                    self._compare_hdf5_files(actual_output_file_path, expected_output_file_path, "Data", "Table Layout")

    def test_hdf5_minimal_h5(self):
        for test_name, input_file_path, _ in self.test_data:
            with self.subTest(test_name=test_name):
                with TemporaryDirectory() as temp_output_dir:
                    output_file_name = Path(input_file_path).stem + "_aacgm.hdf5"
                    expected_output_file_path = os.path.join(self.output_dir, output_file_name)

                    result = self.run_tool([input_file_path, temp_output_dir, "-r"])
                    assert result.exit_code == 0, f"CLI failed: {result.output}"

                    actual_output_file_path = os.path.join(temp_output_dir, output_file_name)
                    assert os.path.exists(actual_output_file_path), "Output file was not created"
                    
                    self._compare_hdf5_files(actual_output_file_path, expected_output_file_path, "/", "Data")

    def _compare_hdf5_files(self, input_path: str, expected_file_path: str, group: str, data_set: str):
        with h5py.File(input_path, "r") as actual, h5py.File(expected_file_path, "r") as expected:
            actual_values = actual[group][data_set][()]
            expected_values = expected[group][data_set][()]
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

    