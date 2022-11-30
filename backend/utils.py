import numpy as np
from astropy.time import Time
from pathlib import Path

crab_flux = 4.722281080894965e-10

def LiMaSiginficance(N_on, N_off, alpha, type=1):
    if type == 1:
        temp = N_on*np.log((1.+alpha)/alpha*(N_on/(N_on+N_off)))+N_off*np.log((1+alpha)*(N_off/(N_on+N_off)))
    
        if np.size(temp) != 1:
            for i, t in enumerate(temp):
                if t > 0:
                    temp[i] = np.sqrt(t)
                else:
                    temp[i] = np.nan
        else:
            if temp >0:
                temp = np.sqrt(temp)
            else:
                temp = np.nan

        significance = np.sign(N_on-alpha*N_off)*np.sqrt(2.)*temp
    else:
        significance = (N_on-alpha*N_off)/np.sqrt(alpha*(N_on+N_off))
    return significance


def MJD2UTC(mjd, return_astropy=False):
    """
    Convert MJD (Modified Julian Day) to UTC.

    Args:
        mjd (astorpy.time): MJD time
        return_astropy (bool): return astropy.time

    Return:
        str, astropy.time (optional): UTC time
    """

    refMJD = Time(mjd, format='mjd')
    if return_astropy:
        return refMJD.isot, refMJD
    else:
        return refMJD.isot

data_folder = Path()

table_css = """
        table
        {
          border-collapse: collapse;
        }
        th
        {
          color: #ffffff;
          background-color: #000000;
        }
        td
        {
          background-color: #cccccc;
        }
        table, th, td
        {
          font-family:Arial, Helvetica, sans-serif;
          border: 1px solid black;
          text-align: right;
          z-order: 2;
        }
        """