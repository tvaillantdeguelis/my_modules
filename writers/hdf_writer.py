#!/usr/bin/env python
# coding: utf8

import os

import numpy as np
from pyhdf.SD import SD, SDC

NP_TO_HDF4_DTYPE = {np.dtype(np.str_): SDC.CHAR,
                    np.dtype(np.int8): SDC.INT8,
                    np.dtype(np.int16): SDC.INT16,
                    np.dtype(np.int32): SDC.INT32,
                    np.dtype(np.uint8): SDC.UINT8,
                    np.dtype(np.uint16): SDC.UINT16,
                    np.dtype(np.uint32): SDC.UINT32,
                    np.dtype(np.float32): SDC.FLOAT32,
                    np.dtype(np.float64): SDC.FLOAT64}

NP_TO_STR_DTYPE =  {np.dtype(np.str_): "Char",
                    np.dtype(np.int8): "Int_8",
                    np.dtype(np.int16): "Int_16",
                    np.dtype(np.int32): "Int_32",
                    np.dtype(np.uint8): "UInt_8",
                    np.dtype(np.uint16): "UInt_16",
                    np.dtype(np.uint32): "UInt_32",
                    np.dtype(np.float32): "Float_32",
                    np.dtype(np.float64): "Float_64"}


class SDSData(object):
    def __init__(self, key, data, fillvalue=None):
        """
        :param str key: SDS name
        """

        # Put fillvalue where masked
        if fillvalue:
            data = data.filled(fillvalue)

        # Remove unecessary dimension (,1)
        if data.shape[-1] == 1:
            data = np.squeeze(data)
                      
        self.key = key
        self.data = data
        self.fillvalue = fillvalue
        self.format = NP_TO_STR_DTYPE[data.dtype]
        self.description = None
        self.units = None
        self.valid_range = None
        self.dim_labels = []
        self.attributes = []


def write_hdf(filename, params):

    # Remove file if already exist
    if os.path.isfile(filename):
        os.remove(filename)

    # Create HDF file
    hdfFile = SD(filename, SDC.WRITE|SDC.CREATE) 

    # Copy each param
    for param in params:
        
        param_data = np.copy(params[param].data)
        param_attrs = params[param].attributes
        param_dims = params[param].dim_labels

        # Create a dataset
        sds = hdfFile.create(params[param].key, 
                             NP_TO_HDF4_DTYPE[param_data.dtype],
                             param_data.shape) 
        
        # Set attributes
        if params[param].description:
            sds.description = params[param].description
        if params[param].units:
            sds.units = params[param].units
        if params[param].format:
            sds.format = params[param].format
        if params[param].valid_range:
            sds.valid_range = params[param].valid_range
        if params[param].fillvalue:
            sds.setfillvalue(params[param].fillvalue)
        for attr_key in param_attrs:
            setattr(sds, attr_key, param_attrs[attr_key])
        for i in range(len(param_dims)):
            sds.dim(i).setname(param_dims[i])

        # Assign values
        sds.set(param_data)

        # Close dataset 
        sds.endaccess() 

    # Close file 
    hdfFile.end()

    print("%s created" % filename)

    return
