from numba import jit, int64, float64
from kolya import parameters
from kolya import NLOpartonic as nlo
from kolya import NNLOpartonic as nnlo
from kolya import NLOpw as nlopw
from kolya import schemechange_KINMS as kin
from kolya.Elmoments_SM import X, XD, XG, XLS, Xpi
import math

def X_DeltaBR_KIN_MS(elcut, par, hqe, **kwargs):
    y=2*elcut/par.mbkin
    Elcuthat=elcut/par.mbkin
    r=par.mcMS/par.mbkin
    MBhat=par.MB/par.mbkin
    mus=par.scale_alphas/par.mbkin
    mu0=par.scale_mcMS/par.mbkin
    muWC=par.scale_mbkin/par.mbkin
    api=par.alphas/math.pi

    rhoD=hqe.rhoD/par.mbkin**3
    rhoLS=hqe.rhoLS/par.mbkin**3
    muG=hqe.muG/par.mbkin**2
    mupi=hqe.mupi/par.mbkin**2

    logy =math.log((1-y)/r**2)

    lr =math.log(r)

    pi2=math.pi**2
    z3=1.202056903159594
    beta0=9
    flagPERP=kwargs.get('flag_basisPERP', 1)
    flagDEBUG=kwargs.get('flag_DEBUG', 0)
    flagNONBLM=kwargs.get('flag_NONBLM', 1)
    flagTEST=kwargs.get('flag_TEST', 0)
    FLAGcD=0
    FLAGcf=0.5*( 3.*( math.log(par.scale_muG/par.mbkin)))
    FLAGcs=0

    deltambkin1 = kin.deltambkin(1,par)
    deltambkin2 = kin.deltambkin(2,par)
    deltamcMS1 = kin.deltamcMS(1,par)
    deltamcMS2 = kin.deltamcMS(2,par)
    Mupipert1 = kin.MuPiPert(1,par)/par.mbkin**2
    Mupipert2 = kin.MuPiPert(2,par)/par.mbkin**2
    Rhodpert1 = kin.RhoDPert(1,par)/par.mbkin**3
    Rhodpert2 = kin.RhoDPert(2,par)/par.mbkin**3

    deltambkin2BLM = kin.deltambkin(-2,par)
    deltamcMS2BLM  = kin.deltamcMS(-2,par)
    Mupipert2BLM   = kin.MuPiPert(-2,par)/par.mbkin**2
    Rhodpert2BLM   = kin.RhoDPert(-2,par)/par.mbkin**3

    flagNLOMuPi  = 1
    flagNLOMuG   = 1
    flagNLORhoD  = 0  # set to 1 when grids for NLO rhoD are available 
    flagNLORhoLS = 0  # set to 1 when grids for NLO rhoLS are available 

    res = 0
    res +=(X(0,Elcuthat,r,0,0)+rhoD*XD(0,Elcuthat,r,0,0)+muG*XG(0,Elcuthat,r,0,0)
        +rhoLS*XLS(0,Elcuthat,r,0,0)+mupi*Xpi(0,Elcuthat,r,0,0))

    if( flagDEBUG == 1):
        print("X_deltaBR LO = ",res)

    resNLO = 0
    resNLO +=(5*deltambkin1*X(0,Elcuthat,r,0,0)-deltambkin1*r*X(0,Elcuthat,r,0,1)
        +deltamcMS1*r*X(0,Elcuthat,r,0,1)-deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)
        +nlo.X1El(0,'SM',Elcuthat,r)-Rhodpert1*XD(0,Elcuthat,r,0,0)-Mupipert1*Xpi(0,Elcuthat,r,0,0))

    if( flagDEBUG == 1):
        print("X_deltaBR NLO = api*",resNLO)
    res += api*resNLO

    if(kwargs.get('flag_includeNNLO', 1) == 1):
        resNNLO = 0
        resNNLO +=(5*beta0*deltambkin2BLM*X(0,Elcuthat,r,0,0)-beta0*deltambkin2BLM*r*X(0,Elcuthat,r,0,1)
            +beta0*deltamcMS2BLM*r*X(0,Elcuthat,r,0,1)-beta0*deltambkin2BLM*Elcuthat*X(0,Elcuthat,r,1,0)
            +(beta0*math.log(mus**2)*nlo.X1El(0,'SM',Elcuthat,r))/4+beta0*nnlo.X2ElBLM(0,Elcuthat,r)
            -beta0*Rhodpert2BLM*XD(0,Elcuthat,r,0,0)-beta0*Mupipert2BLM*Xpi(0,Elcuthat,r,0,0))
        if( flagDEBUG == 1):
            print("X_deltaBR NNLO BLM = api^2*beta0*",resNNLO/beta0)
        res += api**2*resNNLO

        resNNLO = 0
        resNNLO +=(deltamcMS1*r*nlo.X1El_Derivativer(0,Elcuthat,r)+(deltamcMS2-beta0*deltamcMS2BLM)*r*X(0,Elcuthat,r,0,1)
            +(deltamcMS1**2*r**2*X(0,Elcuthat,r,0,2))/2+(deltambkin2-beta0*deltambkin2BLM)*(5*X(0,Elcuthat,r,0,0)
            -r*X(0,Elcuthat,r,0,1)-Elcuthat*X(0,Elcuthat,r,1,0))+deltambkin1**2*(10*X(0,Elcuthat,r,0,0)
            -4*r*X(0,Elcuthat,r,0,1)+(r**2*X(0,Elcuthat,r,0,2))/2-4*Elcuthat*X(0,Elcuthat,r,1,0)
            +Elcuthat*r*X(0,Elcuthat,r,1,1)+(Elcuthat**2*X(0,Elcuthat,r,2,0))/2)
            -(math.log(mus**2)*nlo.X1El(0,'SM',Elcuthat,r))/6+deltambkin1*(-(Elcuthat*nlo.X1El_DerivativeEl(0,Elcuthat,r))
            -r*nlo.X1El_Derivativer(0,Elcuthat,r)+deltamcMS1*(4*r*X(0,Elcuthat,r,0,1)-r**2*X(0,Elcuthat,r,0,2)
            -Elcuthat*r*X(0,Elcuthat,r,1,1))+5*nlo.X1El(0,'SM',Elcuthat,r))+flagTEST*nnlo.X2ElnonBLM(0,Elcuthat,r)
            -(Rhodpert2-beta0*Rhodpert2BLM)*XD(0,Elcuthat,r,0,0)+(Rhodpert1*math.log(mus**2/r**2)*XD(0,Elcuthat,r,0,0))/6
            -deltamcMS1*r*Rhodpert1*XD(0,Elcuthat,r,0,1)+deltambkin1*Rhodpert1*(
            -2*XD(0,Elcuthat,r,0,0)+r*XD(0,Elcuthat,r,0,1)+Elcuthat*XD(0,Elcuthat,r,1,0))
            -(Mupipert2-beta0*Mupipert2BLM)*Xpi(0,Elcuthat,r,0,0)+(Mupipert1*math.log(mus**2/r**2)*Xpi(0,Elcuthat,r,0,0))/6
            -deltamcMS1*Mupipert1*r*Xpi(0,Elcuthat,r,0,1)+deltambkin1*Mupipert1*(
            -3*Xpi(0,Elcuthat,r,0,0)+r*Xpi(0,Elcuthat,r,0,1)+Elcuthat*Xpi(0,Elcuthat,r,1,0)))
        resNNLO += nnlo.fitElNNLOnonBLM(0, Elcuthat, r)
        if( flagDEBUG == 1):
            print("X_deltaBR NNLO non-BLM = api^2*",resNNLO)
        res += api**2*resNNLO

    if(kwargs.get('flag_includeNLOpw', 1) == 1):
        resNLO = 0
        resNLO +=(flagNLORhoD*rhoD*(nlopw.X1ElRhoD(0,Elcuthat,r)+2*deltambkin1*XD(0,Elcuthat,r,0,0)
            +FLAGcD*XD(0,Elcuthat,r,0,0)-deltambkin1*r*XD(0,Elcuthat,r,0,1)
            +deltamcMS1*r*XD(0,Elcuthat,r,0,1)-deltambkin1*Elcuthat*XD(0,Elcuthat,r,1,0))
            +flagNLOMuG*muG*(nlopw.X1ElMuG(0,Elcuthat,r)+3*deltambkin1*XG(0,Elcuthat,r,0,0)
            +FLAGcf*XG(0,Elcuthat,r,0,0)-deltambkin1*r*XG(0,Elcuthat,r,0,1)
            +deltamcMS1*r*XG(0,Elcuthat,r,0,1)-deltambkin1*Elcuthat*XG(0,Elcuthat,r,1,0))
            +flagNLORhoLS*rhoLS*(nlopw.X1ElRhoLS(0,Elcuthat,r)+2*deltambkin1*XLS(0,Elcuthat,r,0,0)
            +FLAGcs*XLS(0,Elcuthat,r,0,0)-deltambkin1*r*XLS(0,Elcuthat,r,0,1)
            +deltamcMS1*r*XLS(0,Elcuthat,r,0,1)-deltambkin1*Elcuthat*XLS(0,Elcuthat,r,1,0))
            +flagNLOMuPi*mupi*(nlopw.X1ElMuPi(0,Elcuthat,r)+3*deltambkin1*Xpi(0,Elcuthat,r,0,0)
            -deltambkin1*r*Xpi(0,Elcuthat,r,0,1)+deltamcMS1*r*Xpi(0,Elcuthat,r,0,1)
            -deltambkin1*Elcuthat*Xpi(0,Elcuthat,r,1,0)))
        if( flagDEBUG == 1):
            print("X_deltaBR NLO pw = api*",resNLO)
        res += api*resNLO

        resNNLO = 0
        resNNLO +=(-(flagNLOMuPi*Mupipert1*nlopw.X1ElMuPi(0,Elcuthat,r))+flagNLORhoD*(-(Rhodpert1*nlopw.X1ElRhoD(0,Elcuthat,r))
            -FLAGcD*Rhodpert1*XD(0,Elcuthat,r,0,0)))
        if( flagDEBUG == 1):
            print("X_deltaBR NNLO from NLO pw = api^2*",resNNLO)
        res += api**2*resNNLO

    return res


