from kolya import parameters
from kolya import Q2moments_SM
from kolya import Q2moments_NP
from kolya import Q2moments_HO
from kolya import Q2moments_HO_RPI
import math

def moment_1_KIN_MS(q2cut, par, hqe, wc, **kwargs):
    """ Central moment of the q2 spectrum. Moment n. 1 """
    
    flagmb4 = kwargs.get('flagmb4', 0)
    flagmb5 = kwargs.get('flagmb5', 0)
    flag_basisPERP = kwargs.get('flag_basisPERP', 1)

    res = Q2moments_SM.moment_1_KIN_MS(q2cut, par, hqe, wc, **kwargs)+Q2moments_NP.moment_1_KIN_MS(q2cut, par, hqe, wc)
    if flag_basisPERP == 1:
        if (flagmb4!=0 or flagmb5!=0):
            res += Q2moments_HO.moment_1_KIN_MS_HO(q2cut, par, hqe, flagmb4, flagmb5)
    if flag_basisPERP == 0:
        if (flagmb4!=0 or flagmb5!=0):
            res += Q2moments_HO_RPI.moment_1_KIN_MS_HO_RPI(q2cut, par, hqe, flagmb4, flagmb5)
    return res

def moment_2_KIN_MS(q2cut, par, hqe, wc, **kwargs):
    """ Central moment of the q2 spectrum. Moment n. 2 """

    flagmb4 = kwargs.get('flagmb4', 0)
    flagmb5 = kwargs.get('flagmb5', 0)
    flag_basisPERP = kwargs.get('flag_basisPERP', 1)

    res = Q2moments_SM.moment_2_KIN_MS(q2cut, par, hqe, wc, **kwargs)+Q2moments_NP.moment_2_KIN_MS(q2cut, par, hqe, wc)
    if flag_basisPERP == 1:
        if (flagmb4!=0 or flagmb5!=0):
            res += Q2moments_HO.moment_2_KIN_MS_HO(q2cut, par, hqe, flagmb4, flagmb5)
    if flag_basisPERP == 0:
        if (flagmb4!=0 or flagmb5!=0):
            res += Q2moments_HO_RPI.moment_2_KIN_MS_HO_RPI(q2cut, par, hqe, flagmb4, flagmb5)
    return res

def moment_3_KIN_MS(q2cut, par, hqe, wc, **kwargs):
    """ Central moment of the q2 spectrum. Moment n. 3 """

    flagmb4 = kwargs.get('flagmb4', 0)
    flagmb5 = kwargs.get('flagmb5', 0)
    flag_basisPERP = kwargs.get('flag_basisPERP', 1)

    res = Q2moments_SM.moment_3_KIN_MS(q2cut, par, hqe, wc, **kwargs)+Q2moments_NP.moment_3_KIN_MS(q2cut, par, hqe, wc)
    if flag_basisPERP == 1:
        if (flagmb4!=0 or flagmb5!=0):
            res += Q2moments_HO.moment_3_KIN_MS_HO(q2cut, par, hqe, flagmb4, flagmb5)
    if flag_basisPERP == 0:
        if (flagmb4!=0 or flagmb5!=0):
            res += Q2moments_HO_RPI.moment_3_KIN_MS_HO_RPI(q2cut, par, hqe, flagmb4, flagmb5)
    return res

def moment_4_KIN_MS(q2cut, par, hqe, wc, **kwargs):
    """ Central moment of the q2 spectrum. Moment n. 4 """

    flagmb4 = kwargs.get('flagmb4', 0)
    flagmb5 = kwargs.get('flagmb5', 0)
    flag_basisPERP = kwargs.get('flag_basisPERP', 1)

    res = Q2moments_SM.moment_4_KIN_MS(q2cut, par, hqe, wc, **kwargs)+Q2moments_NP.moment_4_KIN_MS(q2cut, par, hqe, wc)
    if flag_basisPERP == 1:
        if (flagmb4!=0 or flagmb5!=0):
            res += Q2moments_HO.moment_4_KIN_MS_HO(q2cut, par, hqe, flagmb4, flagmb5)
    if flag_basisPERP == 0:
        if (flagmb4!=0 or flagmb5!=0):
            res += Q2moments_HO_RPI.moment_4_KIN_MS_HO_RPI(q2cut, par, hqe, flagmb4, flagmb5)
    return res
