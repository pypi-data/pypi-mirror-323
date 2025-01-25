from kolya import parameters
import math

def MuPiPert(order,par):
    """ Coefficients in the perturbative expansion of MuPiPert """
    pi=math.pi
    z3=1.202056903159594
    muWC = par.scale_mbkin
    mus = par.scale_alphas
    if (order == 1):
        return     ((4*muWC**2)/3)
    if (order == 2):
        return     ((4*muWC**2*(3*((91-3*pi**2)/18-(11*math.log((2*muWC)/mus))/6)+(3*(-13/9+(2*math.log((2*muWC)/mus))/3))/2))/3)
    if (order == 3):
        return     (muWC**2*((8*(-29/16+z3+math.log((2*muWC)/mus)/2))/3+(4*((-13699+552*pi**2
        +972*z3+(8340-144*pi**2)*math.log((2*muWC)/mus)-1584*math.log((2*muWC)/mus)**2)/144
        +(209-6*pi**2-156*math.log((2*muWC)/mus)+36*math.log((2*muWC)/mus)**2)/36+(96295
        -5340*pi**2+108*pi**4-18468*z3+24*(-2155+66*pi**2)*math.log((2*muWC)/mus)
        +8712*math.log((2*muWC)/mus)**2)/288))/3))
    #BLM!
    if (order == -2):
        return     (-(muWC**2*(-13/9+(2*math.log((2*muWC)/mus))/3)))
    raise ValueError("MuPiPert: order = ",order," not supported!")
    return 0

def RhoDPert(order,par):
    """ Coefficients in the perturbative expansion of RhoDPert """
    pi=math.pi
    z3=1.202056903159594
    muWC = par.scale_mbkin
    mus = par.scale_alphas
    if (order == 1):
        return     ((8*muWC**3)/9)
    if (order == 2):
        return     ((4*muWC**3*(3*((57-2*pi**2)/18-(11*math.log((2*muWC)/mus))/9)+(3*(-8/9+(4*math.log((2*muWC)/mus))/9))/2))/3)
    if (order == 3):
        return     (muWC**3*((-83+48*z3+24*math.log((2*muWC)/mus))/27+(4*((9*(-12133/972+(44*pi**2)/81
        +z3-((-217+4*pi**2)*math.log((2*muWC)/mus))/27-(44*math.log((2*muWC)/mus)**2)/27))/2
        +(179-6*pi**2-144*math.log((2*muWC)/mus)+36*math.log((2*muWC)/mus)**2)/54+(86707
        -5076*pi**2+108*pi**4-18468*z3+144*(-339+11*pi**2)*math.log((2*muWC)/mus)
        +8712*math.log((2*muWC)/mus)**2)/432))/3))
    #BLM!
    if (order == -2):
        return     (-(muWC**3*(-8/9+(4*math.log((2*muWC)/mus))/9)))
    raise ValueError("RhoDPrer: order = ",order," not supported!")
    return 0

def deltambkin(order,par):
    """ Coefficients in the perturbative expansion of mbOS/mbkin """
    pi=math.pi
    z3=1.202056903159594
    z5=1.0369277551433699
    a4 = 0.517479061673899386
    muWC = par.scale_mbkin
    mus = par.scale_alphas
    mcMS = par.mcMS
    mbkin= par.mbkin
    mu0 = par.scale_mcMS
    if (order == 1):
        return     ((16*muWC)/(9*mbkin)+(2*muWC**2)/(3*mbkin**2))
    if (order == 2):
        return     (3*((muWC**2*(-13/27+(2*math.log((2*muWC)/mus))/9))/mbkin**2+(muWC*(-128/81
        +(16*math.log((2*muWC)/mus))/27))/mbkin)+(muWC*(860/27-(8*pi**2)/9-(8*math.log(mus**2/mcMS**2))/27
        -(88*math.log((2*muWC)/mus))/9))/mbkin+(muWC**2*(91/9-pi**2/3-math.log(mus**2/mcMS**2)/9
        -(11*math.log((2*muWC)/mus))/3))/mbkin**2)
    if (order == 3):
        return     ((muWC**2*(32113/144-(445*pi**2)/36+pi**4/4-(171*z3)/4+(2*math.log(mu0**2/mcMS**2))/9
        +(-421/108+pi**2/9)*math.log(mus**2/mcMS**2)+math.log(mus**2/mcMS**2)**2/54+(-2155/18
        +(11*pi**2)/3+(11*math.log(mus**2/mcMS**2))/9)*math.log((2*muWC)/mus)+(121*math.log((2*muWC)/mus)**2)/6))/mbkin**2
        +(muWC*(43637/54-(1022*pi**2)/27+(2*pi**4)/3-114*z3+(16*math.log(mu0**2/mcMS**2))/27
        +(-974/81+(8*pi**2)/27)*math.log(mus**2/mcMS**2)+(4*math.log(mus**2/mcMS**2)**2)/81
        +(-10072/27+(88*pi**2)/9+(88*math.log(mus**2/mcMS**2))/27)*math.log((2*muWC)/mus)
        +(484*math.log((2*muWC)/mus)**2)/9))/mbkin+3*((muWC*(-20047/243+(208*pi**2)/81
        +(140*z3)/27+(128*math.log(mus**2/mcMS**2))/243+(3356/81-(16*pi**2)/27-(16*math.log(mus**2/mcMS**2))/81)*math.log((2*muWC)/mus)
        -(176*math.log((2*muWC)/mus)**2)/27))/mbkin+(muWC**2*(-14221/648+(23*pi**2)/27
        +(35*z3)/18+(13*math.log(mus**2/mcMS**2))/81+(707/54-(2*pi**2)/9-(2*math.log(mus**2/mcMS**2))/27)*math.log((2*muWC)/mus)
        -(22*math.log((2*muWC)/mus)**2)/9))/mbkin**2)+9*((muWC**2*(209/486-pi**2/81
        -(26*math.log((2*muWC)/mus))/81+(2*math.log((2*muWC)/mus)**2)/27))/mbkin**2+(muWC*(1292/729
        -(8*pi**2)/243-(256*math.log((2*muWC)/mus))/243+(16*math.log((2*muWC)/mus)**2)/81))/mbkin))
    #BLM!
    if (order == -2):
        return     ((-3*((muWC**2*(-13/27+(2*math.log((2*muWC)/mus))/9))/mbkin**2+(muWC*(-128/81
        +(16*math.log((2*muWC)/mus))/27))/mbkin))/2)
    raise ValueError("deltambkin: order = ",order," not supported!")
    return 0

