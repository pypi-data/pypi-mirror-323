from kolya import parameters
from kolya import MXmoments_SM
from kolya import MXmoments_NP
from kolya import MXmoments_HO
import math

def moment_1_KIN_MS(elcut, par, hqe, wc, **kwargs):
    """ Central moment of the MX spectrum. Moment n. 1 """
    
    flagmb4 = kwargs.get('flagmb4', 0)
    flagmb5 = kwargs.get('flagmb5', 0)

    res = MXmoments_SM.moment_1_KIN_MS(elcut, par, hqe, wc, **kwargs)+MXmoments_NP.moment_1_KIN_MS(elcut, par, hqe, wc)
    if (flagmb4!=0 or flagmb5!=0):
        res += MXmoments_HO.moment_1_KIN_MS_HO(elcut, par, hqe, flagmb4, flagmb5)
    return res

def moment_2_KIN_MS(elcut, par, hqe, wc, **kwargs):
    """ Central moment of the MX spectrum. Moment n. 2 """
    
    flagmb4 = kwargs.get('flagmb4', 0)
    flagmb5 = kwargs.get('flagmb5', 0)

    res = MXmoments_SM.moment_2_KIN_MS(elcut, par, hqe, wc, **kwargs)+MXmoments_NP.moment_2_KIN_MS(elcut, par, hqe, wc)
    if (flagmb4!=0 or flagmb5!=0):
        res += MXmoments_HO.moment_2_KIN_MS_HO(elcut, par, hqe, flagmb4, flagmb5)
    return res

def moment_3_KIN_MS(elcut, par, hqe, wc, **kwargs):
    """ Central moment of the MX spectrum. Moment n. 3 """
    
    flagmb4 = kwargs.get('flagmb4', 0)
    flagmb5 = kwargs.get('flagmb5', 0)

    res = MXmoments_SM.moment_3_KIN_MS(elcut, par, hqe, wc, **kwargs)+MXmoments_NP.moment_3_KIN_MS(elcut, par, hqe, wc)
    if (flagmb4!=0 or flagmb5!=0):
        res += MXmoments_HO.moment_3_KIN_MS_HO(elcut, par, hqe, flagmb4, flagmb5)
    return res

def moment_4_KIN_MS(elcut, par, hqe, wc, **kwargs):
    """ Central moment of the MX spectrum. Moment n. 4 """
    
    flagmb4 = kwargs.get('flagmb4', 0)
    flagmb5 = kwargs.get('flagmb5', 0)

    res = MXmoments_SM.moment_4_KIN_MS(elcut, par, hqe, wc, **kwargs)
    if (flagmb4!=0 or flagmb5!=0):
        res += MXmoments_HO.moment_4_KIN_MS_HO(elcut, par, hqe, flagmb4, flagmb5)
    return res