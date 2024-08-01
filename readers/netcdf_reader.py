import os

import netCDF4


class NetCDFReader:
    """
    Read netCDF file using the "with" paradigm.
    """
    def __init__(self, file_path):
        self.file_path = file_path
        self._dataset = None
    
    # __enter__ method for the "with" statement
    def __enter__(self):
        try:
            self._dataset = netCDF4.Dataset(self.file_path)
        except FileNotFoundError:
            if self._dataset:
                self._dataset.close()
            print("Error: '%s' does not exist." % self.file_path)
            raise
        return self

    # __exit__ method for the "with" statement
    def __exit__(self, *args):
        if self._dataset:
            self._dataset.close()

    def get_var_keys(self):
        """
        Get all variable keys.
        """
        return self._dataset.variables.keys()

    def get_data(self, key):
        try:
            data = self._dataset.variables[key]
        except KeyError:
            print("Error: '%s' is not in %s." % (key, self.file_path))
            raise

        return data


if __name__ == '__main__':
    ERA_PATH = os.path.join("/media", "thibault", "My Passport", "DATA", "ERA5", "monthly", "pl")
    era_pl_filename = f"era5_pl_2007_0_25.nc"

    with NetCDFReader(os.path.join(ERA_PATH, era_pl_filename)) as data_reader:
        var_keys = data_reader.get_var_keys()

        for var_key in var_keys:
            print(var_key, data_reader.get_data(var_key))
        
        temp = data_reader.get_data('t')[:,:,:,:]
        print(type(temp))
        
    nc = netCDF4.Dataset(os.path.join(ERA_PATH, era_pl_filename))
    