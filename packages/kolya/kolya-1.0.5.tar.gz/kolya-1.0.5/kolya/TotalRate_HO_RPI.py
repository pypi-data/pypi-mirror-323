from kolya import parameters
from kolya.NLOpartonic import X1Q2
import math
from scipy.special import spence

def X_Gamma_KIN_MS_RPI_HO(par, hqeRPI, flagmb4 = 1, flagmb5 = 1):
    r=par.mcMS/par.mbkin
    mu0=par.scale_mcMS/par.mbkin
    mus=par.scale_alphas/par.mbkin
    muWC=par.scale_mbkin/par.mbkin
    mumuG=par.scale_muG/par.mbkin
    api=par.alphas/math.pi

    mupi=hqeRPI.mupi/par.mbkin**2
    muG=hqeRPI.muG/par.mbkin**2
    rhoD=hqeRPI.rhoD/par.mbkin**3

    rEtilde=hqeRPI.rEtilde/par.mbkin**4
    rG=hqeRPI.rG/par.mbkin**4
    sEtilde=hqeRPI.sEtilde/par.mbkin**4
    sB=hqeRPI.sB/par.mbkin**4
    sqB=hqeRPI.sqB/par.mbkin**4
    X1=hqeRPI.X1/par.mbkin**5
    X2=hqeRPI.X2/par.mbkin**5
    X3=hqeRPI.X3/par.mbkin**5
    X4=hqeRPI.X4/par.mbkin**5
    X5=hqeRPI.X5/par.mbkin**5
    X6=hqeRPI.X6/par.mbkin**5
    X7=hqeRPI.X7/par.mbkin**5
    X8=hqeRPI.X8/par.mbkin**5
    X9=hqeRPI.X9/par.mbkin**5
    X10=hqeRPI.X10/par.mbkin**5

    res = 0
    if flagmb4 == 1:
        res +=((-8*rEtilde*(2+9*r**4-20*r**6+9*r**8+12*math.log(r)\
    ))/9)

        res +=((4*rG*(16-21*r**2+9*r**4-7*r**6+3*r**8+24*math.log(\
    r)))/9)

        res +=((-2*sEtilde*(-25+36*r**2-20*r**6+9*r**8-24*math.\
    log(r)))/9)

        res +=((2*(-1+r**2)**3*(1+5*r**2)*sB)/3)

        res +=(-1/36*(sqB*(25-48*r**2+36*r**4-16*r**6+3*r**8+24*\
    math.log(r))))
    if flagmb5 == 1:
        res +=((-4*(-1+r**2)**2*(7+29*r**2+72*r**4)*X1)/15)

        res +=((X2*(-144+85*r**2+180*r**6-400*r**8+279*r**10-840*\
    r**2*math.log(r)))/(90*r**2))

        res +=((X3*(26-45*r**2+20*r**4+20*r**6-30*r**8+9*r**10+40*\
    r**2*math.log(r)))/(5*r**2))

        res +=(-1/90*(X4*(72-115*r**2+180*r**6-200*r**8+63*r**10+\
    120*r**2*math.log(r)))/r**2)

        res +=(-4*(-1+r**2)**2*(-1+r**2+2*r**4)*X5)

        res +=((4*X6*(-11+18*r**2+9*r**4-34*r**6+18*r**8-12*math.\
    log(r)))/9)

        res +=((2*X7*(3+26*r**2-36*r**4+6*r**6+r**8+48*r**2*math.\
    log(r)))/(9*r**2))

        res +=((-4*X8*(3-r**2-9*r**4+24*r**6-26*r**8+9*r**10+12*r**\
    2*math.log(r)))/(9*r**2))

        res +=(-1/9*(X9*(-3+7*r**2+30*r**6-61*r**8+27*r**10+24*r**\
    2*math.log(r)))/r**2)

        res +=((X10*(3+23*r**2-36*r**4+24*r**6-23*r**8+9*r**10+48*\
    r**2*math.log(r)))/(9*r**2))

    return res