def deltamcMS(order,par):
    """ Coefficients in the perturbative expansion of mcOS/mcMS """
    pi=math.pi
    z3=1.202056903159594
    z5=1.0369277551433699
    a4 = 0.517479061673899386
    mus = par.scale_alphas
    mcMS = par.mcMS
    mu0 = par.scale_mcMS
    if (order == 1):
        return     (4/3+math.log(mu0**2/mcMS**2))
    if (order == 2):
        return     (307/32+pi**2/3-z3/6+(pi**2*math.log(2))/9+(493*math.log(mu0**2/mcMS**2))/72+(43*math.log(mu0**2/mcMS**2)**2)/24
        +(-31/9-(31*math.log(mu0**2/mcMS**2))/12)*math.log(mu0**2/mus**2)+3*(-71/144-pi**2/18
        -(13*math.log(mu0**2/mcMS**2))/36-math.log(mu0**2/mcMS**2)**2/12+(2/9+math.log(mu0**2/mcMS**2)/6)*math.log(mu0**2/mus**2)))
    if (order == 3):
        return     (8481925/93312-(220*a4)/27+(652841*pi**2)/38880-(695*pi**4)/7776+(58*z3)/27
        -(1439*pi**2*z3)/432+(1975*z5)/216-(22*pi**2*math.log(2)**2)/81-(55*math.log(2)**4)/162
        +(177305/2592+(37*pi**2)/18-(67*z3)/36)*math.log(mu0**2/mcMS**2)+(19315*math.log(mu0**2/mcMS**2)**2)/864
        +(1591*math.log(mu0**2/mcMS**2)**3)/432+(-32839/576-(31*pi**2)/18+(31*z3)/36
        -(17695*math.log(mu0**2/mcMS**2))/432-(1333*math.log(mu0**2/mcMS**2)**2)/144)*math.log(mu0**2/mus**2)
        +(961/108+(961*math.log(mu0**2/mcMS**2))/144)*math.log(mu0**2/mus**2)**2+math.log(2)*((
        -575*pi**2)/162+(37*pi**2*math.log(mu0**2/mcMS**2))/54-(31*pi**2*math.log(mu0**2/mus**2))/54)
        +9*(2353/23328+(13*pi**2)/324+(7*z3)/54+(89/648+pi**2/54)*math.log(mu0**2/mcMS**2)
        +(13*math.log(mu0**2/mcMS**2)**2)/216+math.log(mu0**2/mcMS**2)**3/108+(-71/432-pi**2/54
        -(13*math.log(mu0**2/mcMS**2))/108-math.log(mu0**2/mcMS**2)**2/36)*math.log(mu0**2/mus**2)
        +(1/27+math.log(mu0**2/mcMS**2)/36)*math.log(mu0**2/mus**2)**2)+3*(-231847/23328+(8*a4)/27
        -(991*pi**2)/648+(61*pi**4)/1944-(241*z3)/72+(2*pi**2*math.log(2)**2)/81+math.log(2)**4/81
        +(-10129/1296-(49*pi**2)/108-(7*z3)/9)*math.log(mu0**2/mcMS**2)-(1103*math.log(mu0**2/mcMS**2)**2)/432
        -(10*math.log(mu0**2/mcMS**2)**3)/27+(1469/216+(43*pi**2)/108-z3/18+(1067*math.log(mu0**2/mcMS**2))/216
        +(37*math.log(mu0**2/mcMS**2)**2)/36)*math.log(mu0**2/mus**2)+(-31/27-(31*math.log(mu0**2/mcMS**2))/36)*math.log(mu0**2/mus**2)**2
        +math.log(2)*((-11*pi**2)/81-(pi**2*math.log(mu0**2/mcMS**2))/27+(pi**2*math.log(mu0**2/mus**2))/27)))
    #BLM!
    if (order == -2):
        return     ((-3*(-71/144-pi**2/18-(13*math.log(mu0**2/mcMS**2))/36-math.log(mu0**2/mcMS**2)**2/12
        +(2/9+math.log(mu0**2/mcMS**2)/6)*math.log(mu0**2/mus**2)))/2)
    raise ValueError("deltamcMS: order = ",order," not supported!")
    return 0

