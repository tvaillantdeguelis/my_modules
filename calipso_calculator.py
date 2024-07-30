import numpy as np
import sys
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

from calipso_constants import *


def compute_par_ab532(tot_ab532, per_ab532):
    """
    Compute parallel attenuated backscatter at 532 nm as the difference between total
    attenuated backscatter at 532 nm and perpendicular attenuated backscatter at 532 nm
    """

    par_ab532 = tot_ab532 - per_ab532.filled(0) # filled mask value of per with 0 in order not
                                                # to get filled value here

    # Mask par_ab532 where 0 (all is due to per => fill value was in par)
    # check if the whole column is 0 in order not to mask isolated pixel with
    # value exactly equal to 0 by chance
    par_ab532 = np.ma.masked_where(np.repeat(np.sum(par_ab532, axis=1),
                                   par_ab532.shape[1]).reshape(par_ab532.shape)==0, par_ab532)

    return par_ab532


def compute_ab_mol_and_b_mol(mol_nd, O3_nd, alt, met_alt, wl, polar=None):
    """
    Compute molecular attenuated backscatter and backscatter from molecular and ozone number
    density.
    """

    # Initialization
    nb_prof = mol_nd.shape[0]
    ab_mol = np.ones((nb_prof, alt.size))*FILL_VALUE_FLOAT
    b_mol = np.ones((nb_prof, alt.size))*FILL_VALUE_FLOAT

    # Loop on profiles
    for i in range(nb_prof):
        _, b_mol_i, T2_mol, T2_O3 = make_molecular_model(mol_nd[i, :], O3_nd[i, :], met_alt,
                                                         alt, wl, polar)
        b_mol  [i, :] = b_mol_i
        ab_mol[i, :] = b_mol_i*T2_mol*T2_O3

    return ab_mol, b_mol


def make_molecular_model(mol_ND_met, O3_ND_met, Z_met, Z_data, wl, polar=None):
# mol_ND_met (molecular number density) and O3_ND_met (ozone number density)
# are 1-D arrays, with the max altitude at index 0 (I'm assuming these will be
# 33-element met data arrays)
#
# Z_met is the altitude array corresponding to the mol_ND_met
# and O3_ND_met array; Z_data is (intended to be) the standard
# CALIPSO altitude array
#
# wl is an integer -- either 532 or 1064 -- specifying the wavelength
# for the model
#
# the return value is an array of molecular attenuated backscatter
# coefficients, with dimensions equal to the dimensions of Z_data

