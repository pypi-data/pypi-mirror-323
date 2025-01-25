from typing import Iterator, Tuple
from ....dataset_model import DataSet
import h5py
import aacgmv2
from datetime import datetime


class FluxHdf5(DataSet):

    def __init__(self, hdf5_file: h5py.File):
        self.hdf5_file = hdf5_file
        self.data = hdf5_file["Data"]["Table Layout"][()]

    @staticmethod
    def match(hdf5_file: h5py.File) -> bool:
        if data := hdf5_file.get("Data", {}).get("Table Layout"):
            fields = data.dtype.descr
            expected_fields = ["year", "month", "day", "hour", "min",
                                "sec", "recno", "kindat", "kinst", "ut1_unix",
                                "ut2_unix", "gdlat", "glon", "gdalt", "sat_id",
                                "mlt", "mlat", "mlong", "el_i_flux", "ion_i_flux",
                                "el_i_ener", "ion_i_ener", "el_m_ener", "ion_m_ener",
                                "ch_energy", "ch_ctrl_ener", "el_d_flux", "ion_d_flux",
                                "el_d_ener", "ion_d_ener"]
            for field, expected_field in zip(fields, expected_fields):
                if field[0] != expected_field:
                    return False
            return True
        return False
    
    def get_aacgm_data(self) -> Iterator[Tuple[datetime, float, float, float]]:
        previous_date = None
        for record in self.hdf5_file["Data"]["Table Layout"][()]:
            record = list(record)
            year, month, day, hour, minute, second = record[:6]
            gdlat, glon, gdalt = record[11:14]
            timestamp = datetime(year, month, day, hour, minute, second)
            if timestamp != previous_date:
                mlat, mlon, mlt = aacgmv2.get_aacgm_coord(gdlat, glon, gdalt, timestamp,
                                                        method='ALLOWTRACE')
            previous_date = timestamp
            yield timestamp, mlat, mlon, mlt

    def convert(self):
        data = self.hdf5_file["Data"]["Table Layout"][()]
        aacgm_data = self.get_aacgm_data()

        for idx, converted_data in enumerate(aacgm_data):
            _, mlat, mlon, mlt = converted_data
            data[idx][15] = mlt
            data[idx][16] = mlat
            data[idx][17] = mlon

        self.hdf5_file["Data"]["Table Layout"][...] = data

    def close(self):
        self.hdf5_file.close()