import os

import matplotlib.pyplot as plt
import numpy as np
import sys

from readers.netcdf_reader import NetCDFReader
from geotools import change_map_grid_resolution

class ERAReader(NetCDFReader):
    def __init__(self, filepath, lat=None, lon=None):
        """
        Read ERA data and interpolate on new lat×lon grid (optional).
        
        :param filepath: ERA filepath
        :param lat: new latitude coordinates
        :param lon: new longitude coordinates
        """
        if (lat is None) != (lon is None):
            raise Exception("ERAReader error: If new coordinates, both lat and lon should be given.\n")
        self.lat = lat
        self.lon = lon
        super().__init__(filepath)
        
    def get_data(self, key):
        try:
            data = self._dataset.variables[key]
        except KeyError:
            print("Error: '%s' is not in %s." % (key, self.file_path))
            raise
        
        # Interpolate to new lat×lon
        if data.ndim >= 2 and ((self.lat is not None) or (self.lon is not None)):
            # Get position of lat and lon dimensions in data shape
            lat_dim_index = data.dimensions.index('latitude')
            lon_dim_index = data.dimensions.index('longitude')
            # Initialize new data shape with lat and lon size modified
            init_shape = data.shape
            new_shape = list(init_shape)
            new_shape[lat_dim_index] = self.lat.size
            new_shape[lon_dim_index] = self.lon.size
            FILL_VALUE = -9999.
            new_data = np.ma.ones(new_shape)*FILL_VALUE
            # Get initial lat and lon coordinates
            lat_init = self._dataset.variables['latitude'][:]
            lon_init = self._dataset.variables['longitude'][:]
            # Loop on each dim which is not lat or lon
            not_lat_lon_shape = np.delete(init_shape, [lat_dim_index, lon_dim_index])
            if not_lat_lon_shape.size == 1:
                for i in range(not_lat_lon_shape[0]): # we assume lat and lon are the last dims
                    new_data[i, :, :] = change_map_grid_resolution(data[i, :, :], lat_init,
                                                                   lon_init, self.lat, self.lon)
            elif not_lat_lon_shape.size == 2: # we assume lat and lon are the last dims
                for i in range(not_lat_lon_shape[0]):
                    for j in range(not_lat_lon_shape[1]):
                        new_data[i, j, :, :] = change_map_grid_resolution(data[i, j, :, :], lat_init,
                                                                          lon_init, self.lat, self.lon)
            else:
                print('not_lat_lon_shape.size > 2 not implemented yet.')
            data = new_data
        
        return data

if __name__ == '__main__':
    if True:
        ERA_PATH = os.path.join("/home", "thibault", "Documents", "Pro", "Recherche", "codes",
                            "DATA", "ERA5", "monthly", "sl")
        era_pl_filename = f"era5_sl_2007_0_25.nc"
        
        lat_2 = np.arange(-89, 90, 2)
        lon_2 = np.arange(1, 360, 2)
        
        with ERAReader(os.path.join(ERA_PATH, era_pl_filename)) as data_reader:
            lat_init = data_reader.get_data('latitude')[:]
            lon_init = data_reader.get_data('longitude')[:]
            temp_init = data_reader.get_data('t2m')[:,:,:]
            print(temp_init.shape)
            
        with ERAReader(os.path.join(ERA_PATH, era_pl_filename), lat_2, lon_2) as data_reader:
            temp_2 = data_reader.get_data('t2m')[:,:,:]
            print(temp_2.shape)
        
        plt.figure()
        plt.subplot(211)
        plt.pcolormesh(lon_init, lat_init, temp_init[7, :, :])
        plt.subplot(212)
        plt.pcolormesh(lon_2, lat_2, temp_2[7, :, :])
        plt.show()
    
    if False:
        ERA_PATH = os.path.join("/home", "thibault", "Documents", "Pro", "Recherche", "codes",
                            "DATA", "ERA5", "monthly", "pl")
        era_pl_filename = f"era5_pl_2007_0_25.nc"
        
        lat_2 = np.arange(-89, 90, 2)
        lon_2 = np.arange(1, 360, 2)
        
        with ERAReader(os.path.join(ERA_PATH, era_pl_filename)) as data_reader:
            lat_init = data_reader.get_data('latitude')[:]
            lon_init = data_reader.get_data('longitude')[:]
            temp_init = data_reader.get_data('t')[:,:,:,:]
            print(temp_init.shape)
            
        with ERAReader(os.path.join(ERA_PATH, era_pl_filename), lat_2, lon_2) as data_reader:
            temp_2 = data_reader.get_data('t')[:,:,:,:]
            print(temp_2.shape)
        
        plt.figure()
        plt.subplot(211)
        plt.pcolormesh(lon_init, lat_init, temp_init[7, -1, :, :])
        plt.subplot(212)
        plt.pcolormesh(lon_2, lat_2, temp_2[7, -1, :, :])
        plt.show()