# mol_ND_met (m^-3)
# O3_ND_met (m^-3)
# Z_met (km)
# Z_data (km)
# wl (nm)

    wavelengthOK = (wl == 532) | (wl == 1064)
    if not wavelengthOK:
        raise Exception(f"Error: Unrecognized wavelength: {wl}; use 532 or 1064 instead\n\n")
    
    # Define molecular and ozone cross section for each wavelength
    # see Table 4.2 in Hostetler et al. (2006; ATDB)
    if wl == 532:
        mol_backscatter_cross_sect = 5.982e-32 # (m^2 / sr^-1)
        mol_ext_cross_sect = 5.167e-31 # (m^2)
        O3_ext_cross_sect = 2.72846e-25 # (m^2)
        depolar = 0.00366 # depolarization ratio (b_per/b_par) for Cabannes
                          # scattering
    else: #  wl = 1064
        mol_backscatter_cross_sect = 3.620e-33 # (m^2 / sr^-1)
        mol_ext_cross_sect  = 3.127e-32 # (m^2)
    
    # Mask metdata (because not done automatically because no FillValue in CALIPSO HDF files)
    mol_ND_met = np.ma.masked_where(mol_ND_met == -9999., mol_ND_met)
    O3_ND_met = np.ma.masked_where(O3_ND_met == -9999., O3_ND_met)

    # Replace fillValue (used for negative altitudes) by lowest altitude
    # where no fillValue in order to get correct values at altitude
    # close to 0 km after interpolation
    # mol
    i = mol_ND_met.size - 1
    low_no_fillValue = mol_ND_met[i]
    while np.ma.is_masked(low_no_fillValue) and (i > 0):
        low_no_fillValue = mol_ND_met[i]
        i -= 1
    mol_ND_met = np.ma.filled(mol_ND_met, low_no_fillValue)
    # O3
    i = O3_ND_met.size - 1
    low_no_fillValue = O3_ND_met[i]
    while np.ma.is_masked(low_no_fillValue) and (i > 0):
        low_no_fillValue = O3_ND_met[i]
        i -= 1
    O3_ND_met = np.ma.filled(O3_ND_met, low_no_fillValue)
    
    # Interpolate (using log) to get density values for all lidar data alt
    Z_data = np.ma.filled(Z_data, -9999.) # pass in ndarray because masked
                                          # arrays are not supported by interp
    mol_ND_data = get_full_density_array(mol_ND_met, Z_met, Z_data)
    if False:
        plt.plot(mol_ND_met, Z_met, marker='o', c='r', label='met', zorder=-1)
        plt.scatter(mol_ND_data, Z_data, s=2, label='data')
        plt.legend()
        plt.title('Molecular number density')
        plt.show()

    # Convert number density to molecular backscatter coefficients
    beta_mol = 1000. * mol_backscatter_cross_sect * mol_ND_data # (km^-1 / sr^-1)

    if polar=='par':
        beta_mol = beta_mol / (1 + depolar)
    elif polar=='per':
        beta_mol = beta_mol * depolar / (1 + depolar)

    # Convert number density to molecular extinction coefficients
    ext_mol = 1000. * mol_ext_cross_sect * mol_ND_data # (km^-1)


    # Derive molecular two-way transmittance values from the extinction
    # coefficient
    T2_mol = extinction2two_way_transmittance(ext_mol, Z_data)


    if wl == 532:

        # Interpolate to get density values for all lidar data alt
        f = interp1d(Z_met, O3_ND_met)
        O3_ND_data = f(Z_data)
        if False:
            plt.plot(O3_ND_met, Z_met, marker='o', c='r', label='met',
                     zorder=-1)
            plt.scatter(O3_ND_data, Z_data, s=2, label='data')
            plt.legend()
            plt.title('Molecular number density')
            plt.show()

        # Convert number density to molecular extinction coefficients
        ext_O3 = 1000. * O3_ext_cross_sect * O3_ND_data # (km^-1)

        # Derive O3 two-way transmittance values from the extinction
        # coefficient
        T2_O3 = extinction2two_way_transmittance(ext_O3, Z_data)

    else: # 1064 nm
        # O3 two-way transmittance = 1
        T2_O3 = np.ones(T2_mol.size)


    return mol_ND_data, beta_mol, T2_mol, T2_O3


def get_full_density_array(metDensity, metAltitude, Z):
# metDensity and metAltitude are meteorological data from the CALIPSO
# level 1 files both are 1-D arrays, with the max altitude at index 0,
# and a max dimension of 33
#
# Z is a 1-D array of CALIPSO lidar data altitudes max altitude at index
# 0, max dimension = 583
#
# the return value, rho, is an array of interpolated "metDensity" values
# corresponding to each altitude in Z
    
    lnDensity = np.ma.log(metDensity)
    f = interp1d(metAltitude, lnDensity)
    rho = f(Z)
    rho = np.exp(rho)
    
    return rho


def extinction2two_way_transmittance(sigma, Z):
# sigma is an array of extinction coefficients Z is the corresponding
# altitude array
#
# the return value, T2, is an array of two-way transmittance values
    T2 = np.zeros(sigma.size)
# use trapezoid integration to convert extinction coefficients to
# optical depths by OMITTING the factor of 2 in the trapezoid scheme,
# we'll end up computing twice the optical depth at each range bin...
# which will work out just fine when we convert the optical depths into
# two-way transmittances
    for j in np.arange(1, T2.size):
        T2[j] = T2[j-1] + (sigma[j-1] + sigma[j]) * (Z[j-1] - Z[j])
        # (sigma[j-1] + sigma[j]) / 2 *2
    T2 = -1.0 * T2
    T2 = np.exp(T2)

    return T2


def nsf_from_V_domain_to_betap_domain(nsf, r_alt, laser_energy, calib, pgr=np.array((1,))):
    return nsf*np.sqrt(r_alt**2/(laser_energy*calib*pgr))


def rms_from_P_domain_to_betap_domain(rms, r_alt, laser_energy, gain, calib, pgr=np.array((1,))):
    return rms*r_alt**2/(laser_energy*gain*calib*pgr)


def compute_shotnoise(fcorr, nb_bins_shift_abs, nb_pixels, nsf, mol_ab):
    return fcorr[:, nb_bins_shift_abs].T * 1/np.sqrt(nb_pixels) * nsf * 1/np.sqrt(mol_ab)

  
def compute_backgroundnoise(fcorr, nb_bins_shift_abs, nb_pixels, rms, mol_ab):
    return fcorr[:, nb_bins_shift_abs].T * 1/np.sqrt(nb_pixels) * 1/mol_ab * rms