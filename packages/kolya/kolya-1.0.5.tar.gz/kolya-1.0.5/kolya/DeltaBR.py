from kolya import parameters
from kolya import DeltaBR_SM
from kolya import DeltaBR_NP
from kolya import DeltaBR_HO
import math

def X_DeltaBR_KIN_MS(elcut, par, hqe, wc, **kwargs):
    
    fmb4 = kwargs.get('flagmb4', 0)
    fmb5 = kwargs.get('flagmb5', 0)

    res = DeltaBR_SM.X_DeltaBR_KIN_MS(elcut, par, hqe, **kwargs)+DeltaBR_NP.X_DeltaBR_KIN_MS(elcut, par, hqe, wc, **kwargs)
    if (fmb4!=0 or fmb5!=0):
        res += DeltaBR_HO.X_DeltaBR_KIN_MS_HO(elcut, par, hqe, flagmb4 = fmb4, flagmb5 = fmb5)
    return res

def DeltaRate_KIN_MS(Vcb, elcut, par, hqe, wc, Aew=1.014, **kwargs):
    GF=1.1663788e-5 # Gev^-2
    
    return X_DeltaBR_KIN_MS(elcut, par, hqe, wc, **kwargs)*par.mbkin**5*GF**2/192/math.pi**3*Vcb**2*Aew

def DeltaBR_KIN_MS(Vcb, elcut, par, hqe, wc, Aew=1.014, **kwargs):
    """ Branching ratio as a function of El_cut """
    hbar=6.582119569e-25 # Gev s 
    tauBplus=1638e-15 # s 
    tauBzero=1519e-15 # s 
    return DeltaRate_KIN_MS(Vcb, elcut, par, hqe, wc, Aew, **kwargs)*(tauBplus+tauBzero)/2/hbar
