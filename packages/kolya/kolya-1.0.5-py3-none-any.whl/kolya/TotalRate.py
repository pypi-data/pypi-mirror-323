from kolya import parameters
from kolya import TotalRate_SM
from kolya import TotalRate_HO
from kolya import TotalRate_HO_RPI
from kolya import TotalRate_NP
import math
from scipy.special import spence

def X_Gamma_KIN_MS(par, hqe, wc, **kwargs):
    """ Total rate: coefficient X in front of Gamma0  """
    
    flagmb4 = kwargs.get('flagmb4', 0)
    flagmb5 = kwargs.get('flagmb5', 0)

    flag_basisPERP = kwargs.get('flag_basisPERP', 1)

    res = TotalRate_SM.X_Gamma_KIN_MS(par, hqe, wc, **kwargs)+TotalRate_NP.X_Gamma_KIN_MS_NP(par, hqe, wc, **kwargs)

    if flag_basisPERP == 1:
        if (flagmb4!=0 or flagmb5!=0):
            res += TotalRate_HO.X_Gamma_KIN_MS_HO(par, hqe, flagmb4, flagmb5)
    if flag_basisPERP == 0:
        if (flagmb4!=0 or flagmb5!=0):
            res += TotalRate_HO_RPI.X_Gamma_KIN_MS_RPI_HO(par, hqe, flagmb4, flagmb5)
    return res
  
def TotalRate_KIN_MS(Vcb, par, hqe, wc, Aew=1.014, **kwargs):
    """ Total rate  of B -> Xc l v in GeV """
    GF=1.1663788e-5 # Gev^-2
    return X_Gamma_KIN_MS( par, hqe, wc, **kwargs)*par.mbkin**5*GF**2/192/math.pi**3*Vcb**2*Aew

def BranchingRatio_KIN_MS(Vcb, par, hqe, wc, Aew=1.014, **kwargs):
    """ Branching ratio of B -> Xc l v """
    hbar=6.582119569e-25 # Gev s 
    tauBplus=1638e-15 # s 
    tauBzero=1519e-15 # s 
    return TotalRate_KIN_MS(Vcb, par, hqe, wc, Aew, **kwargs)*(tauBplus+tauBzero)/2/hbar
