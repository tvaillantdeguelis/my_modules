import numpy as np

from my_modules.constants import *


def rh2waterppmv(rh, temp, press_level):
    """
    Convert RH to PPMv by computing the saturated vapor pressure at the mean temperature of each
    region level (Tetens' formula, valid between -50 and +50°C (J. Lenoble p.257).
    
    :param rh: water vapor (profile) [relative humidity in %]
    :param temp: temperature (profile) [K]
    :param press_level: pressure level (profile) [hPa]
    :return: water vapor (profile) [ppmv]
    """
    a = 7.5 # cst coeff
    b = 237.3 # cst coeff
    psat = 6.107*10**(7.5*(temp-273.15)/(temp-273.15+237.3))
    pw = psat*rh/100.
    ppmv = pw/(press_level-pw)*10**6

    return ppmv


def temp2virttemp(temp, spec_humidity):
    """
    Convert atmospheric temperature to virtual temperature.
    :param temp: temperature (profile) [K]
    :param spec_humidity: specific humidity (profile)
    :return: virtual temperature (profile) [K]
    """
    
    virttemp = (1 + (1/(GAS_CST_DRY_AIR/GAS_CST_WATER_VAPOR) - 1)*spec_humidity) * temp
    
    return virttemp


def press2alt(press, Tv):
    """
    Convert pressure level to altitude level with hydrostatic atmosphere calculation (hypsometric
    equation). The altitude reference (z = 0 km) is taken for the largest pressure level.
    :param press: pressure level profile [hPa]
    :param Tv: virtual temperature profile [K]
    :return: altitude level profile [m]
    """
    press_c = np.copy(press)
    Tv_c = np.copy(Tv)
    if press[0] < press[1]:
        press_c = press_c[::-1] # high press first
        Tv_c = Tv[::-1]
        
    alt = np.zeros(press_c.size)
    for i in range(alt.size-1):
        alt[i+1] = alt[i] + GAS_CST_DRY_AIR/STD_GRAV_ACC*(Tv_c[i+1]-Tv_c[i])* \
                   (np.log(press_c[i])-np.log(press_c[i+1]))/(np.log(Tv_c[i+1])-np.log(Tv_c[i]))
    if press[0] < press[1]:
        alt = alt[::-1]
        
    return alt


if __name__ == '__main__':
    print(rh2waterppmv(70, 288, 1000))
    print(GAS_CST_DRY_AIR/GAS_CST_WATER_VAPOR)
    

    
    
    
    
    


    