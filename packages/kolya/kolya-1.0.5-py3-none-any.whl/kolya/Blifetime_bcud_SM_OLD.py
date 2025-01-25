from kolya import parameters
from kolya import schemechange_KINMS as kin
from kolya import Blifetimes_building_blocks as bl
import math

def X_Gamma_bcud_KIN_MS(par, hqe, wc, **kwargs):
    r=par.mcMS/par.mbkin
    mus=par.scale_alphas/par.mbkin
    mu0=par.scale_mcMS/par.mbkin
    muWC=par.scale_mbkin/par.mbkin
    api=par.alphas/math.pi

    rhoD=hqe.rhoD/par.mbkin**3
    rhoLS=hqe.rhoLS/par.mbkin**3
    muG=hqe.muG/par.mbkin**2
    mupi=hqe.mupi/par.mbkin**2

    flagPERP=kwargs.get('flag_basisPERP', 1)
    flagDEBUG=kwargs.get('flag_DEBUG', 0)
    FLAGcf=0.5*(4./3. + 3.*(1.+ math.log(par.scale_muG/par.mbkin)))
    FLAGcD=-8./3.*4./3.*math.log(par.scale_rhoD/par.mbkin)+3.*(1./2.-2./3.*math.log(par.scale_rhoD/par.mbkin))
    FLAGcs=0.5*(4./3. + 3.*(1.+math.log(par.scale_muG/par.mbkin)))

    deltambkin1 = kin.deltambkin(1,par)
    deltambkin2 = kin.deltambkin(2,par)
    deltambkin3 = kin.deltambkin(3,par)
    deltamcMS1 = kin.deltamcMS(1,par)
    deltamcMS2 = kin.deltamcMS(2,par)
    deltamcMS3 = kin.deltamcMS(3,par)
    Rhodpert1 = kin.RhoDPert(1,par)/par.mbkin**3
    Rhodpert2 = kin.RhoDPert(2,par)/par.mbkin**3
    Rhodpert3 = kin.RhoDPert(3,par)/par.mbkin**3
    Mupipert1 = kin.MuPiPert(1,par)/par.mbkin**2
    Mupipert2 = kin.MuPiPert(2,par)/par.mbkin**2
    Mupipert3 = kin.MuPiPert(3,par)/par.mbkin**2
    CWilson = bl.RGEvolve_O1O2_TraditionalBasis(par.scale_matchingEW,par.scale_alphas)
    print(CWilson)
    res = 0
    res +=(CWilson[0,0]**2*bl.Gij_bcud(1,1,0,r,mus,0,0)+CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,0,r,mus,0,0)
        +CWilson[0,1]**2*bl.Gij_bcud(2,2,0,r,mus,0,0))

    if( flagDEBUG == 1):
        print("X_Gamma LO = ",res)

    resNLO = 0
    resNLO +=((CWilson[0,0]*CWilson[1,0]*bl.Gij_bcud(1,1,0,r,mus,0,0))/2+CWilson[0,0]**2*bl.Gij_bcud(1,1,1,r,mus,0,0)
        +(CWilson[0,1]*CWilson[1,0]*bl.Gij_bcud(1,2,0,r,mus,0,0))/4+(CWilson[0,0]*CWilson[1,1]*bl.Gij_bcud(1,2,0,r,mus,0,0))/4
        +CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,1,r,mus,0,0)+(CWilson[0,1]*CWilson[1,1]*bl.Gij_bcud(2,2,0,r,mus,0,0))/2
        +deltambkin1*(5*CWilson[0,0]**2*bl.Gij_bcud(1,1,0,r,mus,0,0)-mus*CWilson[0,0]**2*bl.Gij_bcud(1,1,0,r,mus,0,1)
        -r*CWilson[0,0]**2*bl.Gij_bcud(1,1,0,r,mus,1,0)+5*CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,0,r,mus,0,0)
        -mus*CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,0,r,mus,0,1)-r*CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,0,r,mus,1,0)
        +5*CWilson[0,1]**2*bl.Gij_bcud(2,2,0,r,mus,0,0)-mus*CWilson[0,1]**2*bl.Gij_bcud(2,2,0,r,mus,0,1)
        -r*CWilson[0,1]**2*bl.Gij_bcud(2,2,0,r,mus,1,0))+deltamcMS1*(r*CWilson[0,0]**2*bl.Gij_bcud(1,1,0,r,mus,1,0)
        +r*CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,0,r,mus,1,0)+r*CWilson[0,1]**2*bl.Gij_bcud(2,2,0,r,mus,1,0))
        +CWilson[0,1]**2*bl.Gij_bcud(2,2,1,r,mus,0,0))

    if( flagDEBUG == 1):
        print("X_Gamma NLO partonic = api*",resNLO)
    res += api*resNLO

    if(kwargs.get('flag_includeNNLO', 1) == 1):
        resNNLO = 0
        resNNLO +=((CWilson[1,0]**2*bl.Gij_bcud(1,1,0,r,mus,0,0))/16+(CWilson[0,0]*CWilson[2,0]*bl.Gij_bcud(1,1,0,r,mus,0,0))/8
            +(CWilson[0,0]*CWilson[1,0]*bl.Gij_bcud(1,1,1,r,mus,0,0))/2+CWilson[0,0]**2*bl.Gij_bcud(1,1,2,r,mus,0,0)
            +(CWilson[1,0]*CWilson[1,1]*bl.Gij_bcud(1,2,0,r,mus,0,0))/16+(CWilson[0,1]*CWilson[2,0]*bl.Gij_bcud(1,2,0,r,mus,0,0))/16
            +(CWilson[0,0]*CWilson[2,1]*bl.Gij_bcud(1,2,0,r,mus,0,0))/16+(CWilson[0,1]*CWilson[1,0]*bl.Gij_bcud(1,2,1,r,mus,0,0))/4
            +(CWilson[0,0]*CWilson[1,1]*bl.Gij_bcud(1,2,1,r,mus,0,0))/4+CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,2,r,mus,0,0)
            +(CWilson[1,1]**2*bl.Gij_bcud(2,2,0,r,mus,0,0))/16+(CWilson[0,1]*CWilson[2,1]*bl.Gij_bcud(2,2,0,r,mus,0,0))/8
            +deltambkin2*(5*CWilson[0,0]**2*bl.Gij_bcud(1,1,0,r,mus,0,0)-mus*CWilson[0,0]**2*bl.Gij_bcud(1,1,0,r,mus,0,1)
            -r*CWilson[0,0]**2*bl.Gij_bcud(1,1,0,r,mus,1,0)+5*CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,0,r,mus,0,0)
            -mus*CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,0,r,mus,0,1)-r*CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,0,r,mus,1,0)
            +5*CWilson[0,1]**2*bl.Gij_bcud(2,2,0,r,mus,0,0)-mus*CWilson[0,1]**2*bl.Gij_bcud(2,2,0,r,mus,0,1)
            -r*CWilson[0,1]**2*bl.Gij_bcud(2,2,0,r,mus,1,0))+deltamcMS2*(r*CWilson[0,0]**2*bl.Gij_bcud(1,1,0,r,mus,1,0)
            +r*CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,0,r,mus,1,0)+r*CWilson[0,1]**2*bl.Gij_bcud(2,2,0,r,mus,1,0))
            +deltamcMS1**2*((r**2*CWilson[0,0]**2*bl.Gij_bcud(1,1,0,r,mus,2,0))/2+(r**2*CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,0,r,mus,2,0))/2
            +(r**2*CWilson[0,1]**2*bl.Gij_bcud(2,2,0,r,mus,2,0))/2)+deltambkin1**2*(10*CWilson[0,0]**2*bl.Gij_bcud(1,1,0,r,mus,0,0)
            -4*mus*CWilson[0,0]**2*bl.Gij_bcud(1,1,0,r,mus,0,1)+(mus**2*CWilson[0,0]**2*bl.Gij_bcud(1,1,0,r,mus,0,2))/2
            -4*r*CWilson[0,0]**2*bl.Gij_bcud(1,1,0,r,mus,1,0)+mus*r*CWilson[0,0]**2*bl.Gij_bcud(1,1,0,r,mus,1,1)
            +(r**2*CWilson[0,0]**2*bl.Gij_bcud(1,1,0,r,mus,2,0))/2+10*CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,0,r,mus,0,0)
            -4*mus*CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,0,r,mus,0,1)+(mus**2*CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,0,r,mus,0,2))/2
            -4*r*CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,0,r,mus,1,0)+mus*r*CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,0,r,mus,1,1)
            +(r**2*CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,0,r,mus,2,0))/2+10*CWilson[0,1]**2*bl.Gij_bcud(2,2,0,r,mus,0,0)
            -4*mus*CWilson[0,1]**2*bl.Gij_bcud(2,2,0,r,mus,0,1)+(mus**2*CWilson[0,1]**2*bl.Gij_bcud(2,2,0,r,mus,0,2))/2
            -4*r*CWilson[0,1]**2*bl.Gij_bcud(2,2,0,r,mus,1,0)+mus*r*CWilson[0,1]**2*bl.Gij_bcud(2,2,0,r,mus,1,1)
            +(r**2*CWilson[0,1]**2*bl.Gij_bcud(2,2,0,r,mus,2,0))/2)+(CWilson[0,1]*CWilson[1,1]*bl.Gij_bcud(2,2,1,r,mus,0,0))/2
            +math.log(mus**2)*((CWilson[0,0]*CWilson[1,0]*bl.Gij_bcud(1,1,0,r,mus,0,0))/12
            +(CWilson[0,0]**2*bl.Gij_bcud(1,1,1,r,mus,0,0))/6+(CWilson[0,1]*CWilson[1,0]*bl.Gij_bcud(1,2,0,r,mus,0,0))/24
            +(CWilson[0,0]*CWilson[1,1]*bl.Gij_bcud(1,2,0,r,mus,0,0))/24+(CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,1,r,mus,0,0))/6
            +(CWilson[0,1]*CWilson[1,1]*bl.Gij_bcud(2,2,0,r,mus,0,0))/12+(CWilson[0,1]**2*bl.Gij_bcud(2,2,1,r,mus,0,0))/6)
            +deltambkin1*((5*CWilson[0,0]*CWilson[1,0]*bl.Gij_bcud(1,1,0,r,mus,0,0))/2
            -(mus*CWilson[0,0]*CWilson[1,0]*bl.Gij_bcud(1,1,0,r,mus,0,1))/2-(r*CWilson[0,0]*CWilson[1,0]*bl.Gij_bcud(1,1,0,r,mus,1,0))/2
            +5*CWilson[0,0]**2*bl.Gij_bcud(1,1,1,r,mus,0,0)-mus*CWilson[0,0]**2*bl.Gij_bcud(1,1,1,r,mus,0,1)
            -r*CWilson[0,0]**2*bl.Gij_bcud(1,1,1,r,mus,1,0)+(5*CWilson[0,1]*CWilson[1,0]*bl.Gij_bcud(1,2,0,r,mus,0,0))/4
            +(5*CWilson[0,0]*CWilson[1,1]*bl.Gij_bcud(1,2,0,r,mus,0,0))/4-(mus*CWilson[0,1]*CWilson[1,0]*bl.Gij_bcud(1,2,0,r,mus,0,1))/4
            -(mus*CWilson[0,0]*CWilson[1,1]*bl.Gij_bcud(1,2,0,r,mus,0,1))/4-(r*CWilson[0,1]*CWilson[1,0]*bl.Gij_bcud(1,2,0,r,mus,1,0))/4
            -(r*CWilson[0,0]*CWilson[1,1]*bl.Gij_bcud(1,2,0,r,mus,1,0))/4+5*CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,1,r,mus,0,0)
            -mus*CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,1,r,mus,0,1)-r*CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,1,r,mus,1,0)
            +(5*CWilson[0,1]*CWilson[1,1]*bl.Gij_bcud(2,2,0,r,mus,0,0))/2-(mus*CWilson[0,1]*CWilson[1,1]*bl.Gij_bcud(2,2,0,r,mus,0,1))/2
            -(r*CWilson[0,1]*CWilson[1,1]*bl.Gij_bcud(2,2,0,r,mus,1,0))/2+deltamcMS1*(4*r*CWilson[0,0]**2*bl.Gij_bcud(1,1,0,r,mus,1,0)
            -mus*r*CWilson[0,0]**2*bl.Gij_bcud(1,1,0,r,mus,1,1)-r**2*CWilson[0,0]**2*bl.Gij_bcud(1,1,0,r,mus,2,0)
            +4*r*CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,0,r,mus,1,0)-mus*r*CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,0,r,mus,1,1)
            -r**2*CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,0,r,mus,2,0)+4*r*CWilson[0,1]**2*bl.Gij_bcud(2,2,0,r,mus,1,0)
            -mus*r*CWilson[0,1]**2*bl.Gij_bcud(2,2,0,r,mus,1,1)-r**2*CWilson[0,1]**2*bl.Gij_bcud(2,2,0,r,mus,2,0))
            +5*CWilson[0,1]**2*bl.Gij_bcud(2,2,1,r,mus,0,0)-mus*CWilson[0,1]**2*bl.Gij_bcud(2,2,1,r,mus,0,1)
            -r*CWilson[0,1]**2*bl.Gij_bcud(2,2,1,r,mus,1,0))+deltamcMS1*((r*CWilson[0,0]*CWilson[1,0]*bl.Gij_bcud(1,1,0,r,mus,1,0))/2
            +r*CWilson[0,0]**2*bl.Gij_bcud(1,1,1,r,mus,1,0)+(r*CWilson[0,1]*CWilson[1,0]*bl.Gij_bcud(1,2,0,r,mus,1,0))/4
            +(r*CWilson[0,0]*CWilson[1,1]*bl.Gij_bcud(1,2,0,r,mus,1,0))/4+r*CWilson[0,0]*CWilson[0,1]*bl.Gij_bcud(1,2,1,r,mus,1,0)
            +(r*CWilson[0,1]*CWilson[1,1]*bl.Gij_bcud(2,2,0,r,mus,1,0))/2+r*CWilson[0,1]**2*bl.Gij_bcud(2,2,1,r,mus,1,0))
            +CWilson[0,1]**2*bl.Gij_bcud(2,2,2,r,mus,0,0))
        if( flagDEBUG == 1):
            print("X_Gamma NNLO partonic = api^2*",resNNLO)
        res += api**2*resNNLO

    return res


