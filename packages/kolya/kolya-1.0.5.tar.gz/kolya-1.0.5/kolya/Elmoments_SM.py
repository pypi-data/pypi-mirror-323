from numba import jit, int64, float64
from kolya import parameters
from kolya import NLOpartonic as nlo
from kolya import NNLOpartonic as nnlo
from kolya import NLOpw as nlopw
from kolya import schemechange_KINMS as kin
import math

@jit(float64(int64, float64, float64, int64, int64), cache=True, nopython=True)
def X(i,elcuthat,r,dEl,dr):
    """ Tree level functions (partonic) for El moments and their derivatives """
    y  = 2*elcuthat
    logy = math.log((1-y)/r**2)
    # tree level function
    if (dEl == 0 and dr == 0 and i==0):
        return     (1-8*r**2-6*r**4+12*logy*r**4+4*r**6-r**8-(2*r**6)/(-1+y)**2-(6*r**4*(1
            +r**2))/(-1+y)-2*r**4*(-3+r**2)*y+2*(-1+r**2)*y**3+y**4)
    if (dEl == 0 and dr == 0 and i==1):
        return     (3*logy*r**4*(3+r**2)+(7-75*r**2-180*r**4+120*r**6-15*r**8+3*r**10)/20
            -r**6/(-1+y)**2-(r**4*(3+5*r**2))/(-1+y)+6*r**4*y-(r**4*(-3+r**2)*y**2)/2
            +(3*(-1+r**2)*y**4)/4+(2*y**5)/5)
    if (dEl == 0 and dr == 0 and i==2):
        return     (2*logy*r**4*(3+2*r**2)+(4-54*r**2-240*r**4+150*r**6+6*r**10-r**12)/30
            -r**6/(2*(-1+y)**2)-(r**4*(3+7*r**2))/(2*(-1+y))+(3*r**4*(3+r**2)*y)/2
            +(3*r**4*y**2)/2-(r**4*(-3+r**2)*y**3)/6+(3*(-1+r**2)*y**5)/10+y**6/6)
    if (dEl == 0 and dr == 0 and i==3):
        return     ((15*logy*r**4*(1+r**2))/4+(6-98*r**2-665*r**4+371*r**6+70*r**8+14*r**10
            -7*r**12+r**14)/112-r**6/(4*(-1+y)**2)-(3*r**4*(1+3*r**2))/(4*(-1+y))
            +r**4*(3+2*r**2)*y+(3*r**4*(3+r**2)*y**2)/8+(r**4*y**3)/2-(r**4*(-3+r**2)*y**4)/16
            +((-1+r**2)*y**6)/8+y**7/14)
    if (dEl == 0 and dr == 0 and i==4):
        return     ((3*logy*r**4*(3+4*r**2))/4+(25-480*r**2-4494*r**4+2128*r**6+1050*r**8
            -70*r**12+24*r**14-3*r**16)/1120-r**6/(8*(-1+y)**2)-(r**4*(3+11*r**2))/(8*(
            -1+y))+(15*r**4*(1+r**2)*y)/8+(r**4*(3+2*r**2)*y**2)/4+(r**4*(3+r**2)*y**3)/8
            +(3*r**4*y**4)/16-(r**4*(-3+r**2)*y**5)/40+(3*(-1+r**2)*y**7)/56+y**8/32)

    # derivative wrt Elcuthat
    if (dEl == 1 and dr == 0 and i==0):
        return     (-4*r**4*(-3+r**2)+(8*r**6)/(-1+y)**3+(12*r**4*(1+r**2))/(-1+y)**2+(24*r**4)/(
            -1+y)+12*(-1+r**2)*y**2+8*y**3)
    if (dEl == 1 and dr == 0 and i==1):
        return     (12*r**4+(4*r**6)/(-1+y)**3+(2*r**4*(3+5*r**2))/(-1+y)**2+(6*r**4*(3
            +r**2))/(-1+y)-2*r**4*(-3+r**2)*y+6*(-1+r**2)*y**3+4*y**4)
    if (dEl == 1 and dr == 0 and i==2):
        return     (3*r**4*(3+r**2)+(2*r**6)/(-1+y)**3+(r**4*(3+7*r**2))/(-1+y)**2+(4*r**4*(3
            +2*r**2))/(-1+y)+6*r**4*y-r**4*(-3+r**2)*y**2+3*(-1+r**2)*y**4+2*y**5)
    if (dEl == 1 and dr == 0 and i==3):
        return     (2*r**4*(3+2*r**2)+r**6/(-1+y)**3+(3*r**4*(1+3*r**2))/(2*(-1+y)**2)
            +(15*r**4*(1+r**2))/(2*(-1+y))+(3*r**4*(3+r**2)*y)/2+3*r**4*y**2-(r**4*(
            -3+r**2)*y**3)/2+(3*(-1+r**2)*y**5)/2+y**6)
    if (dEl == 1 and dr == 0 and i==4):
        return     ((15*r**4*(1+r**2))/4+r**6/(2*(-1+y)**3)+(r**4*(3+11*r**2))/(4*(-1+y)**2)
            +(3*(3*r**4+4*r**6))/(2*(-1+y))+r**4*(3+2*r**2)*y+(3*r**4*(3+r**2)*y**2)/4
            +(3*r**4*y**3)/2-(r**4*(-3+r**2)*y**4)/4+(3*(-1+r**2)*y**6)/4+y**7/2)

    # derivative wrt r
    if (dEl == 0 and dr == 1 and i==0):
        return     (48*logy*r**3-8*r*(2+6*r**2-3*r**4+r**6)-(12*r**5)/(-1+y)**2-(12*r**3*(2
            +3*r**2))/(-1+y)-12*r**3*(-2+r**2)*y+4*r*y**3)
    if (dEl == 0 and dr == 1 and i==1):
        return     (18*logy*r**3*(2+r**2)+(3*r*(-5-36*r**2+20*r**4-4*r**6+r**8))/2-(6*r**5)/(
            -1+y)**2-(6*r**3*(2+5*r**2))/(-1+y)+24*r**3*y-3*r**3*(-2+r**2)*y**2
            +(3*r*y**4)/2)
    if (dEl == 0 and dr == 1 and i==2):
        return     (24*logy*r**3*(1+r**2)-(2*r*(9+110*r**2-55*r**4-5*r**8+r**10))/5-(3*r**5)/(
            -1+y)**2-(3*r**3*(2+7*r**2))/(-1+y)+9*r**3*(2+r**2)*y+6*r**3*y**2
            -r**3*(-2+r**2)*y**3+(3*r*y**5)/5)
    if (dEl == 0 and dr == 1 and i==3):
        return     ((15*logy*r**3*(2+3*r**2))/2+(r*(-14-250*r**2+99*r**4+40*r**6+10*r**8
            -6*r**10+r**12))/8-(3*r**5)/(2*(-1+y)**2)-(3*(2*r**3+9*r**5))/(2*(-1
            +y))+12*r**3*(1+r**2)*y+(9*r**3*(2+r**2)*y**2)/4+2*r**3*y**3-(3*r**3*(
            -2+r**2)*y**4)/8+(r*y**6)/4)
    if (dEl == 0 and dr == 1 and i==4):
        return     (9*logy*r**3*(1+2*r**2)-(3*r*(40+959*r**2-252*r**4-350*r**6+35*r**10
            -14*r**12+2*r**14))/140-(3*r**5)/(4*(-1+y)**2)-(3*(2*r**3+11*r**5))/(4*(
            -1+y))+(15*r**3*(2+3*r**2)*y)/4+3*r**3*(1+r**2)*y**2+(3*r**3*(2+r**2)*y**3)/4
            +(3*r**3*y**4)/4-(3*r**3*(-2+r**2)*y**5)/20+(3*r*y**7)/28)

    # second derivative wrt Elcuthat
    if (dEl == 2 and dr == 0 and i==0):
        return     ((-48*r**6)/(-1+y)**4-(48*r**4*(1+r**2))/(-1+y)**3-(48*r**4)/(-1+y)**2
            +48*(-1+r**2)*y+48*y**2)
    if (dEl == 2 and dr == 0 and i==1):
        return     (-4*r**4*(-3+r**2)-(24*r**6)/(-1+y)**4-(8*r**4*(3+5*r**2))/(-1+y)**3
            -(12*r**4*(3+r**2))/(-1+y)**2+36*(-1+r**2)*y**2+32*y**3)
    if (dEl == 2 and dr == 0 and i==2):
        return     (12*r**4-(12*r**6)/(-1+y)**4-(4*r**4*(3+7*r**2))/(-1+y)**3-(8*r**4*(3
            +2*r**2))/(-1+y)**2-4*r**4*(-3+r**2)*y+24*(-1+r**2)*y**3+20*y**4)
    if (dEl == 2 and dr == 0 and i==3):
        return     (3*r**4*(3+r**2)-(6*r**6)/(-1+y)**4-(6*r**4*(1+3*r**2))/(-1+y)**3-(15*r**4*(1
            +r**2))/(-1+y)**2+12*r**4*y-3*r**4*(-3+r**2)*y**2+15*(-1+r**2)*y**4
            +12*y**5)
    if (dEl == 2 and dr == 0 and i==4):
        return     (2*r**4*(3+2*r**2)-(3*r**6)/(-1+y)**4-(r**4*(3+11*r**2))/(-1+y)**3-(3*r**4*(3
            +4*r**2))/(-1+y)**2+3*r**4*(3+r**2)*y+9*r**4*y**2-2*r**4*(-3+r**2)*y**3
            +9*(-1+r**2)*y**5+7*y**6)

    # second derivative wrt r
    if (dEl == 0 and dr == 2 and i==0):
        return     (144*logy*r**2-8*(2+30*r**2-15*r**4+7*r**6)-(60*r**4)/(-1+y)**2-(36*r**2*(2
            +5*r**2))/(-1+y)-12*r**2*(-6+5*r**2)*y+4*y**3)
    if (dEl == 0 and dr == 2 and i==1):
        return     (18*logy*r**2*(6+5*r**2)+(3*(-5-156*r**2+76*r**4-28*r**6+9*r**8))/2
            -(30*r**4)/(-1+y)**2-(6*r**2*(6+25*r**2))/(-1+y)+72*r**2*y-3*r**2*(
            -6+5*r**2)*y**2+(3*y**4)/2)
    if (dEl == 0 and dr == 2 and i==2):
        return     (24*logy*r**2*(3+5*r**2)-(2*(9+450*r**2-155*r**4-45*r**8+11*r**10))/5
            -(15*r**4)/(-1+y)**2-(3*r**2*(6+35*r**2))/(-1+y)+9*r**2*(6+5*r**2)*y
            +18*r**2*y**2-r**2*(-6+5*r**2)*y**3+(3*y**5)/5)
    if (dEl == 0 and dr == 2 and i==3):
        return     ((45*logy*r**2*(2+5*r**2))/2+(-14-990*r**2+135*r**4+280*r**6+90*r**8
            -66*r**10+13*r**12)/8-(15*r**4)/(2*(-1+y)**2)-(9*(2*r**2+15*r**4))/(2*(
            -1+y))+12*r**2*(3+5*r**2)*y+(9*r**2*(6+5*r**2)*y**2)/4+6*r**2*y**3
            -(3*r**2*(-6+5*r**2)*y**4)/8+y**6/4)
    if (dEl == 0 and dr == 2 and i==4):
        return     (9*logy*r**2*(3+10*r**2)-(3*(40+3717*r**2+420*r**4-2450*r**6+385*r**10
            -182*r**12+30*r**14))/140-(15*r**4)/(4*(-1+y)**2)-(3*(6*r**2+55*r**4))/(4*(
            -1+y))+(45*r**2*(2+5*r**2)*y)/4+3*r**2*(3+5*r**2)*y**2+(3*r**2*(6
            +5*r**2)*y**3)/4+(9*r**2*y**4)/4-(3*r**2*(-6+5*r**2)*y**5)/20+(3*y**7)/28)

    # second derivative wrt Elcuthat and r
    if (dEl == 1 and dr == 1 and i==0):
        return     (-24*r**3*(-2+r**2)+(48*r**5)/(-1+y)**3+(24*r**3*(2+3*r**2))/(-1+y)**2
            +(96*r**3)/(-1+y)+24*r*y**2)
    if (dEl == 1 and dr == 1 and i==1):
        return     (48*r**3+(24*r**5)/(-1+y)**3+(12*r**3*(2+5*r**2))/(-1+y)**2+(36*r**3*(2
            +r**2))/(-1+y)-12*r**3*(-2+r**2)*y+12*r*y**3)
    if (dEl == 1 and dr == 1 and i==2):
        return     (18*r**3*(2+r**2)+(12*r**5)/(-1+y)**3+(6*r**3*(2+7*r**2))/(-1+y)**2
            +(48*r**3*(1+r**2))/(-1+y)+24*r**3*y-6*r**3*(-2+r**2)*y**2+6*r*y**4)
    if (dEl == 1 and dr == 1 and i==3):
        return     (24*r**3*(1+r**2)+(6*r**5)/(-1+y)**3+(3*r**3*(2+9*r**2))/(-1+y)**2+(15*r**3*(2
            +3*r**2))/(-1+y)+9*r**3*(2+r**2)*y+12*r**3*y**2-3*r**3*(-2+r**2)*y**3
            +3*r*y**5)
    if (dEl == 1 and dr == 1 and i==4):
        return     ((15*r**3*(2+3*r**2))/2+(3*r**5)/(-1+y)**3+(3*(2*r**3+11*r**5))/(2*(-1
            +y)**2)+(18*r**3*(1+2*r**2))/(-1+y)+12*r**3*(1+r**2)*y+(9*r**3*(2
            +r**2)*y**2)/2+6*r**3*y**3-(3*r**3*(-2+r**2)*y**4)/2+(3*r*y**6)/2)
    return 0. 

@jit(float64(int64, float64, float64, int64, int64), cache=True, nopython=True)
def Xpi(i,elcuthat,r,dEl,dr):
    """ Tree level functions (mupi) for El moments and their derivatives """
    y  = 2*elcuthat
    logy = math.log((1-y)/r**2)
    # tree level function
    if (dEl == 0 and dr == 0 and i==0):
        return     (-6*logy*r**4+(-1+8*r**2-2*r**4-4*r**6+r**8)/2-(2*r**6)/(-1+y)**4
            -(2*(3*r**4+10*r**6))/(3*(-1+y)**3)+(-21*r**4-20*r**6)/(3*(-1+y)**2)
            -(6*r**4)/(-1+y)+(4*r**4*(-3+r**2)*y)/3+(5*y**4)/6)
    if (dEl == 0 and dr == 0 and i==1):
        return     (-2*r**4*(3+r**2)-r**6/(-1+y)**4+(-3*r**4-14*r**6)/(3*(-1+y)**3)-(5*(3*r**4
            +5*r**6))/(3*(-1+y)**2)-(10*(3*r**4+2*r**6))/(3*(-1+y))-3*r**4*y+(r**4*(
            -3+r**2)*y**2)/3+y**5/3)
    if (dEl == 0 and dr == 0 and i==2):
        return     ((5*logy*r**4*(3+2*r**2))/3+(4-54*r**2-456*r**4+6*r**6+6*r**10-r**12)/36
            -r**6/(2*(-1+y)**4)+(-r**4-6*r**6)/(2*(-1+y)**3)+(-39*r**4-92*r**6)/(12*(
            -1+y)**2)-(5*(6*r**4+7*r**6))/(3*(-1+y))-(3*r**4*y**2)/4+(r**4*(-3
            +r**2)*y**3)/9+(5*y**6)/36)
    if (dEl == 0 and dr == 0 and i==3):
        return     ((15*logy*r**4*(1+r**2))/2+(6-98*r**2-945*r**4+91*r**6+70*r**8+14*r**10
            -7*r**12+r**14)/56-r**6/(4*(-1+y)**4)+(-3*r**4-22*r**6)/(12*(-1+y)**3)
            +(-24*r**4-73*r**6)/(12*(-1+y)**2)-(3*(11*r**4+18*r**6))/(4*(-1+y))
            +(5*r**4*(3+2*r**2)*y)/6-(r**4*y**3)/4+(r**4*(-3+r**2)*y**4)/24+(5*y**7)/84)
    if (dEl == 0 and dr == 0 and i==4):
        return     ((21*logy*r**4*(3+4*r**2))/8+(25-480*r**2-5694*r**4+528*r**6+1050*r**8
            -70*r**12+24*r**14-3*r**16)/320-r**6/(8*(-1+y)**4)+(-3*r**4-26*r**6)/(24*(
            -1+y)**3)+(-57*r**4-212*r**6)/(48*(-1+y)**2)-(7*(21*r**4+44*r**6))/(24*(
            -1+y))+(15*r**4*(1+r**2)*y)/4+(5*r**4*(3+2*r**2)*y**2)/24-(3*r**4*y**4)/32
            +(r**4*(-3+r**2)*y**5)/60+(5*y**8)/192)

    # derivative wrt Elcuthat
    if (dEl == 1 and dr == 0 and i==0):
        return     ((8*r**4*(-3+r**2))/3+(16*r**6)/(-1+y)**5+(4*(3*r**4+10*r**6))/(-1+y)**4
            +(4*(21*r**4+20*r**6))/(3*(-1+y)**3)+(12*r**4)/(-1+y)**2-(12*r**4)/(
            -1+y)+(20*y**3)/3)
    if (dEl == 1 and dr == 0 and i==1):
        return     (-6*r**4+(8*r**6)/(-1+y)**5+(2*(3*r**4+14*r**6))/(-1+y)**4+(20*(3*r**4
            +5*r**6))/(3*(-1+y)**3)+(20*(3*r**4+2*r**6))/(3*(-1+y)**2)+(4*r**4*(
            -3+r**2)*y)/3+(10*y**4)/3)
    if (dEl == 1 and dr == 0 and i==2):
        return     ((4*r**6)/(-1+y)**5+(3*(r**4+6*r**6))/(-1+y)**4+(39*r**4+92*r**6)/(3*(
            -1+y)**3)+(10*(6*r**4+7*r**6))/(3*(-1+y)**2)+(10*r**4*(3+2*r**2))/(3*(
            -1+y))-3*r**4*y+(2*r**4*(-3+r**2)*y**2)/3+(5*y**5)/3)
    if (dEl == 1 and dr == 0 and i==3):
        return     ((5*r**4*(3+2*r**2))/3+(2*r**6)/(-1+y)**5+(3*r**4+22*r**6)/(2*(-1+y)**4)
            +(24*r**4+73*r**6)/(3*(-1+y)**3)+(3*(11*r**4+18*r**6))/(2*(-1+y)**2)
            +(15*r**4*(1+r**2))/(-1+y)-(3*r**4*y**2)/2+(r**4*(-3+r**2)*y**3)/3+(5*y**6)/6)
    if (dEl == 1 and dr == 0 and i==4):
        return     ((15*r**4*(1+r**2))/2+r**6/(-1+y)**5+(3*r**4+26*r**6)/(4*(-1+y)**4)
            +(57*r**4+212*r**6)/(12*(-1+y)**3)+(7*(21*r**4+44*r**6))/(12*(-1+y)**2)
            +(21*(3*r**4+4*r**6))/(4*(-1+y))+(5*r**4*(3+2*r**2)*y)/6-(3*r**4*y**3)/4
            +(r**4*(-3+r**2)*y**4)/6+(5*y**7)/12)

    # derivative wrt r
    if (dEl == 0 and dr == 1 and i==0):
        return     (4*r*(2+2*r**2-3*r**4+r**6)-(12*r**5)/(-1+y)**4-(8*(r**3+5*r**5))/(
            -1+y)**3-(4*(7*r**3+10*r**5))/(-1+y)**2-(24*r**3)/(-1+y)+8*r**3*(
            -2+r**2)*y-24*r**3*math.log((1-y)/r**2))
    if (dEl == 0 and dr == 1 and i==1):
        return     (-12*r**3*(2+r**2)-(6*r**5)/(-1+y)**4-(4*(r**3+7*r**5))/(-1+y)**3-(10*(2*r**3
            +5*r**5))/(-1+y)**2-(40*(r**3+r**5))/(-1+y)-12*r**3*y+2*r**3*(-2
            +r**2)*y**2)
    if (dEl == 0 and dr == 1 and i==2):
        return     (-1/3*(r*(9+182*r**2+17*r**4-5*r**8+r**10))-(3*r**5)/(-1+y)**4-(2*(r**3
            +9*r**5))/(-1+y)**3+(-13*r**3-46*r**5)/(-1+y)**2-(10*(4*r**3+7*r**5))/(
            -1+y)-3*r**3*y**2+(2*r**3*(-2+r**2)*y**3)/3+20*r**3*(1+r**2)*math.log((1
            -y)/r**2))
    if (dEl == 0 and dr == 1 and i==3):
        return     ((r*(-14-330*r**2-21*r**4+40*r**6+10*r**8-6*r**10+r**12))/4-(3*r**5)/(2*(
            -1+y)**4)+(-r**3-11*r**5)/(-1+y)**3+(-16*r**3-73*r**5)/(2*(-1+y)**2)
            -(3*(11*r**3+27*r**5))/(-1+y)+10*r**3*(1+r**2)*y-r**3*y**3+(r**3*(
            -2+r**2)*y**4)/4+15*r**3*(2+3*r**2)*math.log((1-y)/r**2))
    if (dEl == 0 and dr == 1 and i==4):
        return     ((-3*r*(40+1159*r**2+148*r**4-350*r**6+35*r**10-14*r**12+2*r**14))/40
            -(3*r**5)/(4*(-1+y)**4)+(-r**3-13*r**5)/(2*(-1+y)**3)+(-19*r**3-106*r**5)/(4*(
            -1+y)**2)-(7*(7*r**3+22*r**5))/(2*(-1+y))+(15*r**3*(2+3*r**2)*y)/2
            +(5*r**3*(1+r**2)*y**2)/2-(3*r**3*y**4)/8+(r**3*(-2+r**2)*y**5)/10+(63*r**3*(1
            +2*r**2)*math.log((1-y)/r**2))/2)
    return 0. 

@jit(float64(int64, float64, float64, int64, int64), cache=True, nopython=True)
def XG(i,elcuthat,r,dEl,dr):
    """ Tree level functions (mupi) for El moments and their derivatives """
    y  = 2*elcuthat
    logy = math.log((1-y)/r**2)
    # tree level function
    if (dEl == 0 and dr == 0 and i==0):
        return     (6*logy*r**4+(-9-54*r**4+52*r**6-15*r**8)/6+(10*r**6)/(3*(-1+y)**3)
            +(9*r**4+20*r**6)/(3*(-1+y)**2)+(2*(-2*r**2+3*r**4))/(-1+y)-(2*r**2*(6
            -9*r**2+5*r**4)*y)/3-4*r**2*y**2-(4*y**3)/3-(5*y**4)/6)
    if (dEl == 0 and dr == 0 and i==1):
        return     (2*logy*r**2+(-6-7*r**2+15*r**4+39*r**6-14*r**8+3*r**10)/6+(5*r**6)/(3*(
            -1+y)**3)+(9*r**4+35*r**6)/(6*(-1+y)**2)+(2*(-3*r**2+9*r**4+10*r**6))/(3*(
            -1+y))+3*r**4*y-(r**2*(6-9*r**2+5*r**4)*y**2)/6-(4*r**2*y**3)/3-y**4/2
            -y**5/3)
    if (dEl == 0 and dr == 0 and i==2):
        return     (-1/3*(logy*r**2*(-6+9*r**2+10*r**4))+(-104-300*r**2+1800*r**4+450*r**6
            -420*r**8+144*r**10-25*r**12)/180+(5*r**6)/(6*(-1+y)**3)+(9*r**4+50*r**6)/(12*(
            -1+y)**2)+(-6*r**2+27*r**4+55*r**6)/(6*(-1+y))+r**2*y+(3*r**4*y**2)/4
            -(r**2*(6-9*r**2+5*r**4)*y**3)/18-(r**2*y**4)/2-y**5/5-(5*y**6)/36)
    if (dEl == 0 and dr == 0 and i==3):
        return     (-1/4*(logy*r**2*(-6+15*r**2+25*r**4))+(-530-2604*r**2+20685*r**4+875*r**6
            -5250*r**8+1680*r**10-511*r**12+75*r**14)/1680+(5*r**6)/(12*(-1+y)**3)
            +(9*r**4+65*r**6)/(24*(-1+y)**2)+(-2*r**2+12*r**4+35*r**6)/(4*(-1+y))
            -(r**2*(-6+9*r**2+10*r**4)*y)/6+(r**2*y**2)/4+(r**4*y**3)/4-(r**2*(6
            -9*r**2+5*r**4)*y**4)/48-(r**2*y**5)/5-y**6/12-(5*y**7)/84)
    if (dEl == 0 and dr == 0 and i==4):
        return     (-1/8*(logy*r**2*(-8+27*r**2+60*r**4))+(-1125-8064*r**2+76566*r**4+1680*r**6
            -27650*r**8+8400*r**10-3066*r**12+824*r**14-105*r**16)/6720+(5*r**6)/(24*(
            -1+y)**3)+(9*r**4+80*r**6)/(48*(-1+y)**2)+(-6*r**2+45*r**4+170*r**6)/(24*(
            -1+y))-(r**2*(-6+15*r**2+25*r**4)*y)/8-(r**2*(-6+9*r**2+10*r**4)*y**2)/24
            +(r**2*y**3)/12+(3*r**4*y**4)/32-(r**2*(6-9*r**2+5*r**4)*y**5)/120-(r**2*y**6)/12
            -y**7/28-(5*y**8)/192)

    # derivative wrt Elcuthat
    if (dEl == 1 and dr == 0 and i==0):
        return     ((-4*r**2*(6-9*r**2+5*r**4))/3-(20*r**6)/(-1+y)**4-(4*(9*r**4+20*r**6))/(3*(
            -1+y)**3)-(4*(-2*r**2+3*r**4))/(-1+y)**2+(12*r**4)/(-1+y)-16*r**2*y
            -8*y**2-(20*y**3)/3)
    if (dEl == 1 and dr == 0 and i==1):
        return     (6*r**4-(10*r**6)/(-1+y)**4-(2*(9*r**4+35*r**6))/(3*(-1+y)**3)-(4*(
            -3*r**2+9*r**4+10*r**6))/(3*(-1+y)**2)+(4*r**2)/(-1+y)-(2*r**2*(6
            -9*r**2+5*r**4)*y)/3-8*r**2*y**2-4*y**3-(10*y**4)/3)
    if (dEl == 1 and dr == 0 and i==2):
        return     (2*r**2-(5*r**6)/(-1+y)**4+(-9*r**4-50*r**6)/(3*(-1+y)**3)+(6*r**2-27*r**4
            -55*r**6)/(3*(-1+y)**2)-(2*(-6*r**2+9*r**4+10*r**6))/(3*(-1+y))+3*r**4*y
            -(r**2*(6-9*r**2+5*r**4)*y**2)/3-4*r**2*y**3-2*y**4-(5*y**5)/3)
    if (dEl == 1 and dr == 0 and i==3):
        return     (-1/3*(r**2*(-6+9*r**2+10*r**4))-(5*r**6)/(2*(-1+y)**4)+(-9*r**4-65*r**6)/(6*(
            -1+y)**3)+(2*r**2-12*r**4-35*r**6)/(2*(-1+y)**2)+(6*r**2-15*r**4
            -25*r**6)/(2*(-1+y))+r**2*y+(3*r**4*y**2)/2-(r**2*(6-9*r**2+5*r**4)*y**3)/6
            -2*r**2*y**4-y**5-(5*y**6)/6)
    if (dEl == 1 and dr == 0 and i==4):
        return     (-1/4*(r**2*(-6+15*r**2+25*r**4))-(5*r**6)/(4*(-1+y)**4)+(-9*r**4-80*r**6)/(12*(
            -1+y)**3)+(6*r**2-45*r**4-170*r**6)/(12*(-1+y)**2)+(8*r**2-27*r**4
            -60*r**6)/(4*(-1+y))-(r**2*(-6+9*r**2+10*r**4)*y)/6+(r**2*y**2)/2+(3*r**4*y**3)/4
            -(r**2*(6-9*r**2+5*r**4)*y**4)/12-r**2*y**5-y**6/2-(5*y**7)/12)

    # derivative wrt r
    if (dEl == 0 and dr == 1 and i==0):
        return     (-4*r**3*(12-13*r**2+5*r**4)+(20*r**5)/(-1+y)**3+(4*(3*r**3+10*r**5))/(
            -1+y)**2+(8*(-r+3*r**3))/(-1+y)-4*r*(2-6*r**2+5*r**4)*y-8*r*y**2
            +24*r**3*math.log((1-y)/r**2))
    if (dEl == 0 and dr == 1 and i==1):
        return     ((r*(-19+30*r**2+117*r**4-56*r**6+15*r**8))/3+(10*r**5)/(-1+y)**3+(6*r**3
            +35*r**5)/(-1+y)**2+(4*(-r+6*r**3+10*r**5))/(-1+y)+12*r**3*y-r*(2
            -6*r**2+5*r**4)*y**2-(8*r*y**3)/3+4*r*math.log((1-y)/r**2))
    if (dEl == 0 and dr == 1 and i==2):
        return     (-1/3*(r*(22-138*r**2-65*r**4+56*r**6-24*r**8+5*r**10))+(5*r**5)/(-1
            +y)**3+(3*r**3+25*r**5)/(-1+y)**2+(-2*r+18*r**3+55*r**5)/(-1+y)
            +2*r*y+3*r**3*y**2-(r*(2-6*r**2+5*r**4)*y**3)/3-r*y**4-4*r*(-1+3*r**2
            +5*r**4)*math.log((1-y)/r**2))
    if (dEl == 0 and dr == 1 and i==3):
        return     ((r*(-244+2270*r**2+625*r**4-1000*r**6+400*r**8-146*r**10+25*r**12))/40
            +(5*r**5)/(2*(-1+y)**3)+(6*r**3+65*r**5)/(4*(-1+y)**2)+(-2*r+24*r**3
            +105*r**5)/(2*(-1+y))-2*r*(-1+3*r**2+5*r**4)*y+(r*y**2)/2+r**3*y**3
            -(r*(2-6*r**2+5*r**4)*y**4)/8-(2*r*y**5)/5-(3*r*(-2+10*r**2+25*r**4)*math.log((1
            -y)/r**2))/2)
    if (dEl == 0 and dr == 1 and i==4):
        return     (-1/120*(r*(528-6279*r**2-1980*r**4+3950*r**6-1500*r**8+657*r**10-206*r**12
            +30*r**14))+(5*r**5)/(4*(-1+y)**3)+(3*r**3+40*r**5)/(4*(-1+y)**2)+(
            -r+15*r**3+85*r**5)/(2*(-1+y))-(3*r*(-2+10*r**2+25*r**4)*y)/4-(r*(
            -1+3*r**2+5*r**4)*y**2)/2+(r*y**3)/6+(3*r**3*y**4)/8-(r*(2-6*r**2+5*r**4)*y**5)/20
            -(r*y**6)/6-(r*(-4+27*r**2+90*r**4)*math.log((1-y)/r**2))/2)
    return 0. 

@jit(float64(int64, float64, float64, int64, int64), cache=True, nopython=True)
def XD(i,elcuthat,r,dEl,dr):
    """ Tree level functions (mupi) for El moments and their derivatives """
    y  = 2*elcuthat
    logy = math.log((1-y)/r**2)
    # tree level function
    if (dEl == 0 and dr == 0 and i==0):
        return     (-2*logy*(4+3*r**4)+(77-104*r**2+22*r**4-4*r**6-5*r**8)/6+(8*r**6)/(3*(
            -1+y)**5)+(2*(r**4+3*r**6))/(-1+y)**4+(2*(3*r**4+4*r**6))/(3*(-1+y)**3)
            +(-8*r**2-17*r**4-4*r**6)/(3*(-1+y)**2)-(2*(8*r**2+9*r**4))/(3*(-1
            +y))-(8*(3+r**4)*y)/3+(4*(-3+2*r**2)*y**2)/3+(8*y**3)/3+y**4/6)
    if (dEl == 0 and dr == 0 and i==1):
        return     ((4*logy*(-3+2*r**2))/3+(327-910*r**2+270*r**4-150*r**6-35*r**8+18*r**10)/45
            +(4*r**6)/(3*(-1+y)**5)+(3*r**4+14*r**6)/(3*(-1+y)**4)+(7*r**4+16*r**6)/(3*(
            -1+y)**3)+(4*(-r**2-r**4+r**6))/(3*(-1+y)**2)-(2*(8*r**2+13*r**4
            +2*r**6))/(3*(-1+y))-(4+3*r**4)*y-(2*(3+r**4)*y**2)/3+(4*(-3+2*r**2)*y**3)/9
            +y**4+y**5/15)
    if (dEl == 0 and dr == 0 and i==2):
        return     ((logy*(-6+12*r**2+13*r**4+2*r**6))/3+(678-3330*r**2+1360*r**4-530*r**6
            +30*r**8+122*r**10-35*r**12)/180+(2*r**6)/(3*(-1+y)**5)+(3*r**4+19*r**6)/(6*(
            -1+y)**4)+(33*r**4+104*r**6)/(18*(-1+y)**3)+(-8*r**2+13*r**4+56*r**6)/(12*(
            -1+y)**2)+(-12*r**2-17*r**4+2*r**6)/(3*(-1+y))+(2*(-3+2*r**2)*y)/3
            -((4+3*r**4)*y**2)/4-(2*(3+r**4)*y**3)/9+((-3+2*r**2)*y**4)/6+(2*y**5)/5
            +y**6/36)
    if (dEl == 0 and dr == 0 and i==3):
        return     (logy*(1+r**2)*(-1+5*r**2)+(779-6216*r**2+4165*r**4-700*r**6+525*r**8
            +196*r**10-189*r**12+40*r**14)/420+r**6/(3*(-1+y)**5)+(r**4+8*r**6)/(4*(
            -1+y)**4)+(5*(r**4+4*r**6))/(4*(-1+y)**3)+(-4*r**2+23*r**4+80*r**6)/(12*(
            -1+y)**2)+(-32*r**2-21*r**4+60*r**6)/(12*(-1+y))+((-6+12*r**2+13*r**4
            +2*r**6)*y)/6+((-3+2*r**2)*y**2)/6-((4+3*r**4)*y**3)/12-((3+r**4)*y**4)/12
            +((-3+2*r**2)*y**5)/15+y**6/6+y**7/84)
    if (dEl == 0 and dr == 0 and i==4):
        return     ((logy*(-12+80*r**2+81*r**4-60*r**6))/24+(17691-218400*r**2+254142*r**4
            -8400*r**6+26950*r**8-2016*r**10-10290*r**12+5528*r**14-945*r**16)/20160
            +r**6/(6*(-1+y)**5)+(3*r**4+29*r**6)/(24*(-1+y)**4)+(19*r**4+92*r**6)/(24*(
            -1+y)**3)+(-8*r**2+91*r**4+340*r**6)/(48*(-1+y)**2)+(5*(-8*r**2+5*r**4
            +44*r**6))/(24*(-1+y))+((-1+4*r**2+5*r**4)*y)/2+((-6+12*r**2+13*r**4
            +2*r**6)*y**2)/24+((-3+2*r**2)*y**3)/18-((4+3*r**4)*y**4)/32-((3+r**4)*y**5)/30
            +((-3+2*r**2)*y**6)/36+y**7/14+y**8/192)

    # derivative wrt Elcuthat
    if (dEl == 1 and dr == 0 and i==0):
        return     ((-16*(3+r**4))/3-(80*r**6)/(3*(-1+y)**6)-(16*(r**4+3*r**6))/(-1+y)**5
            -(4*(3*r**4+4*r**6))/(-1+y)**4+(4*(8*r**2+17*r**4+4*r**6))/(3*(-1+y)**3)
            +(4*(8*r**2+9*r**4))/(3*(-1+y)**2)-(4*(4+3*r**4))/(-1+y)+(16*(-3
            +2*r**2)*y)/3+16*y**2+(4*y**3)/3)
    if (dEl == 1 and dr == 0 and i==1):
        return     (-2*(4+3*r**4)-(40*r**6)/(3*(-1+y)**6)-(8*(3*r**4+14*r**6))/(3*(-1+y)**5)
            -(2*(7*r**4+16*r**6))/(-1+y)**4-(16*(-r**2-r**4+r**6))/(3*(-1+y)**3)
            +(4*(8*r**2+13*r**4+2*r**6))/(3*(-1+y)**2)+(8*(-3+2*r**2))/(3*(-1
            +y))-(8*(3+r**4)*y)/3+(8*(-3+2*r**2)*y**2)/3+8*y**3+(2*y**4)/3)
    if (dEl == 1 and dr == 0 and i==2):
        return     ((4*(-3+2*r**2))/3-(20*r**6)/(3*(-1+y)**6)-(4*(3*r**4+19*r**6))/(3*(
            -1+y)**5)+(-33*r**4-104*r**6)/(3*(-1+y)**4)+(8*r**2-13*r**4-56*r**6)/(3*(
            -1+y)**3)-(2*(-12*r**2-17*r**4+2*r**6))/(3*(-1+y)**2)+(2*(-6+12*r**2
            +13*r**4+2*r**6))/(3*(-1+y))-(4+3*r**4)*y-(4*(3+r**4)*y**2)/3+(4*(
            -3+2*r**2)*y**3)/3+4*y**4+y**5/3)
    if (dEl == 1 and dr == 0 and i==3):
        return     ((-6+12*r**2+13*r**4+2*r**6)/3-(10*r**6)/(3*(-1+y)**6)-(2*(r**4+8*r**6))/(
            -1+y)**5-(15*(r**4+4*r**6))/(2*(-1+y)**4)+(4*r**2-23*r**4-80*r**6)/(3*(
            -1+y)**3)+(32*r**2+21*r**4-60*r**6)/(6*(-1+y)**2)+(2*(-1+4*r**2
            +5*r**4))/(-1+y)+(2*(-3+2*r**2)*y)/3-((4+3*r**4)*y**2)/2-(2*(3
            +r**4)*y**3)/3+(2*(-3+2*r**2)*y**4)/3+2*y**5+y**6/6)
    if (dEl == 1 and dr == 0 and i==4):
        return     (-1+4*r**2+5*r**4-(5*r**6)/(3*(-1+y)**6)+(-3*r**4-29*r**6)/(3*(-1+y)**5)
            +(-19*r**4-92*r**6)/(4*(-1+y)**4)+(8*r**2-91*r**4-340*r**6)/(12*(-1
            +y)**3)-(5*(-8*r**2+5*r**4+44*r**6))/(12*(-1+y)**2)+(-12+80*r**2
            +81*r**4-60*r**6)/(12*(-1+y))+((-6+12*r**2+13*r**4+2*r**6)*y)/6
            +((-3+2*r**2)*y**2)/3-((4+3*r**4)*y**3)/4-((3+r**4)*y**4)/3+((-3
            +2*r**2)*y**5)/3+y**6+y**7/12)

    # derivative wrt r
    if (dEl == 0 and dr == 1 and i==0):
        return     ((-4*(-12+26*r**2-20*r**4+3*r**6+5*r**8))/(3*r)+(16*r**5)/(-1+y)**5
            +(4*(2*r**3+9*r**5))/(-1+y)**4+(8*(r**3+2*r**5))/(-1+y)**3-(4*(4*r
            +17*r**3+6*r**5))/(3*(-1+y)**2)-(8*(4*r+9*r**3))/(3*(-1+y))-(32*r**3*y)/3
            +(16*r*y**2)/3-24*r**3*math.log((1-y)/r**2))
    if (dEl == 0 and dr == 1 and i==1):
        return     ((4*(18-103*r**2+54*r**4-45*r**6-14*r**8+9*r**10))/(9*r)+(8*r**5)/(
            -1+y)**5+(4*(r**3+7*r**5))/(-1+y)**4+(4*(7*r**3+24*r**5))/(3*(-1+y)**3)
            +(8*(-r-2*r**3+3*r**5))/(3*(-1+y)**2)-(8*(4*r+13*r**3+3*r**5))/(3*(
            -1+y))-12*r**3*y-(8*r**3*y**2)/3+(16*r*y**3)/9+(16*r*math.log((1-y)/r**2))/3)
    if (dEl == 0 and dr == 1 and i==2):
        return     (-1/9*(-36+405*r**2-194*r**4+171*r**6-12*r**8-61*r**10+21*r**12)/r
            +(4*r**5)/(-1+y)**5+(2*r**3+19*r**5)/(-1+y)**4+(2*(11*r**3+52*r**5))/(3*(
            -1+y)**3)+(-4*r+13*r**3+84*r**5)/(3*(-1+y)**2)+(4*(-6*r-17*r**3
            +3*r**5))/(3*(-1+y))+(8*r*y)/3-3*r**3*y**2-(8*r**3*y**3)/9+(2*r*y**4)/3
            +(4*r*(6+13*r**2+3*r**4)*math.log((1-y)/r**2))/3)
    if (dEl == 0 and dr == 1 and i==3):
        return     ((30-564*r**2+445*r**4-150*r**6+150*r**8+70*r**10-81*r**12+20*r**14)/(15*r)
            +(2*r**5)/(-1+y)**5+(r**3+12*r**5)/(-1+y)**4+(5*(r**3+6*r**5))/(-1
            +y)**3+(-2*r+23*r**3+120*r**5)/(3*(-1+y)**2)+(-16*r-21*r**3+90*r**5)/(3*(
            -1+y))+(2*r*(6+13*r**2+3*r**4)*y)/3+(2*r*y**2)/3-r**3*y**3-(r**3*y**4)/3
            +(4*r*y**5)/15+4*r*(2+5*r**2)*math.log((1-y)/r**2))
    if (dEl == 0 and dr == 1 and i==4):
        return     (-1/360*(-360+10200*r**2-15723*r**4-900*r**6-3850*r**8+360*r**10+2205*r**12
            -1382*r**14+270*r**16)/r+r**5/(-1+y)**5+(2*r**3+29*r**5)/(4*(-1+y)**4)
            +(19*r**3+138*r**5)/(6*(-1+y)**3)+(-4*r+91*r**3+510*r**5)/(12*(-1
            +y)**2)+(5*(-4*r+5*r**3+66*r**5))/(6*(-1+y))+2*r*(2+5*r**2)*y+(r*(6
            +13*r**2+3*r**4)*y**2)/6+(2*r*y**3)/9-(3*r**3*y**4)/8-(2*r**3*y**5)/15
            +(r*y**6)/9-(r*(-40-81*r**2+90*r**4)*math.log((1-y)/r**2))/6)
    return 0. 

@jit(float64(int64, float64, float64, int64, int64), cache=True, nopython=True)
def XLS(i,elcuthat,r,dEl,dr):
    """ Tree level functions (mupi) for El moments and their derivatives """
    y  = 2*elcuthat
    logy = math.log((1-y)/r**2)
    # tree level function
    if (dEl == 0 and dr == 0 and i==0):
        return     (-6*logy*r**4+(3-8*r**2+14*r**4-20*r**6+5*r**8)/2+(2*r**6)/(-1+y)**4
            +(2*(3*r**4+4*r**6))/(3*(-1+y)**3)+(3*r**4-4*r**6)/(3*(-1+y)**2)-(6*r**4)/(
            -1+y)+(8*r**4*(-3+r**2)*y)/3+y**4/6)
    if (dEl == 0 and dr == 0 and i==1):
        return     ((3-15*r**2+15*r**4-35*r**6+15*r**8-3*r**10)/5+r**6/(-1+y)**4+(3*r**4
            +8*r**6)/(3*(-1+y)**3)+(2*(3*r**4+2*r**6))/(3*(-1+y)**2)-(2*(3*r**4
            +2*r**6))/(3*(-1+y))-3*r**4*y+(2*r**4*(-3+r**2)*y**2)/3+y**5/15)
    if (dEl == 0 and dr == 0 and i==2):
        return     ((logy*r**4*(3+2*r**2))/3+(8-54*r**2+60*r**4-114*r**6+108*r**8-42*r**10
            +7*r**12)/36+r**6/(2*(-1+y)**4)+(r**4+4*r**6)/(2*(-1+y)**3)+(21*r**4
            +32*r**6)/(12*(-1+y)**2)+(3*r**4+2*r**6)/(3*(-1+y))-(3*r**4*y**2)/4
            +(2*r**4*(-3+r**2)*y**3)/9+y**6/36)
    if (dEl == 0 and dr == 0 and i==3):
        return     ((2-14*r**2+77*r**4-35*r**6+70*r**8-42*r**10+14*r**12-2*r**14)/28
            +r**6/(4*(-1+y)**4)+(3*r**4+16*r**6)/(12*(-1+y)**3)+(15*r**4+34*r**6)/(12*(
            -1+y)**2)+(3*(3*r**4+4*r**6))/(4*(-1+y))+(r**4*(3+2*r**2)*y)/6-(r**4*y**3)/4
            +(r**4*(-3+r**2)*y**4)/12+y**7/84)
    if (dEl == 0 and dr == 0 and i==4):
        return     ((-3*logy*r**4*(3+4*r**2))/8+(5+1362*r**4-144*r**6+450*r**8-480*r**10
            +250*r**12-72*r**14+9*r**16)/320+r**6/(8*(-1+y)**4)+(3*r**4+20*r**6)/(24*(
            -1+y)**3)+(39*r**4+116*r**6)/(48*(-1+y)**2)+(57*r**4+104*r**6)/(24*(
            -1+y))+(r**4*(3+2*r**2)*y**2)/24-(3*r**4*y**4)/32+(r**4*(-3+r**2)*y**5)/30
            +y**8/192)

    # derivative wrt Elcuthat
    if (dEl == 1 and dr == 0 and i==0):
        return     ((16*r**4*(-3+r**2))/3-(16*r**6)/(-1+y)**5-(4*(3*r**4+4*r**6))/(-1+y)**4
            +(4*(-3*r**4+4*r**6))/(3*(-1+y)**3)+(12*r**4)/(-1+y)**2-(12*r**4)/(
            -1+y)+(4*y**3)/3)
    if (dEl == 1 and dr == 0 and i==1):
        return     (-6*r**4-(8*r**6)/(-1+y)**5-(2*(3*r**4+8*r**6))/(-1+y)**4-(8*(3*r**4
            +2*r**6))/(3*(-1+y)**3)+(4*(3*r**4+2*r**6))/(3*(-1+y)**2)+(8*r**4*(
            -3+r**2)*y)/3+(2*y**4)/3)
    if (dEl == 1 and dr == 0 and i==2):
        return     ((-4*r**6)/(-1+y)**5-(3*(r**4+4*r**6))/(-1+y)**4+(-21*r**4-32*r**6)/(3*(
            -1+y)**3)-(2*(3*r**4+2*r**6))/(3*(-1+y)**2)+(2*(3*r**4+2*r**6))/(3*(
            -1+y))-3*r**4*y+(4*r**4*(-3+r**2)*y**2)/3+y**5/3)
    if (dEl == 1 and dr == 0 and i==3):
        return     ((r**4*(3+2*r**2))/3-(2*r**6)/(-1+y)**5+(-3*r**4-16*r**6)/(2*(-1+y)**4)
            +(-15*r**4-34*r**6)/(3*(-1+y)**3)-(3*(3*r**4+4*r**6))/(2*(-1+y)**2)
            -(3*r**4*y**2)/2+(2*r**4*(-3+r**2)*y**3)/3+y**6/6)
    if (dEl == 1 and dr == 0 and i==4):
        return     (-(r**6/(-1+y)**5)+(-3*r**4-20*r**6)/(4*(-1+y)**4)+(-39*r**4-116*r**6)/(12*(
            -1+y)**3)+(-57*r**4-104*r**6)/(12*(-1+y)**2)-(3*(3*r**4+4*r**6))/(4*(
            -1+y))+(r**4*(3+2*r**2)*y)/6-(3*r**4*y**3)/4+(r**4*(-3+r**2)*y**4)/3
            +y**7/12)

    # derivative wrt r
    if (dEl == 0 and dr == 1 and i==0):
        return     (4*r*(-2+10*r**2-15*r**4+5*r**6)+(12*r**5)/(-1+y)**4+(8*(r**3+2*r**5))/(
            -1+y)**3-(4*(-r**3+2*r**5))/(-1+y)**2-(24*r**3)/(-1+y)+16*r**3*(
            -2+r**2)*y-24*r**3*math.log((1-y)/r**2))
    if (dEl == 0 and dr == 1 and i==1):
        return     (-6*r*(1-2*r**2+7*r**4-4*r**6+r**8)+(6*r**5)/(-1+y)**4+(4*(r**3+4*r**5))/(
            -1+y)**3+(8*(r**3+r**5))/(-1+y)**2-(8*(r**3+r**5))/(-1+y)-12*r**3*y
            +4*r**3*(-2+r**2)*y**2)
    if (dEl == 0 and dr == 1 and i==2):
        return     ((r*(-9+14*r**2-61*r**4+72*r**6-35*r**8+7*r**10))/3+(3*r**5)/(-1+y)**4
            +(2*(r**3+6*r**5))/(-1+y)**3+(7*r**3+16*r**5)/(-1+y)**2+(4*(r**3+r**5))/(
            -1+y)-3*r**3*y**2+(4*r**3*(-2+r**2)*y**3)/3+4*r**3*(1+r**2)*math.log((1
            -y)/r**2))
    if (dEl == 0 and dr == 1 and i==3):
        return     (-1/2*(r*(2-22*r**2+15*r**4-40*r**6+30*r**8-12*r**10+2*r**12))+(3*r**5)/(2*(
            -1+y)**4)+(r**3+8*r**5)/(-1+y)**3+(5*r**3+17*r**5)/(-1+y)**2+(9*(r**3
            +2*r**5))/(-1+y)+2*r**3*(1+r**2)*y-r**3*y**3+(r**3*(-2+r**2)*y**4)/2)
    if (dEl == 0 and dr == 1 and i==4):
        return     ((3*r**3*(257+4*r**2+150*r**4-200*r**6+125*r**8-42*r**10+6*r**12))/40
            +(3*r**5)/(4*(-1+y)**4)+(r**3+10*r**5)/(2*(-1+y)**3)+(13*r**3+58*r**5)/(4*(
            -1+y)**2)+(19*r**3+52*r**5)/(2*(-1+y))+(r**3*(1+r**2)*y**2)/2-(3*r**3*y**4)/8
            +(r**3*(-2+r**2)*y**5)/5-(9*r**3*(1+2*r**2)*math.log((1-y)/r**2))/2)
    return 0. 

def moment_1_KIN_MS(elcut, par, hqe, wc, **kwargs):
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
    flagTEST=kwargs.get('flag_TEST', 1)
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
    res +=(X(1,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0)-(rhoD*X(1,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        )
    res += ((rhoD*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)-(muG*X(1,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        )
    res += ((muG*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)-(rhoLS*X(1,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        )
    res += ((rhoLS*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)-(mupi*X(1,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        )
    res += ((mupi*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0))

    if( flagDEBUG == 1):
        print("Elmoment n. 1 LO = ",res*par.mbkin**1)

    resNLO = 0
    resNLO +=((deltambkin1*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +(deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(deltambkin1*r*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(deltamcMS1*r*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)
        -(deltambkin1*Elcuthat*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)
        -(X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
        +nlo.X1El(1,'SM',Elcuthat,r)/X(0,Elcuthat,r,0,0)+(Rhodpert1*X(1,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(Rhodpert1*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(Mupipert1*X(1,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(Mupipert1*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0))

    if( flagDEBUG == 1):
        print("Elmoment n. 1 NLO = api*",resNLO*par.mbkin**1)
    res += api*resNLO

    if(kwargs.get('flag_includeNNLO', 1) == 1):
        resNNLO = 0
        resNNLO +=((beta0*deltambkin2BLM*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(beta0*deltambkin2BLM*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(beta0*deltamcMS2BLM*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(beta0*deltambkin2BLM*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(beta0*deltambkin2BLM*r*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)
            +(beta0*deltamcMS2BLM*r*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)
            -(beta0*deltambkin2BLM*Elcuthat*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)
            -(beta0*math.log(mus**2)*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/(4*X(0,Elcuthat,r,0,0)**2)
            +(beta0*math.log(mus**2)*nlo.X1El(1,'SM',Elcuthat,r))/(4*X(0,Elcuthat,r,0,0))
            -(beta0*X(1,Elcuthat,r,0,0)*nnlo.X2ElBLM(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(beta0*nnlo.X2ElBLM(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)+(beta0*Rhodpert2BLM*X(1,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(beta0*Rhodpert2BLM*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)
            +(beta0*Mupipert2BLM*X(1,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(beta0*Mupipert2BLM*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0))
        if( flagDEBUG == 1):
            print("Elmoment n. 1 NNLO BLM = api^2*beta0*",resNNLO/beta0*par.mbkin**1)
        res += api**2*resNNLO

        resNNLO = 0
        resNNLO +=((deltamcMS2-beta0*deltamcMS2BLM)*(-((r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2)
            +(r*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0))+deltamcMS1**2*((r**2*X(0,Elcuthat,r,0,1)**2*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(r**2*X(0,Elcuthat,r,0,2)*X(1,Elcuthat,r,0,0))/(2*X(0,Elcuthat,r,0,0)**2)
            -(r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(r**2*X(1,Elcuthat,r,0,2))/(2*X(0,Elcuthat,r,0,0)))+(deltambkin2
            -beta0*deltambkin2BLM)*(X(1,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0)
            +(r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(r*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)-(Elcuthat*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0))
            +deltambkin1**2*((r**2*X(0,Elcuthat,r,0,1)**2*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(r**2*X(0,Elcuthat,r,0,2)*X(1,Elcuthat,r,0,0))/(2*X(0,Elcuthat,r,0,0)**2)
            +(2*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(Elcuthat**2*X(0,Elcuthat,r,1,0)**2*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(Elcuthat*r*X(0,Elcuthat,r,1,1)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat**2*X(0,Elcuthat,r,2,0)*X(1,Elcuthat,r,0,0))/(2*X(0,Elcuthat,r,0,0)**2)
            -(r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*r*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(r**2*X(1,Elcuthat,r,0,2))/(2*X(0,Elcuthat,r,0,0))-(Elcuthat*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat**2*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*r*X(1,Elcuthat,r,1,1))/X(0,Elcuthat,r,0,0)+(Elcuthat**2*X(1,Elcuthat,r,2,0))/(2*X(0,Elcuthat,r,0,0)))
            +(math.log(mus**2)*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/(6*X(0,Elcuthat,r,0,0)**2)
            +(X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)**2)/X(0,Elcuthat,r,0,0)**3
            -(math.log(mus**2)*nlo.X1El(1,'SM',Elcuthat,r))/(6*X(0,Elcuthat,r,0,0))-(nlo.X1El(0,'SM',Elcuthat,r)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +deltamcMS1*((r*nlo.X1El_Derivativer(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)-(r*nlo.X1El_Derivativer(0,Elcuthat,r)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(r*X(1,Elcuthat,r,0,1)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(r*X(0,Elcuthat,r,0,1)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2)
            +deltambkin1*(-((Elcuthat*nlo.X1El_DerivativeEl(1,Elcuthat,r))/X(0,Elcuthat,r,0,0))
            -(r*nlo.X1El_Derivativer(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)+(Elcuthat*nlo.X1El_DerivativeEl(0,Elcuthat,r)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r*nlo.X1El_Derivativer(0,Elcuthat,r)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +deltamcMS1*((-2*r**2*X(0,Elcuthat,r,0,1)**2*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(r**2*X(0,Elcuthat,r,0,2)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(Elcuthat*r*X(0,Elcuthat,r,1,1)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*r*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(r**2*X(1,Elcuthat,r,0,2))/X(0,Elcuthat,r,0,0)+(Elcuthat*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*r*X(1,Elcuthat,r,1,1))/X(0,Elcuthat,r,0,0))-(X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(2*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(2*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(r*X(1,Elcuthat,r,0,1)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*X(1,Elcuthat,r,1,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +nlo.X1El(1,'SM',Elcuthat,r)/X(0,Elcuthat,r,0,0)+(r*X(0,Elcuthat,r,0,1)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*X(0,Elcuthat,r,1,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2)
            -(X(1,Elcuthat,r,0,0)*flagTEST*nnlo.X2ElnonBLM(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +flagTEST*nnlo.X2ElnonBLM(1,Elcuthat,r)/X(0,Elcuthat,r,0,0)+(Rhodpert2-beta0*Rhodpert2BLM)*((X(1,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -XD(1,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0))+Rhodpert1*(-1/6*(math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(math.log(mus**2/r**2)*XD(1,Elcuthat,r,0,0))/(6*X(0,Elcuthat,r,0,0)))
            +deltamcMS1*Rhodpert1*((-2*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(r*X(1,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r*X(1,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(r*X(0,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(r*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0))+deltambkin1*Rhodpert1*((
            -2*X(1,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(r*X(1,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*X(1,Elcuthat,r,1,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(r*X(1,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*X(1,Elcuthat,r,0,0)*XD(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(2*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)-(r*X(0,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*X(0,Elcuthat,r,1,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(Elcuthat*XD(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0))
            +(Mupipert2-beta0*Mupipert2BLM)*((X(1,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -Xpi(1,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0))+Mupipert1*(-1/6*(math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(math.log(mus**2/r**2)*Xpi(1,Elcuthat,r,0,0))/(6*X(0,Elcuthat,r,0,0)))
            +deltamcMS1*Mupipert1*((-2*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(r*X(1,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r*X(1,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(r*X(0,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(r*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0))+deltambkin1*Mupipert1*(
            -((X(1,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2)
            +(2*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(r*X(1,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*X(1,Elcuthat,r,1,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(r*X(1,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*X(1,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +Xpi(1,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0)-(r*X(0,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*X(0,Elcuthat,r,1,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(Elcuthat*Xpi(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)))
        resNNLO += nnlo.fitElNNLOnonBLM(1, Elcuthat, r)*flagNONBLM*flagTEST
        if( flagDEBUG == 1):
            print("Elmoment n. 1 NNLO non-BLM = api^2*",resNNLO*par.mbkin**1)
        res += api**2*resNNLO

    if(kwargs.get('flag_includeNLOpw', 1) == 1):
        resNLO = 0
        resNLO +=(flagNLORhoD*rhoD*(-((X(1,Elcuthat,r,0,0)*nlopw.X1ElRhoD(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2)
            +nlopw.X1ElRhoD(1,Elcuthat,r)/X(0,Elcuthat,r,0,0)+(2*deltambkin1*X(1,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(FLAGcD*X(1,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*r*X(1,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(1,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(1,Elcuthat,r,1,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(nlo.X1El(1,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*r*X(1,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(1,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*XD(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(2*deltambkin1*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(FLAGcD*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)
            +(deltambkin1*r*X(0,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(0,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(nlo.X1El(0,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltambkin1*r*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(deltamcMS1*r*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)
            -(deltambkin1*Elcuthat*XD(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0))
            +flagNLOMuG*muG*(-((X(1,Elcuthat,r,0,0)*nlopw.X1ElMuG(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2)
            +nlopw.X1ElMuG(1,Elcuthat,r)/X(0,Elcuthat,r,0,0)+(deltambkin1*X(1,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(FLAGcf*X(1,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*r*X(1,Elcuthat,r,0,1)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(1,Elcuthat,r,0,1)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(1,Elcuthat,r,1,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(nlo.X1El(1,'SM',Elcuthat,r)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*r*X(1,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(1,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*XG(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(deltambkin1*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(FLAGcf*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)
            +(deltambkin1*r*X(0,Elcuthat,r,0,1)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(0,Elcuthat,r,0,1)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(nlo.X1El(0,'SM',Elcuthat,r)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltambkin1*r*XG(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(deltamcMS1*r*XG(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)
            -(deltambkin1*Elcuthat*XG(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0))
            +flagNLORhoLS*rhoLS*(-((X(1,Elcuthat,r,0,0)*nlopw.X1ElRhoLS(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2)
            +nlopw.X1ElRhoLS(1,Elcuthat,r)/X(0,Elcuthat,r,0,0)+(2*deltambkin1*X(1,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(FLAGcs*X(1,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*r*X(1,Elcuthat,r,0,1)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(1,Elcuthat,r,0,1)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(1,Elcuthat,r,1,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(nlo.X1El(1,'SM',Elcuthat,r)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*r*X(1,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(1,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(2*deltambkin1*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(FLAGcs*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)
            +(deltambkin1*r*X(0,Elcuthat,r,0,1)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(0,Elcuthat,r,0,1)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(nlo.X1El(0,'SM',Elcuthat,r)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltambkin1*r*XLS(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(deltamcMS1*r*XLS(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)
            -(deltambkin1*Elcuthat*XLS(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0))
            +flagNLOMuPi*mupi*(-((X(1,Elcuthat,r,0,0)*nlopw.X1ElMuPi(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2)
            +nlopw.X1ElMuPi(1,Elcuthat,r)/X(0,Elcuthat,r,0,0)+(deltambkin1*X(1,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*r*X(1,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(1,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(1,Elcuthat,r,1,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(nlo.X1El(1,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*r*X(1,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(1,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(deltambkin1*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(deltambkin1*r*X(0,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(0,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(nlo.X1El(0,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltambkin1*r*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(deltamcMS1*r*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)
            -(deltambkin1*Elcuthat*Xpi(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)))
        if( flagDEBUG == 1):
            print("Elmoment n. 1 NLO pw = api*",resNLO*par.mbkin**1)
        res += api*resNLO

        resNNLO = 0
        resNNLO +=(flagNLORhoD*((Rhodpert1*X(1,Elcuthat,r,0,0)*nlopw.X1ElRhoD(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(Rhodpert1*nlopw.X1ElRhoD(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)+(FLAGcD*Rhodpert1*X(1,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*Rhodpert1*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(Rhodpert1*nlo.X1El(1,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(FLAGcD*Rhodpert1*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(Rhodpert1*nlo.X1El(0,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2)
            +flagNLOMuPi*((Mupipert1*X(1,Elcuthat,r,0,0)*nlopw.X1ElMuPi(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(Mupipert1*nlopw.X1ElMuPi(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)-(2*Mupipert1*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(Mupipert1*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(Mupipert1*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2))
        if( flagDEBUG == 1):
            print("Elmoment n. 1 NNLO from NLO pw = api^2*",resNNLO*par.mbkin**1)
        res += api**2*resNNLO

    return res*par.mbkin**1


def moment_2_KIN_MS(elcut, par, hqe, wc, **kwargs):
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
    flagTEST=kwargs.get('flag_TEST', 1)
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
    res +=(-(X(1,Elcuthat,r,0,0)**2/X(0,Elcuthat,r,0,0)**2)+X(2,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0)
        +(2*rhoD*X(1,Elcuthat,r,0,0)**2*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(rhoD*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(2*rhoD*X(1,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        )
    res += ((rhoD*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(2*muG*X(1,Elcuthat,r,0,0)**2*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(muG*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(2*muG*X(1,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        )
    res += ((muG*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(2*rhoLS*X(1,Elcuthat,r,0,0)**2*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(rhoLS*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(2*rhoLS*X(1,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        )
    res += ((rhoLS*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(2*mupi*X(1,Elcuthat,r,0,0)**2*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(mupi*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(2*mupi*X(1,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        )
    res += ((mupi*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0))

    if( flagDEBUG == 1):
        print("Elmoment n. 2 LO = ",res*par.mbkin**2)

    resNLO = 0
    resNLO +=((-2*deltambkin1*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**2-(2*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
        +(2*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
        -(2*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
        +(2*deltambkin1*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
        -(2*deltamcMS1*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
        +(2*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
        +(2*deltambkin1*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(deltambkin1*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +(deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(deltambkin1*r*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(deltamcMS1*r*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)
        -(deltambkin1*Elcuthat*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)
        +(2*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
        -(X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
        -(2*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
        +nlo.X1El(2,'SM',Elcuthat,r)/X(0,Elcuthat,r,0,0)-(2*Rhodpert1*X(1,Elcuthat,r,0,0)**2*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        +(Rhodpert1*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +(2*Rhodpert1*X(1,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(Rhodpert1*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)-(2*Mupipert1*X(1,Elcuthat,r,0,0)**2*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        +(Mupipert1*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +(2*Mupipert1*X(1,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(Mupipert1*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0))

    if( flagDEBUG == 1):
        print("Elmoment n. 2 NLO = api*",resNLO*par.mbkin**2)
    res += api*resNLO

    if(kwargs.get('flag_includeNNLO', 1) == 1):
        resNNLO = 0
        resNNLO +=((-2*beta0*deltambkin2BLM*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**2
            -(2*beta0*deltambkin2BLM*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
            +(2*beta0*deltamcMS2BLM*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
            -(2*beta0*deltambkin2BLM*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
            +(2*beta0*deltambkin2BLM*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(2*beta0*deltamcMS2BLM*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(2*beta0*deltambkin2BLM*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(2*beta0*deltambkin2BLM*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)
            +(beta0*deltambkin2BLM*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(beta0*deltamcMS2BLM*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(beta0*deltambkin2BLM*Elcuthat*X(0,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(beta0*deltambkin2BLM*r*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)
            +(beta0*deltamcMS2BLM*r*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)
            -(beta0*deltambkin2BLM*Elcuthat*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)
            +(beta0*math.log(mus**2)*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r))/(2*X(0,Elcuthat,r,0,0)**3)
            -(beta0*math.log(mus**2)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/(4*X(0,Elcuthat,r,0,0)**2)
            -(beta0*math.log(mus**2)*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/(2*X(0,Elcuthat,r,0,0)**2)
            +(beta0*math.log(mus**2)*nlo.X1El(2,'SM',Elcuthat,r))/(4*X(0,Elcuthat,r,0,0))
            +(2*beta0*X(1,Elcuthat,r,0,0)**2*nnlo.X2ElBLM(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(beta0*X(2,Elcuthat,r,0,0)*nnlo.X2ElBLM(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(2*beta0*X(1,Elcuthat,r,0,0)*nnlo.X2ElBLM(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(beta0*nnlo.X2ElBLM(2,Elcuthat,r))/X(0,Elcuthat,r,0,0)-(2*beta0*Rhodpert2BLM*X(1,Elcuthat,r,0,0)**2*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(beta0*Rhodpert2BLM*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*beta0*Rhodpert2BLM*X(1,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(beta0*Rhodpert2BLM*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)
            -(2*beta0*Mupipert2BLM*X(1,Elcuthat,r,0,0)**2*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(beta0*Mupipert2BLM*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*beta0*Mupipert2BLM*X(1,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(beta0*Mupipert2BLM*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0))
        if( flagDEBUG == 1):
            print("Elmoment n. 2 NNLO BLM = api^2*beta0*",resNNLO/beta0*par.mbkin**2)
        res += api**2*resNNLO

        resNNLO = 0
        resNNLO +=((deltamcMS2-beta0*deltamcMS2BLM)*((2*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
            -(2*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0))+deltamcMS1**2*((
            -3*r**2*X(0,Elcuthat,r,0,1)**2*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**4
            +(r**2*X(0,Elcuthat,r,0,2)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
            +(4*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(r**2*X(1,Elcuthat,r,0,1)**2)/X(0,Elcuthat,r,0,0)**2-(r**2*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,2))/X(0,Elcuthat,r,0,0)**2
            +(r**2*X(0,Elcuthat,r,0,1)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(r**2*X(0,Elcuthat,r,0,2)*X(2,Elcuthat,r,0,0))/(2*X(0,Elcuthat,r,0,0)**2)
            -(r**2*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(r**2*X(2,Elcuthat,r,0,2))/(2*X(0,Elcuthat,r,0,0)))+(deltambkin2
            -beta0*deltambkin2BLM)*((-2*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**2
            -(2*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
            -(2*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
            +(2*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(2*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*X(0,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(r*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)-(Elcuthat*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0))
            +deltambkin1**2*(-(X(1,Elcuthat,r,0,0)**2/X(0,Elcuthat,r,0,0)**2)
            -(2*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
            -(3*r**2*X(0,Elcuthat,r,0,1)**2*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**4
            +(r**2*X(0,Elcuthat,r,0,2)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
            -(2*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
            -(6*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**4
            -(3*Elcuthat**2*X(0,Elcuthat,r,1,0)**2*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**4
            +(2*Elcuthat*r*X(0,Elcuthat,r,1,1)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
            +(Elcuthat**2*X(0,Elcuthat,r,2,0)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
            +(2*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(4*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(4*Elcuthat*r*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(r**2*X(1,Elcuthat,r,0,1)**2)/X(0,Elcuthat,r,0,0)**2-(r**2*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,2))/X(0,Elcuthat,r,0,0)**2
            +(2*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(4*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(4*Elcuthat**2*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(2*Elcuthat*r*X(1,Elcuthat,r,0,1)*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat**2*X(1,Elcuthat,r,1,0)**2)/X(0,Elcuthat,r,0,0)**2-(2*Elcuthat*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,1))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat**2*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,2,0))/X(0,Elcuthat,r,0,0)**2
            +X(2,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0)+(r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r**2*X(0,Elcuthat,r,0,1)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(r**2*X(0,Elcuthat,r,0,2)*X(2,Elcuthat,r,0,0))/(2*X(0,Elcuthat,r,0,0)**2)
            +(Elcuthat*X(0,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(0,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(Elcuthat**2*X(0,Elcuthat,r,1,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(Elcuthat*r*X(0,Elcuthat,r,1,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat**2*X(0,Elcuthat,r,2,0)*X(2,Elcuthat,r,0,0))/(2*X(0,Elcuthat,r,0,0)**2)
            -(r*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)-(r**2*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*r*X(0,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(r**2*X(2,Elcuthat,r,0,2))/(2*X(0,Elcuthat,r,0,0))-(Elcuthat*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)
            -(Elcuthat*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat**2*X(0,Elcuthat,r,1,0)*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*r*X(2,Elcuthat,r,1,1))/X(0,Elcuthat,r,0,0)+(Elcuthat**2*X(2,Elcuthat,r,2,0))/(2*X(0,Elcuthat,r,0,0)))
            -(math.log(mus**2)*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r))/(3*X(0,Elcuthat,r,0,0)**3)
            +(math.log(mus**2)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/(6*X(0,Elcuthat,r,0,0)**2)
            -(3*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r)**2)/X(0,Elcuthat,r,0,0)**4
            +(X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)**2)/X(0,Elcuthat,r,0,0)**3
            +(math.log(mus**2)*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/(3*X(0,Elcuthat,r,0,0)**2)
            +(4*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -nlo.X1El(1,'SM',Elcuthat,r)**2/X(0,Elcuthat,r,0,0)**2-(math.log(mus**2)*nlo.X1El(2,'SM',Elcuthat,r))/(6*X(0,Elcuthat,r,0,0))
            -(nlo.X1El(0,'SM',Elcuthat,r)*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +deltamcMS1*((r*nlo.X1El_Derivativer(2,Elcuthat,r))/X(0,Elcuthat,r,0,0)-(2*r*nlo.X1El_Derivativer(1,Elcuthat,r)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*r*nlo.X1El_Derivativer(0,Elcuthat,r)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
            -(r*nlo.X1El_Derivativer(0,Elcuthat,r)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(4*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(2*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(r*X(2,Elcuthat,r,0,1)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(4*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(2*r*X(1,Elcuthat,r,0,1)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(r*X(0,Elcuthat,r,0,1)*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2)
            +deltambkin1*(-((Elcuthat*nlo.X1El_DerivativeEl(2,Elcuthat,r))/X(0,Elcuthat,r,0,0))
            -(r*nlo.X1El_Derivativer(2,Elcuthat,r))/X(0,Elcuthat,r,0,0)+(2*Elcuthat*nlo.X1El_DerivativeEl(1,Elcuthat,r)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*r*nlo.X1El_Derivativer(1,Elcuthat,r)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*Elcuthat*nlo.X1El_DerivativeEl(0,Elcuthat,r)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
            -(2*r*nlo.X1El_Derivativer(0,Elcuthat,r)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
            +(Elcuthat*nlo.X1El_DerivativeEl(0,Elcuthat,r)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r*nlo.X1El_Derivativer(0,Elcuthat,r)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +deltamcMS1*((2*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
            +(6*r**2*X(0,Elcuthat,r,0,1)**2*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**4
            -(2*r**2*X(0,Elcuthat,r,0,2)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
            +(6*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**4
            -(2*Elcuthat*r*X(0,Elcuthat,r,1,1)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
            -(2*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(8*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(4*Elcuthat*r*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(2*r**2*X(1,Elcuthat,r,0,1)**2)/X(0,Elcuthat,r,0,0)**2+(2*r**2*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,2))/X(0,Elcuthat,r,0,0)**2
            -(4*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(2*Elcuthat*r*X(1,Elcuthat,r,0,1)*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(2*Elcuthat*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,1))/X(0,Elcuthat,r,0,0)**2
            -(r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*r**2*X(0,Elcuthat,r,0,1)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(r**2*X(0,Elcuthat,r,0,2)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(0,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(Elcuthat*r*X(0,Elcuthat,r,1,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(2*r**2*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*r*X(0,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(r**2*X(2,Elcuthat,r,0,2))/X(0,Elcuthat,r,0,0)+(Elcuthat*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*r*X(2,Elcuthat,r,1,1))/X(0,Elcuthat,r,0,0))+(4*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(6*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(6*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            -(4*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(4*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(2*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(2*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(2*Elcuthat*X(0,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(r*X(2,Elcuthat,r,0,1)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*X(2,Elcuthat,r,1,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(4*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(4*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(4*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(2*r*X(1,Elcuthat,r,0,1)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(2*Elcuthat*X(1,Elcuthat,r,1,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(2*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)+(r*X(0,Elcuthat,r,0,1)*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*X(0,Elcuthat,r,1,0)*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2)
            +(2*X(1,Elcuthat,r,0,0)**2*flagTEST*nnlo.X2ElnonBLM(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(X(2,Elcuthat,r,0,0)*flagTEST*nnlo.X2ElnonBLM(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(2*X(1,Elcuthat,r,0,0)*flagTEST*nnlo.X2ElnonBLM(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +flagTEST*nnlo.X2ElnonBLM(2,Elcuthat,r)/X(0,Elcuthat,r,0,0)+(Rhodpert2-beta0*Rhodpert2BLM)*((
            -2*X(1,Elcuthat,r,0,0)**2*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*X(1,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -XD(2,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0))+Rhodpert1*((math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)**2*XD(0,Elcuthat,r,0,0))/(3*X(0,Elcuthat,r,0,0)**3)
            -(math.log(mus**2/r**2)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/(6*X(0,Elcuthat,r,0,0)**2)
            -(math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/(3*X(0,Elcuthat,r,0,0)**2)
            +(math.log(mus**2/r**2)*XD(2,Elcuthat,r,0,0))/(6*X(0,Elcuthat,r,0,0)))
            +deltamcMS1*Rhodpert1*((6*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(4*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(r*X(2,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*r*X(1,Elcuthat,r,0,0)**2*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(r*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(4*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*r*X(1,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*r*X(1,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(r*X(0,Elcuthat,r,0,1)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(r*XD(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0))+deltambkin1*Rhodpert1*((2*X(1,Elcuthat,r,0,0)**2*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(4*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*Elcuthat*X(0,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(r*X(2,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*X(2,Elcuthat,r,1,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*r*X(1,Elcuthat,r,0,0)**2*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(r*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(2*Elcuthat*X(1,Elcuthat,r,0,0)**2*XD(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(Elcuthat*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(2*X(1,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*r*X(1,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*Elcuthat*X(1,Elcuthat,r,1,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*r*X(1,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(2*Elcuthat*X(1,Elcuthat,r,0,0)*XD(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +XD(2,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0)-(r*X(0,Elcuthat,r,0,1)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*X(0,Elcuthat,r,1,0)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r*XD(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(Elcuthat*XD(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0))
            +(Mupipert2-beta0*Mupipert2BLM)*((-2*X(1,Elcuthat,r,0,0)**2*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*X(1,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -Xpi(2,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0))+Mupipert1*((math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)**2*Xpi(0,Elcuthat,r,0,0))/(3*X(0,Elcuthat,r,0,0)**3)
            -(math.log(mus**2/r**2)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/(6*X(0,Elcuthat,r,0,0)**2)
            -(math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/(3*X(0,Elcuthat,r,0,0)**2)
            +(math.log(mus**2/r**2)*Xpi(2,Elcuthat,r,0,0))/(6*X(0,Elcuthat,r,0,0)))
            +deltamcMS1*Mupipert1*((6*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(4*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(r*X(2,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*r*X(1,Elcuthat,r,0,0)**2*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(r*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(4*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*r*X(1,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*r*X(1,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(r*X(0,Elcuthat,r,0,1)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(r*Xpi(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0))+deltambkin1*Mupipert1*((
            -6*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(4*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*Elcuthat*X(0,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(r*X(2,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*X(2,Elcuthat,r,1,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*r*X(1,Elcuthat,r,0,0)**2*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(r*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(2*Elcuthat*X(1,Elcuthat,r,0,0)**2*Xpi(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(Elcuthat*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(4*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*r*X(1,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*Elcuthat*X(1,Elcuthat,r,1,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*r*X(1,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(2*Elcuthat*X(1,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(r*X(0,Elcuthat,r,0,1)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*X(0,Elcuthat,r,1,0)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r*Xpi(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(Elcuthat*Xpi(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)))
        resNNLO += nnlo.fitElNNLOnonBLM(2, Elcuthat, r)*flagNONBLM*flagTEST
        if( flagDEBUG == 1):
            print("Elmoment n. 2 NNLO non-BLM = api^2*",resNNLO*par.mbkin**2)
        res += api**2*resNNLO

    if(kwargs.get('flag_includeNLOpw', 1) == 1):
        resNLO = 0
        resNLO +=(flagNLORhoD*rhoD*((2*X(1,Elcuthat,r,0,0)**2*nlopw.X1ElRhoD(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(X(2,Elcuthat,r,0,0)*nlopw.X1ElRhoD(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(2*X(1,Elcuthat,r,0,0)*nlopw.X1ElRhoD(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +nlopw.X1ElRhoD(2,Elcuthat,r)/X(0,Elcuthat,r,0,0)-(2*deltambkin1*X(1,Elcuthat,r,0,0)**2*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*FLAGcD*X(1,Elcuthat,r,0,0)**2*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(6*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(4*deltambkin1*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*deltamcMS1*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(FLAGcD*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*r*X(2,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(2,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(2,Elcuthat,r,1,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(2*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(nlo.X1El(2,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*deltambkin1*r*X(1,Elcuthat,r,0,0)**2*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(2*deltamcMS1*r*X(1,Elcuthat,r,0,0)**2*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*r*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(2*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)**2*XD(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*Elcuthat*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(2*deltambkin1*X(1,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*FLAGcD*X(1,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(4*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*deltambkin1*r*X(1,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*deltamcMS1*r*X(1,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*deltambkin1*Elcuthat*X(1,Elcuthat,r,1,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*nlo.X1El(1,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*deltambkin1*r*X(1,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(2*deltamcMS1*r*X(1,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(2*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*XD(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(deltambkin1*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(FLAGcD*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)
            +(deltambkin1*r*X(0,Elcuthat,r,0,1)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(0,Elcuthat,r,0,1)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(nlo.X1El(0,'SM',Elcuthat,r)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltambkin1*r*XD(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(deltamcMS1*r*XD(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)
            -(deltambkin1*Elcuthat*XD(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0))
            +flagNLOMuG*muG*((2*X(1,Elcuthat,r,0,0)**2*nlopw.X1ElMuG(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(X(2,Elcuthat,r,0,0)*nlopw.X1ElMuG(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(2*X(1,Elcuthat,r,0,0)*nlopw.X1ElMuG(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +nlopw.X1ElMuG(2,Elcuthat,r)/X(0,Elcuthat,r,0,0)+(2*FLAGcf*X(1,Elcuthat,r,0,0)**2*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(6*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(4*deltambkin1*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*deltamcMS1*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(FLAGcf*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*r*X(2,Elcuthat,r,0,1)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(2,Elcuthat,r,0,1)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(2,Elcuthat,r,1,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(2*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(nlo.X1El(2,'SM',Elcuthat,r)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*deltambkin1*r*X(1,Elcuthat,r,0,0)**2*XG(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(2*deltamcMS1*r*X(1,Elcuthat,r,0,0)**2*XG(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*r*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(2*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)**2*XG(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*Elcuthat*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(2*FLAGcf*X(1,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(4*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*deltambkin1*r*X(1,Elcuthat,r,0,1)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*deltamcMS1*r*X(1,Elcuthat,r,0,1)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*deltambkin1*Elcuthat*X(1,Elcuthat,r,1,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*nlo.X1El(1,'SM',Elcuthat,r)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*deltambkin1*r*X(1,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(2*deltamcMS1*r*X(1,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(2*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*XG(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(FLAGcf*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(deltambkin1*r*X(0,Elcuthat,r,0,1)*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(0,Elcuthat,r,0,1)*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(nlo.X1El(0,'SM',Elcuthat,r)*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltambkin1*r*XG(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(deltamcMS1*r*XG(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)
            -(deltambkin1*Elcuthat*XG(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0))
            +flagNLORhoLS*rhoLS*((2*X(1,Elcuthat,r,0,0)**2*nlopw.X1ElRhoLS(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(X(2,Elcuthat,r,0,0)*nlopw.X1ElRhoLS(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(2*X(1,Elcuthat,r,0,0)*nlopw.X1ElRhoLS(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +nlopw.X1ElRhoLS(2,Elcuthat,r)/X(0,Elcuthat,r,0,0)-(2*deltambkin1*X(1,Elcuthat,r,0,0)**2*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*FLAGcs*X(1,Elcuthat,r,0,0)**2*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(6*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(4*deltambkin1*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*deltamcMS1*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(FLAGcs*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*r*X(2,Elcuthat,r,0,1)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(2,Elcuthat,r,0,1)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(2,Elcuthat,r,1,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(2*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(nlo.X1El(2,'SM',Elcuthat,r)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*deltambkin1*r*X(1,Elcuthat,r,0,0)**2*XLS(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(2*deltamcMS1*r*X(1,Elcuthat,r,0,0)**2*XLS(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*r*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(2*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)**2*XLS(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*Elcuthat*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(2*deltambkin1*X(1,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*FLAGcs*X(1,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(4*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*deltambkin1*r*X(1,Elcuthat,r,0,1)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*deltamcMS1*r*X(1,Elcuthat,r,0,1)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*deltambkin1*Elcuthat*X(1,Elcuthat,r,1,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*nlo.X1El(1,'SM',Elcuthat,r)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*deltambkin1*r*X(1,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(2*deltamcMS1*r*X(1,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(2*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(deltambkin1*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(FLAGcs*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)
            +(deltambkin1*r*X(0,Elcuthat,r,0,1)*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(0,Elcuthat,r,0,1)*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(nlo.X1El(0,'SM',Elcuthat,r)*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltambkin1*r*XLS(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(deltamcMS1*r*XLS(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)
            -(deltambkin1*Elcuthat*XLS(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0))
            +flagNLOMuPi*mupi*((2*X(1,Elcuthat,r,0,0)**2*nlopw.X1ElMuPi(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(X(2,Elcuthat,r,0,0)*nlopw.X1ElMuPi(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(2*X(1,Elcuthat,r,0,0)*nlopw.X1ElMuPi(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +nlopw.X1ElMuPi(2,Elcuthat,r)/X(0,Elcuthat,r,0,0)+(6*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(6*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(4*deltambkin1*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*deltamcMS1*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*r*X(2,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(2,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(2,Elcuthat,r,1,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(2*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(nlo.X1El(2,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*deltambkin1*r*X(1,Elcuthat,r,0,0)**2*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(2*deltamcMS1*r*X(1,Elcuthat,r,0,0)**2*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*r*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(2*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)**2*Xpi(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*Elcuthat*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(4*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*deltambkin1*r*X(1,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*deltamcMS1*r*X(1,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*deltambkin1*Elcuthat*X(1,Elcuthat,r,1,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*deltambkin1*r*X(1,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(2*deltamcMS1*r*X(1,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(2*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*r*X(0,Elcuthat,r,0,1)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(0,Elcuthat,r,0,1)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(nlo.X1El(0,'SM',Elcuthat,r)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltambkin1*r*Xpi(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(deltamcMS1*r*Xpi(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)
            -(deltambkin1*Elcuthat*Xpi(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)))
        if( flagDEBUG == 1):
            print("Elmoment n. 2 NLO pw = api*",resNLO*par.mbkin**2)
        res += api*resNLO

        resNNLO = 0
        resNNLO +=(flagNLORhoD*((-2*Rhodpert1*X(1,Elcuthat,r,0,0)**2*nlopw.X1ElRhoD(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(Rhodpert1*X(2,Elcuthat,r,0,0)*nlopw.X1ElRhoD(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(2*Rhodpert1*X(1,Elcuthat,r,0,0)*nlopw.X1ElRhoD(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(Rhodpert1*nlopw.X1ElRhoD(2,Elcuthat,r))/X(0,Elcuthat,r,0,0)-(2*FLAGcD*Rhodpert1*X(1,Elcuthat,r,0,0)**2*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(FLAGcD*Rhodpert1*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(6*Rhodpert1*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(2*Rhodpert1*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*Rhodpert1*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(Rhodpert1*nlo.X1El(2,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*FLAGcD*Rhodpert1*X(1,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(4*Rhodpert1*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*Rhodpert1*nlo.X1El(1,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(FLAGcD*Rhodpert1*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(Rhodpert1*nlo.X1El(0,'SM',Elcuthat,r)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2)
            +flagNLOMuPi*((-2*Mupipert1*X(1,Elcuthat,r,0,0)**2*nlopw.X1ElMuPi(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(Mupipert1*X(2,Elcuthat,r,0,0)*nlopw.X1ElMuPi(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(2*Mupipert1*X(1,Elcuthat,r,0,0)*nlopw.X1ElMuPi(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(Mupipert1*nlopw.X1ElMuPi(2,Elcuthat,r))/X(0,Elcuthat,r,0,0)+(6*Mupipert1*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(2*Mupipert1*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*Mupipert1*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(Mupipert1*nlo.X1El(2,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(4*Mupipert1*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*Mupipert1*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(Mupipert1*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2))
        if( flagDEBUG == 1):
            print("Elmoment n. 2 NNLO from NLO pw = api^2*",resNNLO*par.mbkin**2)
        res += api**2*resNNLO

    return res*par.mbkin**2


def moment_3_KIN_MS(elcut, par, hqe, wc, **kwargs):
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
    flagTEST=kwargs.get('flag_TEST', 1)
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
    res +=((2*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**3-(3*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +X(3,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0)-(6*rhoD*X(1,Elcuthat,r,0,0)**3*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
        +(6*rhoD*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(rhoD*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +(6*rhoD*X(1,Elcuthat,r,0,0)**2*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(3*rhoD*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(3*rhoD*X(1,Elcuthat,r,0,0)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        )
    res += ((rhoD*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)-(6*muG*X(1,Elcuthat,r,0,0)**3*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
        +(6*muG*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(muG*X(3,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +(6*muG*X(1,Elcuthat,r,0,0)**2*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(3*muG*X(2,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(3*muG*X(1,Elcuthat,r,0,0)*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        )
    res += ((muG*XG(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)-(6*rhoLS*X(1,Elcuthat,r,0,0)**3*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
        +(6*rhoLS*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(rhoLS*X(3,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +(6*rhoLS*X(1,Elcuthat,r,0,0)**2*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(3*rhoLS*X(2,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(3*rhoLS*X(1,Elcuthat,r,0,0)*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        )
    res += ((rhoLS*XLS(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)-(6*mupi*X(1,Elcuthat,r,0,0)**3*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
        +(6*mupi*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(mupi*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +(6*mupi*X(1,Elcuthat,r,0,0)**2*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(3*mupi*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(3*mupi*X(1,Elcuthat,r,0,0)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        )
    res += ((mupi*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0))

    if( flagDEBUG == 1):
        print("Elmoment n. 3 LO = ",res*par.mbkin**3)

    resNLO = 0
    resNLO +=((6*deltambkin1*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**3+(6*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**4
        -(6*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**4
        +(6*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**4
        -(6*deltambkin1*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
        +(6*deltamcMS1*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
        -(6*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
        -(9*deltambkin1*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(6*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        +(6*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(6*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        +(3*deltambkin1*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(3*deltamcMS1*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +(3*deltambkin1*Elcuthat*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +(3*deltambkin1*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
        -(3*deltamcMS1*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
        +(3*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
        +(3*deltambkin1*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(deltambkin1*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +(deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(deltambkin1*r*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(deltamcMS1*r*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)
        -(deltambkin1*Elcuthat*X(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)
        -(6*X(1,Elcuthat,r,0,0)**3*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
        +(6*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
        -(X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
        +(6*X(1,Elcuthat,r,0,0)**2*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
        -(3*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
        -(3*X(1,Elcuthat,r,0,0)*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
        +nlo.X1El(3,'SM',Elcuthat,r)/X(0,Elcuthat,r,0,0)+(6*Rhodpert1*X(1,Elcuthat,r,0,0)**3*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
        -(6*Rhodpert1*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        +(Rhodpert1*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(6*Rhodpert1*X(1,Elcuthat,r,0,0)**2*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        +(3*Rhodpert1*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +(3*Rhodpert1*X(1,Elcuthat,r,0,0)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(Rhodpert1*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(6*Mupipert1*X(1,Elcuthat,r,0,0)**3*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
        -(6*Mupipert1*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        +(Mupipert1*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(6*Mupipert1*X(1,Elcuthat,r,0,0)**2*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        +(3*Mupipert1*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +(3*Mupipert1*X(1,Elcuthat,r,0,0)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(Mupipert1*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0))

    if( flagDEBUG == 1):
        print("Elmoment n. 3 NLO = api*",resNLO*par.mbkin**3)
    res += api*resNLO

    if(kwargs.get('flag_includeNNLO', 1) == 1):
        resNNLO = 0
        resNNLO +=((6*beta0*deltambkin2BLM*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**3
            +(6*beta0*deltambkin2BLM*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**4
            -(6*beta0*deltamcMS2BLM*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**4
            +(6*beta0*deltambkin2BLM*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**4
            -(6*beta0*deltambkin2BLM*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(6*beta0*deltamcMS2BLM*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(6*beta0*deltambkin2BLM*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(9*beta0*deltambkin2BLM*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*beta0*deltambkin2BLM*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*beta0*deltamcMS2BLM*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*beta0*deltambkin2BLM*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*beta0*deltambkin2BLM*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(3*beta0*deltamcMS2BLM*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*beta0*deltambkin2BLM*Elcuthat*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*beta0*deltambkin2BLM*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(3*beta0*deltamcMS2BLM*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(3*beta0*deltambkin2BLM*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(3*beta0*deltambkin2BLM*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)
            +(beta0*deltambkin2BLM*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(beta0*deltamcMS2BLM*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(beta0*deltambkin2BLM*Elcuthat*X(0,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(beta0*deltambkin2BLM*r*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)
            +(beta0*deltamcMS2BLM*r*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)
            -(beta0*deltambkin2BLM*Elcuthat*X(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)
            -(3*beta0*math.log(mus**2)*X(1,Elcuthat,r,0,0)**3*nlo.X1El(0,'SM',Elcuthat,r))/(2*X(0,Elcuthat,r,0,0)**4)
            +(3*beta0*math.log(mus**2)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/(2*X(0,Elcuthat,r,0,0)**3)
            -(beta0*math.log(mus**2)*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/(4*X(0,Elcuthat,r,0,0)**2)
            +(3*beta0*math.log(mus**2)*X(1,Elcuthat,r,0,0)**2*nlo.X1El(1,'SM',Elcuthat,r))/(2*X(0,Elcuthat,r,0,0)**3)
            -(3*beta0*math.log(mus**2)*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/(4*X(0,Elcuthat,r,0,0)**2)
            -(3*beta0*math.log(mus**2)*X(1,Elcuthat,r,0,0)*nlo.X1El(2,'SM',Elcuthat,r))/(4*X(0,Elcuthat,r,0,0)**2)
            +(beta0*math.log(mus**2)*nlo.X1El(3,'SM',Elcuthat,r))/(4*X(0,Elcuthat,r,0,0))
            -(6*beta0*X(1,Elcuthat,r,0,0)**3*nnlo.X2ElBLM(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(6*beta0*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nnlo.X2ElBLM(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(beta0*X(3,Elcuthat,r,0,0)*nnlo.X2ElBLM(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(6*beta0*X(1,Elcuthat,r,0,0)**2*nnlo.X2ElBLM(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(3*beta0*X(2,Elcuthat,r,0,0)*nnlo.X2ElBLM(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(3*beta0*X(1,Elcuthat,r,0,0)*nnlo.X2ElBLM(2,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(beta0*nnlo.X2ElBLM(3,Elcuthat,r))/X(0,Elcuthat,r,0,0)+(6*beta0*Rhodpert2BLM*X(1,Elcuthat,r,0,0)**3*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*beta0*Rhodpert2BLM*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(beta0*Rhodpert2BLM*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*beta0*Rhodpert2BLM*X(1,Elcuthat,r,0,0)**2*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*beta0*Rhodpert2BLM*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*beta0*Rhodpert2BLM*X(1,Elcuthat,r,0,0)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(beta0*Rhodpert2BLM*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)
            +(6*beta0*Mupipert2BLM*X(1,Elcuthat,r,0,0)**3*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*beta0*Mupipert2BLM*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(beta0*Mupipert2BLM*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*beta0*Mupipert2BLM*X(1,Elcuthat,r,0,0)**2*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*beta0*Mupipert2BLM*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*beta0*Mupipert2BLM*X(1,Elcuthat,r,0,0)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(beta0*Mupipert2BLM*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0))
        if( flagDEBUG == 1):
            print("Elmoment n. 3 NNLO BLM = api^2*beta0*",resNNLO/beta0*par.mbkin**3)
        res += api**2*resNNLO

        resNNLO = 0
        resNNLO +=((deltamcMS2-beta0*deltamcMS2BLM)*((-6*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**4
            +(6*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(6*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(3*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(3*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0))+deltamcMS1**2*((12*r**2*X(0,Elcuthat,r,0,1)**2*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**5
            -(3*r**2*X(0,Elcuthat,r,0,2)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**4
            -(18*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            +(6*r**2*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)**2)/X(0,Elcuthat,r,0,0)**3
            +(3*r**2*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,2))/X(0,Elcuthat,r,0,0)**3
            -(9*r**2*X(0,Elcuthat,r,0,1)**2*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(3*r**2*X(0,Elcuthat,r,0,2)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(3*r**2*X(1,Elcuthat,r,0,2)*X(2,Elcuthat,r,0,0))/(2*X(0,Elcuthat,r,0,0)**2)
            +(6*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(3*r**2*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(3*r**2*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,2))/(2*X(0,Elcuthat,r,0,0)**2)
            +(r**2*X(0,Elcuthat,r,0,1)**2*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(r**2*X(0,Elcuthat,r,0,2)*X(3,Elcuthat,r,0,0))/(2*X(0,Elcuthat,r,0,0)**2)
            -(r**2*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(r**2*X(3,Elcuthat,r,0,2))/(2*X(0,Elcuthat,r,0,0)))+(deltambkin2
            -beta0*deltambkin2BLM)*((6*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**3
            +(6*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**4
            +(6*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**4
            -(6*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(6*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(9*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*Elcuthat*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(3*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(3*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*X(0,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(r*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)-(Elcuthat*X(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0))
            +deltambkin1**2*((6*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**3
            +(12*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**4
            +(12*r**2*X(0,Elcuthat,r,0,1)**2*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**5
            -(3*r**2*X(0,Elcuthat,r,0,2)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**4
            +(12*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**4
            +(24*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**5
            +(12*Elcuthat**2*X(0,Elcuthat,r,1,0)**2*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**5
            -(6*Elcuthat*r*X(0,Elcuthat,r,1,1)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**4
            -(3*Elcuthat**2*X(0,Elcuthat,r,2,0)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(18*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(18*Elcuthat*r*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            +(6*r**2*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)**2)/X(0,Elcuthat,r,0,0)**3
            +(3*r**2*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,2))/X(0,Elcuthat,r,0,0)**3
            -(12*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(18*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            -(18*Elcuthat**2*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            +(12*Elcuthat*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(6*Elcuthat**2*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)**2)/X(0,Elcuthat,r,0,0)**3
            +(6*Elcuthat*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,1,1))/X(0,Elcuthat,r,0,0)**3
            +(3*Elcuthat**2*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,2,0))/X(0,Elcuthat,r,0,0)**3
            -(9*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(12*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(9*r**2*X(0,Elcuthat,r,0,1)**2*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(3*r**2*X(0,Elcuthat,r,0,2)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(18*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(9*Elcuthat**2*X(0,Elcuthat,r,1,0)**2*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(6*Elcuthat*r*X(0,Elcuthat,r,1,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*Elcuthat**2*X(0,Elcuthat,r,2,0)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(6*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*Elcuthat*r*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(3*r**2*X(1,Elcuthat,r,0,2)*X(2,Elcuthat,r,0,0))/(2*X(0,Elcuthat,r,0,0)**2)
            +(6*Elcuthat*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(6*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*Elcuthat**2*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(3*Elcuthat*r*X(1,Elcuthat,r,1,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(3*Elcuthat**2*X(1,Elcuthat,r,2,0)*X(2,Elcuthat,r,0,0))/(2*X(0,Elcuthat,r,0,0)**2)
            +(6*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(6*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(6*Elcuthat*r*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(3*r**2*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(3*Elcuthat*r*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(3*r**2*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,2))/(2*X(0,Elcuthat,r,0,0)**2)
            +(6*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(6*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(6*Elcuthat**2*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(3*Elcuthat*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(3*Elcuthat**2*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(3*Elcuthat*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,1,1))/X(0,Elcuthat,r,0,0)**2
            -(3*Elcuthat**2*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,2,0))/(2*X(0,Elcuthat,r,0,0)**2)
            +(3*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(2*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r**2*X(0,Elcuthat,r,0,1)**2*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(r**2*X(0,Elcuthat,r,0,2)*X(3,Elcuthat,r,0,0))/(2*X(0,Elcuthat,r,0,0)**2)
            +(2*Elcuthat*X(0,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(0,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(Elcuthat**2*X(0,Elcuthat,r,1,0)**2*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(Elcuthat*r*X(0,Elcuthat,r,1,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat**2*X(0,Elcuthat,r,2,0)*X(3,Elcuthat,r,0,0))/(2*X(0,Elcuthat,r,0,0)**2)
            -(2*r*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)-(r**2*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*r*X(0,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(r**2*X(3,Elcuthat,r,0,2))/(2*X(0,Elcuthat,r,0,0))-(2*Elcuthat*X(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)
            -(Elcuthat*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat**2*X(0,Elcuthat,r,1,0)*X(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*r*X(3,Elcuthat,r,1,1))/X(0,Elcuthat,r,0,0)+(Elcuthat**2*X(3,Elcuthat,r,2,0))/(2*X(0,Elcuthat,r,0,0)))
            +(math.log(mus**2)*X(1,Elcuthat,r,0,0)**3*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            -(math.log(mus**2)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(math.log(mus**2)*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/(6*X(0,Elcuthat,r,0,0)**2)
            +(12*X(1,Elcuthat,r,0,0)**3*nlo.X1El(0,'SM',Elcuthat,r)**2)/X(0,Elcuthat,r,0,0)**5
            -(9*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)**2)/X(0,Elcuthat,r,0,0)**4
            +(X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)**2)/X(0,Elcuthat,r,0,0)**3
            -(math.log(mus**2)*X(1,Elcuthat,r,0,0)**2*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(math.log(mus**2)*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/(2*X(0,Elcuthat,r,0,0)**2)
            -(18*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(6*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(6*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)**2)/X(0,Elcuthat,r,0,0)**3
            +(math.log(mus**2)*X(1,Elcuthat,r,0,0)*nlo.X1El(2,'SM',Elcuthat,r))/(2*X(0,Elcuthat,r,0,0)**2)
            +(6*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(3*nlo.X1El(1,'SM',Elcuthat,r)*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(math.log(mus**2)*nlo.X1El(3,'SM',Elcuthat,r))/(6*X(0,Elcuthat,r,0,0))-(nlo.X1El(0,'SM',Elcuthat,r)*nlo.X1El(3,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +deltamcMS1*((r*nlo.X1El_Derivativer(3,Elcuthat,r))/X(0,Elcuthat,r,0,0)-(3*r*nlo.X1El_Derivativer(2,Elcuthat,r)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(6*r*nlo.X1El_Derivativer(1,Elcuthat,r)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
            -(6*r*nlo.X1El_Derivativer(0,Elcuthat,r)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**4
            -(3*r*nlo.X1El_Derivativer(1,Elcuthat,r)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(6*r*nlo.X1El_Derivativer(0,Elcuthat,r)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(r*nlo.X1El_Derivativer(0,Elcuthat,r)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(24*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
            -(18*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            -(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(6*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(6*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(2*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(r*X(3,Elcuthat,r,0,1)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(6*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(3*r*X(2,Elcuthat,r,0,1)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(6*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(3*r*X(1,Elcuthat,r,0,1)*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(r*X(0,Elcuthat,r,0,1)*nlo.X1El(3,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2)
            +deltambkin1*(-((Elcuthat*nlo.X1El_DerivativeEl(3,Elcuthat,r))/X(0,Elcuthat,r,0,0))
            -(r*nlo.X1El_Derivativer(3,Elcuthat,r))/X(0,Elcuthat,r,0,0)+(3*Elcuthat*nlo.X1El_DerivativeEl(2,Elcuthat,r)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*r*nlo.X1El_Derivativer(2,Elcuthat,r)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*Elcuthat*nlo.X1El_DerivativeEl(1,Elcuthat,r)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
            -(6*r*nlo.X1El_Derivativer(1,Elcuthat,r)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
            +(6*Elcuthat*nlo.X1El_DerivativeEl(0,Elcuthat,r)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**4
            +(6*r*nlo.X1El_Derivativer(0,Elcuthat,r)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**4
            +(3*Elcuthat*nlo.X1El_DerivativeEl(1,Elcuthat,r)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*r*nlo.X1El_Derivativer(1,Elcuthat,r)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*Elcuthat*nlo.X1El_DerivativeEl(0,Elcuthat,r)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*r*nlo.X1El_Derivativer(0,Elcuthat,r)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(Elcuthat*nlo.X1El_DerivativeEl(0,Elcuthat,r)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r*nlo.X1El_Derivativer(0,Elcuthat,r)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +deltamcMS1*((-12*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**4
            -(24*r**2*X(0,Elcuthat,r,0,1)**2*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**5
            +(6*r**2*X(0,Elcuthat,r,0,2)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**4
            -(24*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**5
            +(6*Elcuthat*r*X(0,Elcuthat,r,1,1)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(36*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            +(18*Elcuthat*r*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(12*r**2*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)**2)/X(0,Elcuthat,r,0,0)**3
            -(6*r**2*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,2))/X(0,Elcuthat,r,0,0)**3
            +(18*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            -(12*Elcuthat*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(6*Elcuthat*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,1,1))/X(0,Elcuthat,r,0,0)**3
            +(12*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(18*r**2*X(0,Elcuthat,r,0,1)**2*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*r**2*X(0,Elcuthat,r,0,2)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(18*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*Elcuthat*r*X(0,Elcuthat,r,1,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(12*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*Elcuthat*r*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*r**2*X(1,Elcuthat,r,0,2)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*Elcuthat*r*X(1,Elcuthat,r,1,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(12*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(6*Elcuthat*r*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(6*r**2*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(3*Elcuthat*r*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(3*r**2*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,2))/X(0,Elcuthat,r,0,0)**2
            -(6*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(3*Elcuthat*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(3*Elcuthat*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,1,1))/X(0,Elcuthat,r,0,0)**2
            -(2*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*r**2*X(0,Elcuthat,r,0,1)**2*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(r**2*X(0,Elcuthat,r,0,2)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(0,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(Elcuthat*r*X(0,Elcuthat,r,1,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*r*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(2*r**2*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*r*X(0,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(r**2*X(3,Elcuthat,r,0,2))/X(0,Elcuthat,r,0,0)+(Elcuthat*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*r*X(3,Elcuthat,r,1,1))/X(0,Elcuthat,r,0,0))-(18*X(1,Elcuthat,r,0,0)**3*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            -(24*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
            -(24*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**3*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
            +(18*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(18*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,1,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(18*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(18*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            -(6*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(6*Elcuthat*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(6*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(6*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,1,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(3*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(2*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(2*Elcuthat*X(0,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(r*X(3,Elcuthat,r,0,1)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*X(3,Elcuthat,r,1,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(18*X(1,Elcuthat,r,0,0)**2*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(18*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(9*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(6*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(6*Elcuthat*X(0,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(3*r*X(2,Elcuthat,r,0,1)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(3*Elcuthat*X(2,Elcuthat,r,1,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(9*X(1,Elcuthat,r,0,0)*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(6*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(6*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(3*r*X(1,Elcuthat,r,0,1)*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(3*Elcuthat*X(1,Elcuthat,r,1,0)*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(3*nlo.X1El(3,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)+(r*X(0,Elcuthat,r,0,1)*nlo.X1El(3,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*X(0,Elcuthat,r,1,0)*nlo.X1El(3,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2)
            -(6*X(1,Elcuthat,r,0,0)**3*flagTEST*nnlo.X2ElnonBLM(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(6*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*flagTEST*nnlo.X2ElnonBLM(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(X(3,Elcuthat,r,0,0)*flagTEST*nnlo.X2ElnonBLM(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(6*X(1,Elcuthat,r,0,0)**2*flagTEST*nnlo.X2ElnonBLM(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(3*X(2,Elcuthat,r,0,0)*flagTEST*nnlo.X2ElnonBLM(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(3*X(1,Elcuthat,r,0,0)*flagTEST*nnlo.X2ElnonBLM(2,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +flagTEST*nnlo.X2ElnonBLM(3,Elcuthat,r)/X(0,Elcuthat,r,0,0)+(Rhodpert2-beta0*Rhodpert2BLM)*((6*X(1,Elcuthat,r,0,0)**3*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*X(1,Elcuthat,r,0,0)**2*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*X(1,Elcuthat,r,0,0)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -XD(3,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0))+Rhodpert1*(-((math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)**3*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4)
            +(math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(math.log(mus**2/r**2)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/(6*X(0,Elcuthat,r,0,0)**2)
            +(math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)**2*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(math.log(mus**2/r**2)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/(2*X(0,Elcuthat,r,0,0)**2)
            -(math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)*XD(2,Elcuthat,r,0,0))/(2*X(0,Elcuthat,r,0,0)**2)
            +(math.log(mus**2/r**2)*XD(3,Elcuthat,r,0,0))/(6*X(0,Elcuthat,r,0,0)))
            +deltamcMS1*Rhodpert1*((-24*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(18*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(r*X(3,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(6*r*X(1,Elcuthat,r,0,0)**3*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(6*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(r*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*r*X(2,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*r*X(1,Elcuthat,r,0,0)**2*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(3*r*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(6*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*r*X(1,Elcuthat,r,0,1)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*r*X(1,Elcuthat,r,0,0)*XD(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(r*X(0,Elcuthat,r,0,1)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(r*XD(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0))+deltambkin1*Rhodpert1*((24*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(24*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**3*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(18*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,1,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(6*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*Elcuthat*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,1,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*Elcuthat*X(0,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(r*X(3,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*X(3,Elcuthat,r,1,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*r*X(1,Elcuthat,r,0,0)**3*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            +(6*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(r*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(6*Elcuthat*X(1,Elcuthat,r,0,0)**3*XD(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            +(6*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(Elcuthat*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*Elcuthat*X(0,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(3*r*X(2,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(3*Elcuthat*X(2,Elcuthat,r,1,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(6*r*X(1,Elcuthat,r,0,0)**2*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(3*r*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(6*Elcuthat*X(1,Elcuthat,r,0,0)**2*XD(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(3*Elcuthat*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(6*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(3*r*X(1,Elcuthat,r,0,1)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(3*Elcuthat*X(1,Elcuthat,r,1,0)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(3*r*X(1,Elcuthat,r,0,0)*XD(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(3*Elcuthat*X(1,Elcuthat,r,0,0)*XD(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(r*X(0,Elcuthat,r,0,1)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*X(0,Elcuthat,r,1,0)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r*XD(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(Elcuthat*XD(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0))
            +(Mupipert2-beta0*Mupipert2BLM)*((6*X(1,Elcuthat,r,0,0)**3*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*X(1,Elcuthat,r,0,0)**2*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*X(1,Elcuthat,r,0,0)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -Xpi(3,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0))+Mupipert1*(-((math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)**3*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4)
            +(math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(math.log(mus**2/r**2)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/(6*X(0,Elcuthat,r,0,0)**2)
            +(math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)**2*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(math.log(mus**2/r**2)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/(2*X(0,Elcuthat,r,0,0)**2)
            -(math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)*Xpi(2,Elcuthat,r,0,0))/(2*X(0,Elcuthat,r,0,0)**2)
            +(math.log(mus**2/r**2)*Xpi(3,Elcuthat,r,0,0))/(6*X(0,Elcuthat,r,0,0)))
            +deltamcMS1*Mupipert1*((-24*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(18*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(r*X(3,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(6*r*X(1,Elcuthat,r,0,0)**3*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(6*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(r*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*r*X(2,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*r*X(1,Elcuthat,r,0,0)**2*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(3*r*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(6*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*r*X(1,Elcuthat,r,0,1)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*r*X(1,Elcuthat,r,0,0)*Xpi(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(r*X(0,Elcuthat,r,0,1)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(r*Xpi(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0))+deltambkin1*Mupipert1*((6*X(1,Elcuthat,r,0,0)**3*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(24*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(24*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**3*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(18*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,1,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(6*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*Elcuthat*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,1,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*Elcuthat*X(0,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(r*X(3,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*X(3,Elcuthat,r,1,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*r*X(1,Elcuthat,r,0,0)**3*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            +(6*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(r*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(6*Elcuthat*X(1,Elcuthat,r,0,0)**3*Xpi(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            +(6*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(Elcuthat*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(6*X(1,Elcuthat,r,0,0)**2*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(6*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*Elcuthat*X(0,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(3*r*X(2,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(3*Elcuthat*X(2,Elcuthat,r,1,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(6*r*X(1,Elcuthat,r,0,0)**2*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(3*r*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(6*Elcuthat*X(1,Elcuthat,r,0,0)**2*Xpi(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(3*Elcuthat*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(3*X(1,Elcuthat,r,0,0)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(6*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(3*r*X(1,Elcuthat,r,0,1)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(3*Elcuthat*X(1,Elcuthat,r,1,0)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(3*r*X(1,Elcuthat,r,0,0)*Xpi(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(3*Elcuthat*X(1,Elcuthat,r,0,0)*Xpi(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -Xpi(3,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0)-(r*X(0,Elcuthat,r,0,1)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*X(0,Elcuthat,r,1,0)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r*Xpi(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(Elcuthat*Xpi(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)))
        resNNLO += nnlo.fitElNNLOnonBLM(3, Elcuthat, r)*flagNONBLM*flagTEST
        if( flagDEBUG == 1):
            print("Elmoment n. 3 NNLO non-BLM = api^2*",resNNLO*par.mbkin**3)
        res += api**2*resNNLO

    if(kwargs.get('flag_includeNLOpw', 1) == 1):
        resNLO = 0
        resNLO +=(flagNLORhoD*rhoD*((-6*X(1,Elcuthat,r,0,0)**3*nlopw.X1ElRhoD(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(6*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlopw.X1ElRhoD(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(X(3,Elcuthat,r,0,0)*nlopw.X1ElRhoD(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(6*X(1,Elcuthat,r,0,0)**2*nlopw.X1ElRhoD(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(3*X(2,Elcuthat,r,0,0)*nlopw.X1ElRhoD(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(3*X(1,Elcuthat,r,0,0)*nlopw.X1ElRhoD(2,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +nlopw.X1ElRhoD(3,Elcuthat,r)/X(0,Elcuthat,r,0,0)-(6*FLAGcD*X(1,Elcuthat,r,0,0)**3*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(24*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(24*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(24*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**3*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(18*deltambkin1*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*deltamcMS1*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,1,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(6*FLAGcD*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(18*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*deltambkin1*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*deltamcMS1*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*deltambkin1*Elcuthat*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*deltambkin1*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*deltamcMS1*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,1,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(FLAGcD*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*r*X(3,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(3,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(3,Elcuthat,r,1,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(24*X(1,Elcuthat,r,0,0)**3*nlo.X1El(0,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(18*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(2*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(18*X(1,Elcuthat,r,0,0)**2*nlo.X1El(1,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(6*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*X(1,Elcuthat,r,0,0)*nlo.X1El(2,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(nlo.X1El(3,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(6*deltambkin1*r*X(1,Elcuthat,r,0,0)**3*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(6*deltamcMS1*r*X(1,Elcuthat,r,0,0)**3*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(6*deltambkin1*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(6*deltamcMS1*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*r*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(6*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)**3*XD(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            -(6*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*Elcuthat*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(6*FLAGcD*X(1,Elcuthat,r,0,0)**2*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(18*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*deltambkin1*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*deltamcMS1*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(3*FLAGcD*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*deltambkin1*r*X(2,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(3*deltamcMS1*r*X(2,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*deltambkin1*Elcuthat*X(2,Elcuthat,r,1,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(18*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(6*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(3*nlo.X1El(2,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*deltambkin1*r*X(1,Elcuthat,r,0,0)**2*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(6*deltamcMS1*r*X(1,Elcuthat,r,0,0)**2*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(3*deltambkin1*r*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(3*deltamcMS1*r*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(6*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)**2*XD(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(3*deltambkin1*Elcuthat*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(3*FLAGcD*X(1,Elcuthat,r,0,0)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*deltambkin1*r*X(1,Elcuthat,r,0,1)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(3*deltamcMS1*r*X(1,Elcuthat,r,0,1)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*deltambkin1*Elcuthat*X(1,Elcuthat,r,1,0)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(6*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(3*nlo.X1El(1,'SM',Elcuthat,r)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*deltambkin1*r*X(1,Elcuthat,r,0,0)*XD(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(3*deltamcMS1*r*X(1,Elcuthat,r,0,0)*XD(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(3*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*XD(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(FLAGcD*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(deltambkin1*r*X(0,Elcuthat,r,0,1)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(0,Elcuthat,r,0,1)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(nlo.X1El(0,'SM',Elcuthat,r)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltambkin1*r*XD(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(deltamcMS1*r*XD(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)
            -(deltambkin1*Elcuthat*XD(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0))
            +flagNLOMuG*muG*((-6*X(1,Elcuthat,r,0,0)**3*nlopw.X1ElMuG(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(6*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlopw.X1ElMuG(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(X(3,Elcuthat,r,0,0)*nlopw.X1ElMuG(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(6*X(1,Elcuthat,r,0,0)**2*nlopw.X1ElMuG(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(3*X(2,Elcuthat,r,0,0)*nlopw.X1ElMuG(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(3*X(1,Elcuthat,r,0,0)*nlopw.X1ElMuG(2,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +nlopw.X1ElMuG(3,Elcuthat,r)/X(0,Elcuthat,r,0,0)-(6*deltambkin1*X(1,Elcuthat,r,0,0)**3*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*FLAGcf*X(1,Elcuthat,r,0,0)**3*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(24*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(24*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(24*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**3*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(18*deltambkin1*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*deltamcMS1*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,1,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(6*deltambkin1*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*FLAGcf*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(18*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*deltambkin1*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*deltamcMS1*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*deltambkin1*Elcuthat*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*deltambkin1*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*deltamcMS1*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,1,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(deltambkin1*X(3,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(FLAGcf*X(3,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*r*X(3,Elcuthat,r,0,1)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(3,Elcuthat,r,0,1)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(3,Elcuthat,r,1,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(24*X(1,Elcuthat,r,0,0)**3*nlo.X1El(0,'SM',Elcuthat,r)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(18*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(2*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(18*X(1,Elcuthat,r,0,0)**2*nlo.X1El(1,'SM',Elcuthat,r)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(6*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*X(1,Elcuthat,r,0,0)*nlo.X1El(2,'SM',Elcuthat,r)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(nlo.X1El(3,'SM',Elcuthat,r)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(6*deltambkin1*r*X(1,Elcuthat,r,0,0)**3*XG(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(6*deltamcMS1*r*X(1,Elcuthat,r,0,0)**3*XG(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(6*deltambkin1*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(6*deltamcMS1*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*r*X(3,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(3,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(6*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)**3*XG(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            -(6*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*Elcuthat*X(3,Elcuthat,r,0,0)*XG(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(6*deltambkin1*X(1,Elcuthat,r,0,0)**2*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*FLAGcf*X(1,Elcuthat,r,0,0)**2*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(18*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*deltambkin1*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*deltamcMS1*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(3*deltambkin1*X(2,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(3*FLAGcf*X(2,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*deltambkin1*r*X(2,Elcuthat,r,0,1)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(3*deltamcMS1*r*X(2,Elcuthat,r,0,1)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*deltambkin1*Elcuthat*X(2,Elcuthat,r,1,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(18*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(6*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(3*nlo.X1El(2,'SM',Elcuthat,r)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*deltambkin1*r*X(1,Elcuthat,r,0,0)**2*XG(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(6*deltamcMS1*r*X(1,Elcuthat,r,0,0)**2*XG(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(3*deltambkin1*r*X(2,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(3*deltamcMS1*r*X(2,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(6*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)**2*XG(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(3*deltambkin1*Elcuthat*X(2,Elcuthat,r,0,0)*XG(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(3*deltambkin1*X(1,Elcuthat,r,0,0)*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(3*FLAGcf*X(1,Elcuthat,r,0,0)*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*deltambkin1*r*X(1,Elcuthat,r,0,1)*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(3*deltamcMS1*r*X(1,Elcuthat,r,0,1)*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*deltambkin1*Elcuthat*X(1,Elcuthat,r,1,0)*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(6*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(3*nlo.X1El(1,'SM',Elcuthat,r)*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*deltambkin1*r*X(1,Elcuthat,r,0,0)*XG(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(3*deltamcMS1*r*X(1,Elcuthat,r,0,0)*XG(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(3*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*XG(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*XG(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(FLAGcf*XG(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)
            +(deltambkin1*r*X(0,Elcuthat,r,0,1)*XG(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(0,Elcuthat,r,0,1)*XG(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*XG(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(nlo.X1El(0,'SM',Elcuthat,r)*XG(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltambkin1*r*XG(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(deltamcMS1*r*XG(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)
            -(deltambkin1*Elcuthat*XG(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0))
            +flagNLORhoLS*rhoLS*((-6*X(1,Elcuthat,r,0,0)**3*nlopw.X1ElRhoLS(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(6*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlopw.X1ElRhoLS(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(X(3,Elcuthat,r,0,0)*nlopw.X1ElRhoLS(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(6*X(1,Elcuthat,r,0,0)**2*nlopw.X1ElRhoLS(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(3*X(2,Elcuthat,r,0,0)*nlopw.X1ElRhoLS(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(3*X(1,Elcuthat,r,0,0)*nlopw.X1ElRhoLS(2,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +nlopw.X1ElRhoLS(3,Elcuthat,r)/X(0,Elcuthat,r,0,0)-(6*FLAGcs*X(1,Elcuthat,r,0,0)**3*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(24*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(24*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(24*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**3*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(18*deltambkin1*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*deltamcMS1*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,1,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(6*FLAGcs*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(18*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*deltambkin1*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*deltamcMS1*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*deltambkin1*Elcuthat*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*deltambkin1*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*deltamcMS1*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,1,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(FLAGcs*X(3,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*r*X(3,Elcuthat,r,0,1)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(3,Elcuthat,r,0,1)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(3,Elcuthat,r,1,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(24*X(1,Elcuthat,r,0,0)**3*nlo.X1El(0,'SM',Elcuthat,r)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(18*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(2*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(18*X(1,Elcuthat,r,0,0)**2*nlo.X1El(1,'SM',Elcuthat,r)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(6*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*X(1,Elcuthat,r,0,0)*nlo.X1El(2,'SM',Elcuthat,r)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(nlo.X1El(3,'SM',Elcuthat,r)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(6*deltambkin1*r*X(1,Elcuthat,r,0,0)**3*XLS(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(6*deltamcMS1*r*X(1,Elcuthat,r,0,0)**3*XLS(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(6*deltambkin1*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(6*deltamcMS1*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*r*X(3,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(3,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(6*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)**3*XLS(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            -(6*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*Elcuthat*X(3,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(6*FLAGcs*X(1,Elcuthat,r,0,0)**2*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(18*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*deltambkin1*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*deltamcMS1*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(3*FLAGcs*X(2,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*deltambkin1*r*X(2,Elcuthat,r,0,1)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(3*deltamcMS1*r*X(2,Elcuthat,r,0,1)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*deltambkin1*Elcuthat*X(2,Elcuthat,r,1,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(18*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(6*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(3*nlo.X1El(2,'SM',Elcuthat,r)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*deltambkin1*r*X(1,Elcuthat,r,0,0)**2*XLS(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(6*deltamcMS1*r*X(1,Elcuthat,r,0,0)**2*XLS(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(3*deltambkin1*r*X(2,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(3*deltamcMS1*r*X(2,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(6*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)**2*XLS(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(3*deltambkin1*Elcuthat*X(2,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(3*FLAGcs*X(1,Elcuthat,r,0,0)*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*deltambkin1*r*X(1,Elcuthat,r,0,1)*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(3*deltamcMS1*r*X(1,Elcuthat,r,0,1)*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*deltambkin1*Elcuthat*X(1,Elcuthat,r,1,0)*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(6*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(3*nlo.X1El(1,'SM',Elcuthat,r)*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*deltambkin1*r*X(1,Elcuthat,r,0,0)*XLS(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(3*deltamcMS1*r*X(1,Elcuthat,r,0,0)*XLS(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(3*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*XLS(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(FLAGcs*XLS(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(deltambkin1*r*X(0,Elcuthat,r,0,1)*XLS(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(0,Elcuthat,r,0,1)*XLS(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*XLS(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(nlo.X1El(0,'SM',Elcuthat,r)*XLS(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltambkin1*r*XLS(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(deltamcMS1*r*XLS(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)
            -(deltambkin1*Elcuthat*XLS(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0))
            +flagNLOMuPi*mupi*((-6*X(1,Elcuthat,r,0,0)**3*nlopw.X1ElMuPi(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(6*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlopw.X1ElMuPi(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(X(3,Elcuthat,r,0,0)*nlopw.X1ElMuPi(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(6*X(1,Elcuthat,r,0,0)**2*nlopw.X1ElMuPi(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(3*X(2,Elcuthat,r,0,0)*nlopw.X1ElMuPi(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(3*X(1,Elcuthat,r,0,0)*nlopw.X1ElMuPi(2,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +nlopw.X1ElMuPi(3,Elcuthat,r)/X(0,Elcuthat,r,0,0)-(6*deltambkin1*X(1,Elcuthat,r,0,0)**3*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(24*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(24*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(24*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**3*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(18*deltambkin1*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*deltamcMS1*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,1,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(6*deltambkin1*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(18*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*deltambkin1*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*deltamcMS1*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*deltambkin1*Elcuthat*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*deltambkin1*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*deltamcMS1*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,1,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(deltambkin1*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*r*X(3,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(3,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(3,Elcuthat,r,1,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(24*X(1,Elcuthat,r,0,0)**3*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(18*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(2*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(18*X(1,Elcuthat,r,0,0)**2*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(6*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*X(1,Elcuthat,r,0,0)*nlo.X1El(2,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(nlo.X1El(3,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(6*deltambkin1*r*X(1,Elcuthat,r,0,0)**3*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(6*deltamcMS1*r*X(1,Elcuthat,r,0,0)**3*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(6*deltambkin1*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(6*deltamcMS1*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*r*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(6*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)**3*Xpi(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            -(6*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(deltambkin1*Elcuthat*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(6*deltambkin1*X(1,Elcuthat,r,0,0)**2*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(18*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*deltambkin1*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*deltamcMS1*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(3*deltambkin1*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*deltambkin1*r*X(2,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(3*deltamcMS1*r*X(2,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*deltambkin1*Elcuthat*X(2,Elcuthat,r,1,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(18*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(6*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(3*nlo.X1El(2,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*deltambkin1*r*X(1,Elcuthat,r,0,0)**2*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(6*deltamcMS1*r*X(1,Elcuthat,r,0,0)**2*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(3*deltambkin1*r*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(3*deltamcMS1*r*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(6*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)**2*Xpi(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(3*deltambkin1*Elcuthat*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(3*deltambkin1*X(1,Elcuthat,r,0,0)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*deltambkin1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*deltamcMS1*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*deltambkin1*r*X(1,Elcuthat,r,0,1)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(3*deltamcMS1*r*X(1,Elcuthat,r,0,1)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*deltambkin1*Elcuthat*X(1,Elcuthat,r,1,0)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(6*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(3*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*deltambkin1*r*X(1,Elcuthat,r,0,0)*Xpi(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(3*deltamcMS1*r*X(1,Elcuthat,r,0,0)*Xpi(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(3*deltambkin1*Elcuthat*X(1,Elcuthat,r,0,0)*Xpi(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(deltambkin1*r*X(0,Elcuthat,r,0,1)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltamcMS1*r*X(0,Elcuthat,r,0,1)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(deltambkin1*Elcuthat*X(0,Elcuthat,r,1,0)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(nlo.X1El(0,'SM',Elcuthat,r)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(deltambkin1*r*Xpi(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(deltamcMS1*r*Xpi(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)
            -(deltambkin1*Elcuthat*Xpi(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)))
        if( flagDEBUG == 1):
            print("Elmoment n. 3 NLO pw = api*",resNLO*par.mbkin**3)
        res += api*resNLO

        resNNLO = 0
        resNNLO +=(flagNLORhoD*((6*Rhodpert1*X(1,Elcuthat,r,0,0)**3*nlopw.X1ElRhoD(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            -(6*Rhodpert1*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlopw.X1ElRhoD(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(Rhodpert1*X(3,Elcuthat,r,0,0)*nlopw.X1ElRhoD(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(6*Rhodpert1*X(1,Elcuthat,r,0,0)**2*nlopw.X1ElRhoD(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(3*Rhodpert1*X(2,Elcuthat,r,0,0)*nlopw.X1ElRhoD(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(3*Rhodpert1*X(1,Elcuthat,r,0,0)*nlopw.X1ElRhoD(2,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(Rhodpert1*nlopw.X1ElRhoD(3,Elcuthat,r))/X(0,Elcuthat,r,0,0)+(6*FLAGcD*Rhodpert1*X(1,Elcuthat,r,0,0)**3*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*FLAGcD*Rhodpert1*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(FLAGcD*Rhodpert1*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(24*Rhodpert1*X(1,Elcuthat,r,0,0)**3*nlo.X1El(0,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(18*Rhodpert1*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(2*Rhodpert1*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(18*Rhodpert1*X(1,Elcuthat,r,0,0)**2*nlo.X1El(1,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*Rhodpert1*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*Rhodpert1*X(1,Elcuthat,r,0,0)*nlo.X1El(2,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(Rhodpert1*nlo.X1El(3,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*FLAGcD*Rhodpert1*X(1,Elcuthat,r,0,0)**2*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*FLAGcD*Rhodpert1*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(18*Rhodpert1*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*Rhodpert1*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*Rhodpert1*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*Rhodpert1*nlo.X1El(2,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*FLAGcD*Rhodpert1*X(1,Elcuthat,r,0,0)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*Rhodpert1*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*Rhodpert1*nlo.X1El(1,'SM',Elcuthat,r)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(FLAGcD*Rhodpert1*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(Rhodpert1*nlo.X1El(0,'SM',Elcuthat,r)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2)
            +flagNLOMuPi*((6*Mupipert1*X(1,Elcuthat,r,0,0)**3*nlopw.X1ElMuPi(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            -(6*Mupipert1*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlopw.X1ElMuPi(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(Mupipert1*X(3,Elcuthat,r,0,0)*nlopw.X1ElMuPi(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(6*Mupipert1*X(1,Elcuthat,r,0,0)**2*nlopw.X1ElMuPi(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(3*Mupipert1*X(2,Elcuthat,r,0,0)*nlopw.X1ElMuPi(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(3*Mupipert1*X(1,Elcuthat,r,0,0)*nlopw.X1ElMuPi(2,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(Mupipert1*nlopw.X1ElMuPi(3,Elcuthat,r))/X(0,Elcuthat,r,0,0)-(24*Mupipert1*X(1,Elcuthat,r,0,0)**3*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(18*Mupipert1*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(2*Mupipert1*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(18*Mupipert1*X(1,Elcuthat,r,0,0)**2*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*Mupipert1*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*Mupipert1*X(1,Elcuthat,r,0,0)*nlo.X1El(2,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(Mupipert1*nlo.X1El(3,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(18*Mupipert1*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(6*Mupipert1*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*Mupipert1*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*Mupipert1*nlo.X1El(2,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*Mupipert1*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(3*Mupipert1*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(Mupipert1*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2))
        if( flagDEBUG == 1):
            print("Elmoment n. 3 NNLO from NLO pw = api^2*",resNNLO*par.mbkin**3)
        res += api**2*resNNLO

    return res*par.mbkin**3


def moment_4_KIN_MS(elcut, par, hqe, wc, **kwargs):
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
    flagTEST=kwargs.get('flag_TEST', 1)
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
    res +=((-3*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**4+(6*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(4*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +X(4,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0)+rhoD*((12*X(1,Elcuthat,r,0,0)**4*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
        -(18*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
        +(8*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(X(4,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(12*X(1,Elcuthat,r,0,0)**3*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
        +(12*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(4*X(3,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +(6*X(1,Elcuthat,r,0,0)**2*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(4*X(1,Elcuthat,r,0,0)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +XD(4,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0))+muG*((12*X(1,Elcuthat,r,0,0)**4*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
        -(18*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
        +(8*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(X(4,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(12*X(1,Elcuthat,r,0,0)**3*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
        +(12*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(4*X(3,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +(6*X(1,Elcuthat,r,0,0)**2*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(4*X(1,Elcuthat,r,0,0)*XG(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +XG(4,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0))+rhoLS*((12*X(1,Elcuthat,r,0,0)**4*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
        -(18*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
        +(8*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(X(4,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(12*X(1,Elcuthat,r,0,0)**3*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
        +(12*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(4*X(3,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +(6*X(1,Elcuthat,r,0,0)**2*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(4*X(1,Elcuthat,r,0,0)*XLS(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +XLS(4,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0))+mupi*((12*X(1,Elcuthat,r,0,0)**4*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
        -(18*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
        +(8*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(X(4,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(12*X(1,Elcuthat,r,0,0)**3*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
        +(12*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(4*X(3,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +(6*X(1,Elcuthat,r,0,0)**2*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(4*X(1,Elcuthat,r,0,0)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +Xpi(4,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0)))

    if( flagDEBUG == 1):
        print("Elmoment n. 4 LO = ",res*par.mbkin**4)

    resNLO = 0
    resNLO +=(deltamcMS1*((12*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**5
        -(12*r*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
        -(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
        +(12*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        +(6*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
        +(8*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(4*r*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(4*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
        -(r*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +(r*X(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0))+deltambkin1*((-12*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**4
        -(12*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**5
        -(12*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**5
        +(12*r*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
        +(12*Elcuthat*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
        +(24*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        +(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
        +(18*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
        -(12*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(6*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
        -(6*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
        -(16*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(8*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        -(8*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        +(4*r*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +(4*Elcuthat*X(1,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +(4*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
        +(4*Elcuthat*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
        +(4*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(r*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +(Elcuthat*X(0,Elcuthat,r,1,0)*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(r*X(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)-(Elcuthat*X(4,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0))
        +(12*X(1,Elcuthat,r,0,0)**4*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
        -(18*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
        +(8*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
        -(X(4,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
        -(12*X(1,Elcuthat,r,0,0)**3*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
        +(12*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
        -(4*X(3,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
        +(6*X(1,Elcuthat,r,0,0)**2*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
        -(4*X(1,Elcuthat,r,0,0)*nlo.X1El(3,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
        +nlo.X1El(4,'SM',Elcuthat,r)/X(0,Elcuthat,r,0,0)+Rhodpert1*((-12*X(1,Elcuthat,r,0,0)**4*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
        +(18*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
        -(8*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        +(X(4,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +(12*X(1,Elcuthat,r,0,0)**3*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
        -(12*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        +(4*X(3,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(6*X(1,Elcuthat,r,0,0)**2*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        +(4*X(1,Elcuthat,r,0,0)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -XD(4,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0))+Mupipert1*((-12*X(1,Elcuthat,r,0,0)**4*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
        +(18*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
        -(8*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        +(X(4,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        +(12*X(1,Elcuthat,r,0,0)**3*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
        -(12*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        +(4*X(3,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -(6*X(1,Elcuthat,r,0,0)**2*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
        +(4*X(1,Elcuthat,r,0,0)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
        -Xpi(4,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0)))

    if( flagDEBUG == 1):
        print("Elmoment n. 4 NLO = api*",resNLO*par.mbkin**4)
    res += api*resNLO

    if(kwargs.get('flag_includeNNLO', 1) == 1):
        resNNLO = 0
        resNNLO +=((-12*beta0*deltambkin2BLM*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**4
            -(12*beta0*deltambkin2BLM*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**5
            +(12*beta0*deltamcMS2BLM*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**5
            -(12*beta0*deltambkin2BLM*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**5
            +(12*beta0*deltambkin2BLM*r*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(12*beta0*deltamcMS2BLM*r*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            +(12*beta0*deltambkin2BLM*Elcuthat*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            +(24*beta0*deltambkin2BLM*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(18*beta0*deltambkin2BLM*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*beta0*deltamcMS2BLM*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*beta0*deltambkin2BLM*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*beta0*deltambkin2BLM*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*beta0*deltamcMS2BLM*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*beta0*deltambkin2BLM*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*beta0*deltambkin2BLM*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(6*beta0*deltamcMS2BLM*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(6*beta0*deltambkin2BLM*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(16*beta0*deltambkin2BLM*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(8*beta0*deltambkin2BLM*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*beta0*deltamcMS2BLM*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*beta0*deltambkin2BLM*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*beta0*deltambkin2BLM*r*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(4*beta0*deltamcMS2BLM*r*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*beta0*deltambkin2BLM*Elcuthat*X(1,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*beta0*deltambkin2BLM*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(4*beta0*deltamcMS2BLM*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(4*beta0*deltambkin2BLM*Elcuthat*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(4*beta0*deltambkin2BLM*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)
            +(beta0*deltambkin2BLM*r*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(beta0*deltamcMS2BLM*r*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(beta0*deltambkin2BLM*Elcuthat*X(0,Elcuthat,r,1,0)*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(beta0*deltambkin2BLM*r*X(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)
            +(beta0*deltamcMS2BLM*r*X(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)
            -(beta0*deltambkin2BLM*Elcuthat*X(4,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)
            +(3*beta0*math.log(mus**2)*X(1,Elcuthat,r,0,0)**4*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
            -(9*beta0*math.log(mus**2)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/(2*X(0,Elcuthat,r,0,0)**4)
            +(2*beta0*math.log(mus**2)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(beta0*math.log(mus**2)*X(4,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/(4*X(0,Elcuthat,r,0,0)**2)
            -(3*beta0*math.log(mus**2)*X(1,Elcuthat,r,0,0)**3*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(3*beta0*math.log(mus**2)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(beta0*math.log(mus**2)*X(3,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(3*beta0*math.log(mus**2)*X(1,Elcuthat,r,0,0)**2*nlo.X1El(2,'SM',Elcuthat,r))/(2*X(0,Elcuthat,r,0,0)**3)
            -(beta0*math.log(mus**2)*X(1,Elcuthat,r,0,0)*nlo.X1El(3,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(beta0*math.log(mus**2)*nlo.X1El(4,'SM',Elcuthat,r))/(4*X(0,Elcuthat,r,0,0))
            +(12*beta0*X(1,Elcuthat,r,0,0)**4*nnlo.X2ElBLM(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
            -(18*beta0*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*nnlo.X2ElBLM(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(8*beta0*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*nnlo.X2ElBLM(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(beta0*X(4,Elcuthat,r,0,0)*nnlo.X2ElBLM(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(12*beta0*X(1,Elcuthat,r,0,0)**3*nnlo.X2ElBLM(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(12*beta0*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nnlo.X2ElBLM(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(4*beta0*X(3,Elcuthat,r,0,0)*nnlo.X2ElBLM(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(6*beta0*X(1,Elcuthat,r,0,0)**2*nnlo.X2ElBLM(2,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(4*beta0*X(1,Elcuthat,r,0,0)*nnlo.X2ElBLM(3,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(beta0*nnlo.X2ElBLM(4,Elcuthat,r))/X(0,Elcuthat,r,0,0)-(12*beta0*Rhodpert2BLM*X(1,Elcuthat,r,0,0)**4*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(18*beta0*Rhodpert2BLM*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(8*beta0*Rhodpert2BLM*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(beta0*Rhodpert2BLM*X(4,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(12*beta0*Rhodpert2BLM*X(1,Elcuthat,r,0,0)**3*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*beta0*Rhodpert2BLM*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*beta0*Rhodpert2BLM*X(3,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*beta0*Rhodpert2BLM*X(1,Elcuthat,r,0,0)**2*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*beta0*Rhodpert2BLM*X(1,Elcuthat,r,0,0)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(beta0*Rhodpert2BLM*XD(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)
            -(12*beta0*Mupipert2BLM*X(1,Elcuthat,r,0,0)**4*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(18*beta0*Mupipert2BLM*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(8*beta0*Mupipert2BLM*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(beta0*Mupipert2BLM*X(4,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(12*beta0*Mupipert2BLM*X(1,Elcuthat,r,0,0)**3*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*beta0*Mupipert2BLM*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*beta0*Mupipert2BLM*X(3,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*beta0*Mupipert2BLM*X(1,Elcuthat,r,0,0)**2*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*beta0*Mupipert2BLM*X(1,Elcuthat,r,0,0)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(beta0*Mupipert2BLM*Xpi(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0))
        if( flagDEBUG == 1):
            print("Elmoment n. 4 NNLO BLM = api^2*beta0*",resNNLO/beta0*par.mbkin**4)
        res += api**2*resNNLO

        resNNLO = 0
        resNNLO +=((deltamcMS2-beta0*deltamcMS2BLM)*((12*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**5
            -(12*r*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(8*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*r*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(4*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(r*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r*X(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0))+deltamcMS1**2*((
            -30*r**2*X(0,Elcuthat,r,0,1)**2*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**6
            +(6*r**2*X(0,Elcuthat,r,0,2)*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**5
            +(48*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**5
            -(18*r**2*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)**2)/X(0,Elcuthat,r,0,0)**4
            -(6*r**2*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,2))/X(0,Elcuthat,r,0,0)**4
            +(36*r**2*X(0,Elcuthat,r,0,1)**2*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(9*r**2*X(0,Elcuthat,r,0,2)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(36*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(6*r**2*X(1,Elcuthat,r,0,1)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*r**2*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,2)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(18*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            +(12*r**2*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(3*r**2*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,2))/X(0,Elcuthat,r,0,0)**3
            -(12*r**2*X(0,Elcuthat,r,0,1)**2*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(4*r**2*X(0,Elcuthat,r,0,2)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*r**2*X(1,Elcuthat,r,0,2)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(8*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(4*r**2*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(2*r**2*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,2))/X(0,Elcuthat,r,0,0)**2
            +(r**2*X(0,Elcuthat,r,0,1)**2*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(r**2*X(0,Elcuthat,r,0,2)*X(4,Elcuthat,r,0,0))/(2*X(0,Elcuthat,r,0,0)**2)
            -(r**2*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(r**2*X(4,Elcuthat,r,0,2))/(2*X(0,Elcuthat,r,0,0)))+(deltambkin2
            -beta0*deltambkin2BLM)*((-12*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**5
            -(12*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**5
            +(12*r*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            +(12*Elcuthat*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            +(24*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(6*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(16*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(8*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*r*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*Elcuthat*X(1,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(4*Elcuthat*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(4*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(r*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*X(0,Elcuthat,r,1,0)*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(r*X(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)-(Elcuthat*X(4,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0))
            +deltambkin1**2*((-18*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**4
            -(36*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**5
            -(30*r**2*X(0,Elcuthat,r,0,1)**2*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**6
            +(6*r**2*X(0,Elcuthat,r,0,2)*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**5
            -(36*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**5
            -(60*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**6
            -(30*Elcuthat**2*X(0,Elcuthat,r,1,0)**2*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**6
            +(12*Elcuthat*r*X(0,Elcuthat,r,1,1)*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**5
            +(6*Elcuthat**2*X(0,Elcuthat,r,2,0)*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**5
            +(36*r*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            +(48*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**5
            +(48*Elcuthat*r*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**5
            -(18*r**2*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)**2)/X(0,Elcuthat,r,0,0)**4
            -(6*r**2*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,2))/X(0,Elcuthat,r,0,0)**4
            +(36*Elcuthat*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            +(48*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**5
            +(48*Elcuthat**2*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**5
            -(36*Elcuthat*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            -(18*Elcuthat**2*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,1,0)**2)/X(0,Elcuthat,r,0,0)**4
            -(12*Elcuthat*r*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,1,1))/X(0,Elcuthat,r,0,0)**4
            -(6*Elcuthat**2*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,2,0))/X(0,Elcuthat,r,0,0)**4
            +(36*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(54*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(36*r**2*X(0,Elcuthat,r,0,1)**2*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(9*r**2*X(0,Elcuthat,r,0,2)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(54*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(72*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(36*Elcuthat**2*X(0,Elcuthat,r,1,0)**2*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(18*Elcuthat*r*X(0,Elcuthat,r,1,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(9*Elcuthat**2*X(0,Elcuthat,r,2,0)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(36*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(36*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(36*Elcuthat*r*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(6*r**2*X(1,Elcuthat,r,0,1)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*r**2*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,2)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(36*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(36*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(36*Elcuthat**2*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*Elcuthat*r*X(1,Elcuthat,r,0,1)*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*Elcuthat**2*X(1,Elcuthat,r,1,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*Elcuthat*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*Elcuthat**2*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,2,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(18*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(18*Elcuthat*r*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            +(12*r**2*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(12*Elcuthat*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(3*r**2*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,2))/X(0,Elcuthat,r,0,0)**3
            -(18*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(18*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            -(18*Elcuthat**2*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            +(12*Elcuthat*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(12*Elcuthat**2*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(6*Elcuthat*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,1,1))/X(0,Elcuthat,r,0,0)**3
            +(3*Elcuthat**2*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,2,0))/X(0,Elcuthat,r,0,0)**3
            -(24*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(24*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*r**2*X(0,Elcuthat,r,0,1)**2*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(4*r**2*X(0,Elcuthat,r,0,2)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(24*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(24*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*Elcuthat**2*X(0,Elcuthat,r,1,0)**2*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(8*Elcuthat*r*X(0,Elcuthat,r,1,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*Elcuthat**2*X(0,Elcuthat,r,2,0)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*r*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(8*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*Elcuthat*r*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*r**2*X(1,Elcuthat,r,0,2)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(12*Elcuthat*X(1,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(8*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*Elcuthat**2*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*Elcuthat*r*X(1,Elcuthat,r,1,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*Elcuthat**2*X(1,Elcuthat,r,2,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(12*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(8*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(8*Elcuthat*r*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(4*r**2*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(4*Elcuthat*r*X(1,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(2*r**2*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,2))/X(0,Elcuthat,r,0,0)**2
            +(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(8*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(8*Elcuthat**2*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(4*Elcuthat*r*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(4*Elcuthat**2*X(1,Elcuthat,r,1,0)*X(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(4*Elcuthat*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,1,1))/X(0,Elcuthat,r,0,0)**2
            -(2*Elcuthat**2*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,2,0))/X(0,Elcuthat,r,0,0)**2
            +(6*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(3*r*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r**2*X(0,Elcuthat,r,0,1)**2*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(r**2*X(0,Elcuthat,r,0,2)*X(4,Elcuthat,r,0,0))/(2*X(0,Elcuthat,r,0,0)**2)
            +(3*Elcuthat*X(0,Elcuthat,r,1,0)*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(0,Elcuthat,r,1,0)*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(Elcuthat**2*X(0,Elcuthat,r,1,0)**2*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(Elcuthat*r*X(0,Elcuthat,r,1,1)*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat**2*X(0,Elcuthat,r,2,0)*X(4,Elcuthat,r,0,0))/(2*X(0,Elcuthat,r,0,0)**2)
            -(3*r*X(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)-(r**2*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*r*X(0,Elcuthat,r,1,0)*X(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(r**2*X(4,Elcuthat,r,0,2))/(2*X(0,Elcuthat,r,0,0))-(3*Elcuthat*X(4,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)
            -(Elcuthat*r*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat**2*X(0,Elcuthat,r,1,0)*X(4,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*r*X(4,Elcuthat,r,1,1))/X(0,Elcuthat,r,0,0)+(Elcuthat**2*X(4,Elcuthat,r,2,0))/(2*X(0,Elcuthat,r,0,0)))
            -(2*math.log(mus**2)*X(1,Elcuthat,r,0,0)**4*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
            +(3*math.log(mus**2)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            -(4*math.log(mus**2)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/(3*X(0,Elcuthat,r,0,0)**3)
            +(math.log(mus**2)*X(4,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/(6*X(0,Elcuthat,r,0,0)**2)
            -(30*X(1,Elcuthat,r,0,0)**4*nlo.X1El(0,'SM',Elcuthat,r)**2)/X(0,Elcuthat,r,0,0)**6
            +(36*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)**2)/X(0,Elcuthat,r,0,0)**5
            -(12*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)**2)/X(0,Elcuthat,r,0,0)**4
            +(X(4,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)**2)/X(0,Elcuthat,r,0,0)**3
            +(2*math.log(mus**2)*X(1,Elcuthat,r,0,0)**3*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            -(2*math.log(mus**2)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(2*math.log(mus**2)*X(3,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/(3*X(0,Elcuthat,r,0,0)**2)
            +(48*X(1,Elcuthat,r,0,0)**3*nlo.X1El(0,'SM',Elcuthat,r)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
            -(36*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(8*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(18*X(1,Elcuthat,r,0,0)**2*nlo.X1El(1,'SM',Elcuthat,r)**2)/X(0,Elcuthat,r,0,0)**4
            +(6*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)**2)/X(0,Elcuthat,r,0,0)**3
            -(math.log(mus**2)*X(1,Elcuthat,r,0,0)**2*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(18*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r)*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(12*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(2*math.log(mus**2)*X(1,Elcuthat,r,0,0)*nlo.X1El(3,'SM',Elcuthat,r))/(3*X(0,Elcuthat,r,0,0)**2)
            +(8*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*nlo.X1El(3,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(4*nlo.X1El(1,'SM',Elcuthat,r)*nlo.X1El(3,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(math.log(mus**2)*nlo.X1El(4,'SM',Elcuthat,r))/(6*X(0,Elcuthat,r,0,0))-(nlo.X1El(0,'SM',Elcuthat,r)*nlo.X1El(4,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +deltamcMS1*((r*nlo.X1El_Derivativer(4,Elcuthat,r))/X(0,Elcuthat,r,0,0)-(4*r*nlo.X1El_Derivativer(3,Elcuthat,r)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(6*r*nlo.X1El_Derivativer(2,Elcuthat,r)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
            -(12*r*nlo.X1El_Derivativer(1,Elcuthat,r)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**4
            +(12*r*nlo.X1El_Derivativer(0,Elcuthat,r)*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**5
            +(12*r*nlo.X1El_Derivativer(1,Elcuthat,r)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(18*r*nlo.X1El_Derivativer(0,Elcuthat,r)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(4*r*nlo.X1El_Derivativer(1,Elcuthat,r)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(8*r*nlo.X1El_Derivativer(0,Elcuthat,r)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(r*nlo.X1El_Derivativer(0,Elcuthat,r)*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(60*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**4*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**6
            +(48*r*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
            +(72*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
            -(36*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            -(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            -(24*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(8*r*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(2*r*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(r*X(4,Elcuthat,r,0,1)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(48*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
            -(36*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            -(36*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(8*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(4*r*X(3,Elcuthat,r,0,1)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(8*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*nlo.X1El(3,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(4*r*X(1,Elcuthat,r,0,1)*nlo.X1El(3,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(r*X(0,Elcuthat,r,0,1)*nlo.X1El(4,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2)
            +deltambkin1*(-((Elcuthat*nlo.X1El_DerivativeEl(4,Elcuthat,r))/X(0,Elcuthat,r,0,0))
            -(r*nlo.X1El_Derivativer(4,Elcuthat,r))/X(0,Elcuthat,r,0,0)+(4*Elcuthat*nlo.X1El_DerivativeEl(3,Elcuthat,r)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*r*nlo.X1El_Derivativer(3,Elcuthat,r)*X(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*Elcuthat*nlo.X1El_DerivativeEl(2,Elcuthat,r)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
            -(6*r*nlo.X1El_Derivativer(2,Elcuthat,r)*X(1,Elcuthat,r,0,0)**2)/X(0,Elcuthat,r,0,0)**3
            +(12*Elcuthat*nlo.X1El_DerivativeEl(1,Elcuthat,r)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**4
            +(12*r*nlo.X1El_Derivativer(1,Elcuthat,r)*X(1,Elcuthat,r,0,0)**3)/X(0,Elcuthat,r,0,0)**4
            -(12*Elcuthat*nlo.X1El_DerivativeEl(0,Elcuthat,r)*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**5
            -(12*r*nlo.X1El_Derivativer(0,Elcuthat,r)*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**5
            -(12*Elcuthat*nlo.X1El_DerivativeEl(1,Elcuthat,r)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*r*nlo.X1El_Derivativer(1,Elcuthat,r)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(18*Elcuthat*nlo.X1El_DerivativeEl(0,Elcuthat,r)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*r*nlo.X1El_Derivativer(0,Elcuthat,r)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(4*Elcuthat*nlo.X1El_DerivativeEl(1,Elcuthat,r)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*r*nlo.X1El_Derivativer(1,Elcuthat,r)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(8*Elcuthat*nlo.X1El_DerivativeEl(0,Elcuthat,r)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*r*nlo.X1El_Derivativer(0,Elcuthat,r)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(Elcuthat*nlo.X1El_DerivativeEl(0,Elcuthat,r)*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r*nlo.X1El_Derivativer(0,Elcuthat,r)*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +deltamcMS1*((36*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**5
            +(60*r**2*X(0,Elcuthat,r,0,1)**2*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**6
            -(12*r**2*X(0,Elcuthat,r,0,2)*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**5
            +(60*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**6
            -(12*Elcuthat*r*X(0,Elcuthat,r,1,1)*X(1,Elcuthat,r,0,0)**4)/X(0,Elcuthat,r,0,0)**5
            -(36*r*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(96*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**5
            -(48*Elcuthat*r*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**5
            +(36*r**2*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)**2)/X(0,Elcuthat,r,0,0)**4
            +(12*r**2*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,2))/X(0,Elcuthat,r,0,0)**4
            -(48*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**5
            +(36*Elcuthat*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*X(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            +(12*Elcuthat*r*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,1,1))/X(0,Elcuthat,r,0,0)**4
            -(54*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(72*r**2*X(0,Elcuthat,r,0,1)**2*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(18*r**2*X(0,Elcuthat,r,0,2)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(72*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(18*Elcuthat*r*X(0,Elcuthat,r,1,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(36*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(72*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(36*Elcuthat*r*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*r**2*X(1,Elcuthat,r,0,1)**2*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*r**2*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,2)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(36*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*Elcuthat*r*X(1,Elcuthat,r,0,1)*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*Elcuthat*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,1)*X(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(36*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            +(18*Elcuthat*r*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(24*r**2*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(12*Elcuthat*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(6*r**2*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,2))/X(0,Elcuthat,r,0,0)**3
            +(18*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            -(12*Elcuthat*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(6*Elcuthat*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,1,1))/X(0,Elcuthat,r,0,0)**3
            +(24*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(24*r**2*X(0,Elcuthat,r,0,1)**2*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(8*r**2*X(0,Elcuthat,r,0,2)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(24*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(8*Elcuthat*r*X(0,Elcuthat,r,1,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*r*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(16*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*Elcuthat*r*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*r**2*X(1,Elcuthat,r,0,2)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(8*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*Elcuthat*r*X(1,Elcuthat,r,1,1)*X(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(12*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(16*r**2*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(8*Elcuthat*r*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(8*r**2*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(4*Elcuthat*r*X(1,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(4*r**2*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,2))/X(0,Elcuthat,r,0,0)**2
            -(8*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(4*Elcuthat*r*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(4*Elcuthat*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,1,1))/X(0,Elcuthat,r,0,0)**2
            -(3*r*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*r**2*X(0,Elcuthat,r,0,1)**2*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(r**2*X(0,Elcuthat,r,0,2)*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*Elcuthat*r*X(0,Elcuthat,r,0,1)*X(0,Elcuthat,r,1,0)*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(Elcuthat*r*X(0,Elcuthat,r,1,1)*X(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(3*r*X(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(2*r**2*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*r*X(0,Elcuthat,r,1,0)*X(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(r**2*X(4,Elcuthat,r,0,2))/X(0,Elcuthat,r,0,0)+(Elcuthat*r*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*r*X(4,Elcuthat,r,1,1))/X(0,Elcuthat,r,0,0))+(48*X(1,Elcuthat,r,0,0)**4*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
            +(60*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**4*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**6
            +(60*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**4*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**6
            -(48*r*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
            -(48*Elcuthat*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,1,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
            -(72*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            -(72*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
            -(72*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
            +(36*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(36*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(18*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,1,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(32*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(24*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(24*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            -(8*r*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(8*Elcuthat*X(1,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(8*Elcuthat*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,1,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(4*X(4,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(2*r*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(2*Elcuthat*X(0,Elcuthat,r,1,0)*X(4,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(r*X(4,Elcuthat,r,0,1)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*X(4,Elcuthat,r,1,0)*nlo.X1El(0,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(48*X(1,Elcuthat,r,0,0)**3*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            -(48*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
            -(48*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**3*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
            +(36*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(36*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,1,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(48*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(36*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(36*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(12*Elcuthat*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,1,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(16*X(3,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(8*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(8*Elcuthat*X(0,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(4*r*X(3,Elcuthat,r,0,1)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(4*Elcuthat*X(3,Elcuthat,r,1,0)*nlo.X1El(1,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(24*X(1,Elcuthat,r,0,0)**2*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(18*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*nlo.X1El(2,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(16*X(1,Elcuthat,r,0,0)*nlo.X1El(3,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(8*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*nlo.X1El(3,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(8*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*nlo.X1El(3,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(4*r*X(1,Elcuthat,r,0,1)*nlo.X1El(3,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(4*Elcuthat*X(1,Elcuthat,r,1,0)*nlo.X1El(3,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(4*nlo.X1El(4,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)+(r*X(0,Elcuthat,r,0,1)*nlo.X1El(4,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*X(0,Elcuthat,r,1,0)*nlo.X1El(4,'SM',Elcuthat,r))/X(0,Elcuthat,r,0,0)**2)
            +(12*X(1,Elcuthat,r,0,0)**4*flagTEST*nnlo.X2ElnonBLM(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
            -(18*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*flagTEST*nnlo.X2ElnonBLM(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(8*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*flagTEST*nnlo.X2ElnonBLM(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(X(4,Elcuthat,r,0,0)*flagTEST*nnlo.X2ElnonBLM(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(12*X(1,Elcuthat,r,0,0)**3*flagTEST*nnlo.X2ElnonBLM(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(12*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*flagTEST*nnlo.X2ElnonBLM(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(4*X(3,Elcuthat,r,0,0)*flagTEST*nnlo.X2ElnonBLM(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(6*X(1,Elcuthat,r,0,0)**2*flagTEST*nnlo.X2ElnonBLM(2,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(4*X(1,Elcuthat,r,0,0)*flagTEST*nnlo.X2ElnonBLM(3,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +flagTEST*nnlo.X2ElnonBLM(4,Elcuthat,r)/X(0,Elcuthat,r,0,0)+(Rhodpert2-beta0*Rhodpert2BLM)*((
            -12*X(1,Elcuthat,r,0,0)**4*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(18*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(8*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(X(4,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(12*X(1,Elcuthat,r,0,0)**3*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*X(3,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*X(1,Elcuthat,r,0,0)**2*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*X(1,Elcuthat,r,0,0)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -XD(4,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0))+Rhodpert1*((2*math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)**4*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(3*math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(4*math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/(3*X(0,Elcuthat,r,0,0)**3)
            -(math.log(mus**2/r**2)*X(4,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/(6*X(0,Elcuthat,r,0,0)**2)
            -(2*math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)**3*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(2*math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*math.log(mus**2/r**2)*X(3,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/(3*X(0,Elcuthat,r,0,0)**2)
            +(math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)**2*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)*XD(3,Elcuthat,r,0,0))/(3*X(0,Elcuthat,r,0,0)**2)
            +(math.log(mus**2/r**2)*XD(4,Elcuthat,r,0,0))/(6*X(0,Elcuthat,r,0,0)))
            +deltamcMS1*Rhodpert1*((60*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**4*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**6
            -(48*r*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(72*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(36*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(24*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(8*r*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*r*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(r*X(4,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(12*r*X(1,Elcuthat,r,0,0)**4*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**5
            +(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(r*X(4,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(48*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(36*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(36*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*r*X(3,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(12*r*X(1,Elcuthat,r,0,0)**3*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(4*r*X(3,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*r*X(1,Elcuthat,r,0,0)**2*XD(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(8*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*r*X(1,Elcuthat,r,0,1)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*r*X(1,Elcuthat,r,0,0)*XD(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(r*X(0,Elcuthat,r,0,1)*XD(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(r*XD(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0))+deltambkin1*Rhodpert1*((
            -12*X(1,Elcuthat,r,0,0)**4*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(60*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**4*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**6
            -(60*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**4*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**6
            +(48*r*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(48*Elcuthat*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,1,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(18*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(72*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(72*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(36*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(36*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,1,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(8*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(24*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(24*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(8*r*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*Elcuthat*X(1,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*Elcuthat*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,1,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(X(4,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*r*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*Elcuthat*X(0,Elcuthat,r,1,0)*X(4,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(r*X(4,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*X(4,Elcuthat,r,1,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(12*r*X(1,Elcuthat,r,0,0)**4*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**5
            -(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            +(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(r*X(4,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(12*Elcuthat*X(1,Elcuthat,r,0,0)**4*XD(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**5
            -(18*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            +(8*Elcuthat*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(Elcuthat*X(4,Elcuthat,r,0,0)*XD(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(12*X(1,Elcuthat,r,0,0)**3*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(48*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(48*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**3*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(36*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(36*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,1,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(36*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(36*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*Elcuthat*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,1,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*X(3,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(8*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*Elcuthat*X(0,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*r*X(3,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(4*Elcuthat*X(3,Elcuthat,r,1,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(12*r*X(1,Elcuthat,r,0,0)**3*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(4*r*X(3,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(12*Elcuthat*X(1,Elcuthat,r,0,0)**3*XD(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            +(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(4*Elcuthat*X(3,Elcuthat,r,0,0)*XD(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(6*X(1,Elcuthat,r,0,0)**2*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*r*X(1,Elcuthat,r,0,0)**2*XD(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(6*Elcuthat*X(1,Elcuthat,r,0,0)**2*XD(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(4*X(1,Elcuthat,r,0,0)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(8*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*r*X(1,Elcuthat,r,0,1)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(4*Elcuthat*X(1,Elcuthat,r,1,0)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(4*r*X(1,Elcuthat,r,0,0)*XD(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(4*Elcuthat*X(1,Elcuthat,r,0,0)*XD(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -XD(4,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0)-(r*X(0,Elcuthat,r,0,1)*XD(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*X(0,Elcuthat,r,1,0)*XD(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r*XD(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(Elcuthat*XD(4,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0))
            +(Mupipert2-beta0*Mupipert2BLM)*((-12*X(1,Elcuthat,r,0,0)**4*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(18*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(8*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(X(4,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(12*X(1,Elcuthat,r,0,0)**3*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*X(3,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*X(1,Elcuthat,r,0,0)**2*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*X(1,Elcuthat,r,0,0)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -Xpi(4,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0))+Mupipert1*((2*math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)**4*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(3*math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(4*math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/(3*X(0,Elcuthat,r,0,0)**3)
            -(math.log(mus**2/r**2)*X(4,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/(6*X(0,Elcuthat,r,0,0)**2)
            -(2*math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)**3*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(2*math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*math.log(mus**2/r**2)*X(3,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/(3*X(0,Elcuthat,r,0,0)**2)
            +(math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)**2*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*math.log(mus**2/r**2)*X(1,Elcuthat,r,0,0)*Xpi(3,Elcuthat,r,0,0))/(3*X(0,Elcuthat,r,0,0)**2)
            +(math.log(mus**2/r**2)*Xpi(4,Elcuthat,r,0,0))/(6*X(0,Elcuthat,r,0,0)))
            +deltamcMS1*Mupipert1*((60*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**4*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**6
            -(48*r*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(72*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(36*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(24*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(8*r*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*r*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(r*X(4,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(12*r*X(1,Elcuthat,r,0,0)**4*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**5
            +(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(r*X(4,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(48*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(36*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(36*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*r*X(3,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(12*r*X(1,Elcuthat,r,0,0)**3*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(4*r*X(3,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*r*X(1,Elcuthat,r,0,0)**2*Xpi(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(8*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*r*X(1,Elcuthat,r,0,1)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*r*X(1,Elcuthat,r,0,0)*Xpi(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(r*X(0,Elcuthat,r,0,1)*Xpi(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(r*Xpi(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0))+deltambkin1*Mupipert1*((
            -24*X(1,Elcuthat,r,0,0)**4*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(60*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**4*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**6
            -(60*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**4*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**6
            +(48*r*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(48*Elcuthat*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,1,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(36*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(72*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(72*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(36*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(36*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,1,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(16*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(24*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(24*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(8*r*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*Elcuthat*X(1,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*Elcuthat*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,1,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*X(4,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(2*r*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*Elcuthat*X(0,Elcuthat,r,1,0)*X(4,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(r*X(4,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*X(4,Elcuthat,r,1,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(12*r*X(1,Elcuthat,r,0,0)**4*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**5
            -(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            +(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(r*X(4,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(12*Elcuthat*X(1,Elcuthat,r,0,0)**4*Xpi(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**5
            -(18*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            +(8*Elcuthat*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(Elcuthat*X(4,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(24*X(1,Elcuthat,r,0,0)**3*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(48*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(48*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**3*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(36*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(36*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,1,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(24*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(36*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(36*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*Elcuthat*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,1,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*X(3,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(8*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*Elcuthat*X(0,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*r*X(3,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(4*Elcuthat*X(3,Elcuthat,r,1,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(12*r*X(1,Elcuthat,r,0,0)**3*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(4*r*X(3,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(12*Elcuthat*X(1,Elcuthat,r,0,0)**3*Xpi(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            +(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(4*Elcuthat*X(3,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(12*X(1,Elcuthat,r,0,0)**2*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*r*X(1,Elcuthat,r,0,0)**2*Xpi(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(6*Elcuthat*X(1,Elcuthat,r,0,0)**2*Xpi(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(8*X(1,Elcuthat,r,0,0)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(8*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*r*X(1,Elcuthat,r,0,1)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(4*Elcuthat*X(1,Elcuthat,r,1,0)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(4*r*X(1,Elcuthat,r,0,0)*Xpi(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(4*Elcuthat*X(1,Elcuthat,r,0,0)*Xpi(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(2*Xpi(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)-(r*X(0,Elcuthat,r,0,1)*Xpi(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(Elcuthat*X(0,Elcuthat,r,1,0)*Xpi(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r*Xpi(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)+(Elcuthat*Xpi(4,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)))
        resNNLO += nnlo.fitElNNLOnonBLM(4, Elcuthat, r)*flagNONBLM*flagTEST
        if( flagDEBUG == 1):
            print("Elmoment n. 4 NNLO non-BLM = api^2*",resNNLO*par.mbkin**4)
        res += api**2*resNNLO

    if(kwargs.get('flag_includeNLOpw', 1) == 1):
        resNLO = 0
        resNLO +=(flagNLORhoD*rhoD*((12*X(1,Elcuthat,r,0,0)**4*nlopw.X1ElRhoD(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
            -(18*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*nlopw.X1ElRhoD(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(8*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*nlopw.X1ElRhoD(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(X(4,Elcuthat,r,0,0)*nlopw.X1ElRhoD(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(12*X(1,Elcuthat,r,0,0)**3*nlopw.X1ElRhoD(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(12*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlopw.X1ElRhoD(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(4*X(3,Elcuthat,r,0,0)*nlopw.X1ElRhoD(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(6*X(1,Elcuthat,r,0,0)**2*nlopw.X1ElRhoD(2,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(4*X(1,Elcuthat,r,0,0)*nlopw.X1ElRhoD(3,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +nlopw.X1ElRhoD(4,Elcuthat,r)/X(0,Elcuthat,r,0,0)-(60*X(1,Elcuthat,r,0,0)**4*nlo.X1El(0,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**6
            +(72*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(24*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(2*X(4,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(48*X(1,Elcuthat,r,0,0)**3*nlo.X1El(1,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(36*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(8*X(3,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(18*X(1,Elcuthat,r,0,0)**2*nlo.X1El(2,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(8*X(1,Elcuthat,r,0,0)*nlo.X1El(3,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(nlo.X1El(4,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(48*X(1,Elcuthat,r,0,0)**3*nlo.X1El(0,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(36*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(8*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(36*X(1,Elcuthat,r,0,0)**2*nlo.X1El(1,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*X(1,Elcuthat,r,0,0)*nlo.X1El(2,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*nlo.X1El(3,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(18*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*nlo.X1El(1,'SM',Elcuthat,r)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(nlo.X1El(0,'SM',Elcuthat,r)*XD(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +FLAGcD*((12*X(1,Elcuthat,r,0,0)**4*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(18*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(8*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(X(4,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(12*X(1,Elcuthat,r,0,0)**3*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*X(3,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(6*X(1,Elcuthat,r,0,0)**2*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*X(1,Elcuthat,r,0,0)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +XD(4,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0))+deltamcMS1*((-60*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**4*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**6
            +(48*r*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(72*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(36*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(24*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(8*r*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*r*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(r*X(4,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(12*r*X(1,Elcuthat,r,0,0)**4*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**5
            -(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            +(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(r*X(4,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(48*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(36*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(36*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*r*X(3,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(12*r*X(1,Elcuthat,r,0,0)**3*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(4*r*X(3,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*r*X(1,Elcuthat,r,0,0)**2*XD(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(8*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*r*X(1,Elcuthat,r,0,1)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(4*r*X(1,Elcuthat,r,0,0)*XD(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(r*X(0,Elcuthat,r,0,1)*XD(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r*XD(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0))+deltambkin1*((12*X(1,Elcuthat,r,0,0)**4*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(60*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**4*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**6
            +(60*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**4*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**6
            -(48*r*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(48*Elcuthat*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,1,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(18*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(72*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(72*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(36*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(36*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,1,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(8*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(24*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(24*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(8*r*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*Elcuthat*X(1,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*Elcuthat*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,1,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(X(4,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*r*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*Elcuthat*X(0,Elcuthat,r,1,0)*X(4,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(r*X(4,Elcuthat,r,0,1)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*X(4,Elcuthat,r,1,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(12*r*X(1,Elcuthat,r,0,0)**4*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**5
            +(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(r*X(4,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(12*Elcuthat*X(1,Elcuthat,r,0,0)**4*XD(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**5
            +(18*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            -(8*Elcuthat*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(Elcuthat*X(4,Elcuthat,r,0,0)*XD(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(12*X(1,Elcuthat,r,0,0)**3*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(48*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(48*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**3*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(36*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(36*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,1,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(36*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(36*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*Elcuthat*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,1,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*X(3,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(8*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*Elcuthat*X(0,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*r*X(3,Elcuthat,r,0,1)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*Elcuthat*X(3,Elcuthat,r,1,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(12*r*X(1,Elcuthat,r,0,0)**3*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(4*r*X(3,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(12*Elcuthat*X(1,Elcuthat,r,0,0)**3*XD(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            -(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(4*Elcuthat*X(3,Elcuthat,r,0,0)*XD(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(6*X(1,Elcuthat,r,0,0)**2*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*r*X(1,Elcuthat,r,0,0)**2*XD(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(6*Elcuthat*X(1,Elcuthat,r,0,0)**2*XD(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(4*X(1,Elcuthat,r,0,0)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(8*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*r*X(1,Elcuthat,r,0,1)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*Elcuthat*X(1,Elcuthat,r,1,0)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*r*X(1,Elcuthat,r,0,0)*XD(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(4*Elcuthat*X(1,Elcuthat,r,0,0)*XD(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +XD(4,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0)+(r*X(0,Elcuthat,r,0,1)*XD(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*X(0,Elcuthat,r,1,0)*XD(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(r*XD(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)-(Elcuthat*XD(4,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)))
            +flagNLOMuG*muG*((12*X(1,Elcuthat,r,0,0)**4*nlopw.X1ElMuG(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
            -(18*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*nlopw.X1ElMuG(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(8*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*nlopw.X1ElMuG(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(X(4,Elcuthat,r,0,0)*nlopw.X1ElMuG(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(12*X(1,Elcuthat,r,0,0)**3*nlopw.X1ElMuG(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(12*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlopw.X1ElMuG(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(4*X(3,Elcuthat,r,0,0)*nlopw.X1ElMuG(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(6*X(1,Elcuthat,r,0,0)**2*nlopw.X1ElMuG(2,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(4*X(1,Elcuthat,r,0,0)*nlopw.X1ElMuG(3,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +nlopw.X1ElMuG(4,Elcuthat,r)/X(0,Elcuthat,r,0,0)-(60*X(1,Elcuthat,r,0,0)**4*nlo.X1El(0,'SM',Elcuthat,r)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**6
            +(72*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(24*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(2*X(4,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(48*X(1,Elcuthat,r,0,0)**3*nlo.X1El(1,'SM',Elcuthat,r)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(36*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(8*X(3,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(18*X(1,Elcuthat,r,0,0)**2*nlo.X1El(2,'SM',Elcuthat,r)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(8*X(1,Elcuthat,r,0,0)*nlo.X1El(3,'SM',Elcuthat,r)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(nlo.X1El(4,'SM',Elcuthat,r)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(48*X(1,Elcuthat,r,0,0)**3*nlo.X1El(0,'SM',Elcuthat,r)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(36*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(8*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(36*X(1,Elcuthat,r,0,0)**2*nlo.X1El(1,'SM',Elcuthat,r)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*X(1,Elcuthat,r,0,0)*nlo.X1El(2,'SM',Elcuthat,r)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*nlo.X1El(3,'SM',Elcuthat,r)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(18*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r)*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XG(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*nlo.X1El(1,'SM',Elcuthat,r)*XG(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(nlo.X1El(0,'SM',Elcuthat,r)*XG(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +FLAGcf*((12*X(1,Elcuthat,r,0,0)**4*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(18*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(8*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(X(4,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(12*X(1,Elcuthat,r,0,0)**3*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*X(3,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(6*X(1,Elcuthat,r,0,0)**2*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*X(1,Elcuthat,r,0,0)*XG(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +XG(4,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0))+deltamcMS1*((-60*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**4*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**6
            +(48*r*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(72*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(36*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(24*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(8*r*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*r*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(r*X(4,Elcuthat,r,0,1)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(12*r*X(1,Elcuthat,r,0,0)**4*XG(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**5
            -(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            +(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(r*X(4,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(48*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(36*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(36*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*r*X(3,Elcuthat,r,0,1)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(12*r*X(1,Elcuthat,r,0,0)**3*XG(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(4*r*X(3,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*r*X(1,Elcuthat,r,0,0)**2*XG(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(8*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XG(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*r*X(1,Elcuthat,r,0,1)*XG(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(4*r*X(1,Elcuthat,r,0,0)*XG(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(r*X(0,Elcuthat,r,0,1)*XG(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r*XG(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0))+deltambkin1*((24*X(1,Elcuthat,r,0,0)**4*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(60*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**4*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**6
            +(60*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**4*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**6
            -(48*r*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(48*Elcuthat*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,1,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(36*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(72*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(72*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(36*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(36*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,1,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(16*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(24*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(24*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(8*r*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*Elcuthat*X(1,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*Elcuthat*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,1,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*X(4,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*r*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*Elcuthat*X(0,Elcuthat,r,1,0)*X(4,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(r*X(4,Elcuthat,r,0,1)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*X(4,Elcuthat,r,1,0)*XG(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(12*r*X(1,Elcuthat,r,0,0)**4*XG(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**5
            +(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(r*X(4,Elcuthat,r,0,0)*XG(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(12*Elcuthat*X(1,Elcuthat,r,0,0)**4*XG(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**5
            +(18*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XG(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            -(8*Elcuthat*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XG(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(Elcuthat*X(4,Elcuthat,r,0,0)*XG(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(24*X(1,Elcuthat,r,0,0)**3*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(48*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(48*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**3*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(36*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(36*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,1,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(24*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(36*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(36*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*Elcuthat*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,1,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*X(3,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(8*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*Elcuthat*X(0,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*r*X(3,Elcuthat,r,0,1)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*Elcuthat*X(3,Elcuthat,r,1,0)*XG(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(12*r*X(1,Elcuthat,r,0,0)**3*XG(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(4*r*X(3,Elcuthat,r,0,0)*XG(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(12*Elcuthat*X(1,Elcuthat,r,0,0)**3*XG(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            -(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XG(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(4*Elcuthat*X(3,Elcuthat,r,0,0)*XG(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(12*X(1,Elcuthat,r,0,0)**2*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*XG(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*r*X(1,Elcuthat,r,0,0)**2*XG(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(6*Elcuthat*X(1,Elcuthat,r,0,0)**2*XG(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(8*X(1,Elcuthat,r,0,0)*XG(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(8*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XG(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*XG(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*r*X(1,Elcuthat,r,0,1)*XG(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*Elcuthat*X(1,Elcuthat,r,1,0)*XG(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*r*X(1,Elcuthat,r,0,0)*XG(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(4*Elcuthat*X(1,Elcuthat,r,0,0)*XG(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(2*XG(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(r*X(0,Elcuthat,r,0,1)*XG(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*X(0,Elcuthat,r,1,0)*XG(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(r*XG(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)-(Elcuthat*XG(4,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)))
            +flagNLORhoLS*rhoLS*((12*X(1,Elcuthat,r,0,0)**4*nlopw.X1ElRhoLS(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
            -(18*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*nlopw.X1ElRhoLS(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(8*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*nlopw.X1ElRhoLS(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(X(4,Elcuthat,r,0,0)*nlopw.X1ElRhoLS(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(12*X(1,Elcuthat,r,0,0)**3*nlopw.X1ElRhoLS(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(12*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlopw.X1ElRhoLS(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(4*X(3,Elcuthat,r,0,0)*nlopw.X1ElRhoLS(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(6*X(1,Elcuthat,r,0,0)**2*nlopw.X1ElRhoLS(2,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(4*X(1,Elcuthat,r,0,0)*nlopw.X1ElRhoLS(3,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +nlopw.X1ElRhoLS(4,Elcuthat,r)/X(0,Elcuthat,r,0,0)-(60*X(1,Elcuthat,r,0,0)**4*nlo.X1El(0,'SM',Elcuthat,r)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**6
            +(72*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(24*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(2*X(4,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(48*X(1,Elcuthat,r,0,0)**3*nlo.X1El(1,'SM',Elcuthat,r)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(36*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(8*X(3,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(18*X(1,Elcuthat,r,0,0)**2*nlo.X1El(2,'SM',Elcuthat,r)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(8*X(1,Elcuthat,r,0,0)*nlo.X1El(3,'SM',Elcuthat,r)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(nlo.X1El(4,'SM',Elcuthat,r)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(48*X(1,Elcuthat,r,0,0)**3*nlo.X1El(0,'SM',Elcuthat,r)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(36*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(8*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(36*X(1,Elcuthat,r,0,0)**2*nlo.X1El(1,'SM',Elcuthat,r)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*X(1,Elcuthat,r,0,0)*nlo.X1El(2,'SM',Elcuthat,r)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*nlo.X1El(3,'SM',Elcuthat,r)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(18*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r)*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XLS(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*nlo.X1El(1,'SM',Elcuthat,r)*XLS(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(nlo.X1El(0,'SM',Elcuthat,r)*XLS(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +FLAGcs*((12*X(1,Elcuthat,r,0,0)**4*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(18*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(8*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(X(4,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(12*X(1,Elcuthat,r,0,0)**3*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*X(3,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(6*X(1,Elcuthat,r,0,0)**2*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*X(1,Elcuthat,r,0,0)*XLS(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +XLS(4,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0))+deltamcMS1*((-60*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**4*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**6
            +(48*r*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(72*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(36*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(24*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(8*r*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*r*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(r*X(4,Elcuthat,r,0,1)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(12*r*X(1,Elcuthat,r,0,0)**4*XLS(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**5
            -(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            +(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(r*X(4,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(48*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(36*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(36*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*r*X(3,Elcuthat,r,0,1)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(12*r*X(1,Elcuthat,r,0,0)**3*XLS(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(4*r*X(3,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*r*X(1,Elcuthat,r,0,0)**2*XLS(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(8*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XLS(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*r*X(1,Elcuthat,r,0,1)*XLS(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(4*r*X(1,Elcuthat,r,0,0)*XLS(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(r*X(0,Elcuthat,r,0,1)*XLS(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r*XLS(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0))+deltambkin1*((12*X(1,Elcuthat,r,0,0)**4*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(60*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**4*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**6
            +(60*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**4*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**6
            -(48*r*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(48*Elcuthat*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,1,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(18*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(72*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(72*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(36*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(36*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,1,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(8*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(24*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(24*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(8*r*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*Elcuthat*X(1,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*Elcuthat*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,1,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(X(4,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*r*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*Elcuthat*X(0,Elcuthat,r,1,0)*X(4,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(r*X(4,Elcuthat,r,0,1)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*X(4,Elcuthat,r,1,0)*XLS(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(12*r*X(1,Elcuthat,r,0,0)**4*XLS(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**5
            +(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(r*X(4,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(12*Elcuthat*X(1,Elcuthat,r,0,0)**4*XLS(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**5
            +(18*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            -(8*Elcuthat*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(Elcuthat*X(4,Elcuthat,r,0,0)*XLS(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(12*X(1,Elcuthat,r,0,0)**3*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(48*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(48*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**3*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(36*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(36*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,1,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(36*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(36*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*Elcuthat*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,1,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*X(3,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(8*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*Elcuthat*X(0,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*r*X(3,Elcuthat,r,0,1)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*Elcuthat*X(3,Elcuthat,r,1,0)*XLS(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(12*r*X(1,Elcuthat,r,0,0)**3*XLS(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(4*r*X(3,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(12*Elcuthat*X(1,Elcuthat,r,0,0)**3*XLS(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            -(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(4*Elcuthat*X(3,Elcuthat,r,0,0)*XLS(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(6*X(1,Elcuthat,r,0,0)**2*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*XLS(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*r*X(1,Elcuthat,r,0,0)**2*XLS(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(6*Elcuthat*X(1,Elcuthat,r,0,0)**2*XLS(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(4*X(1,Elcuthat,r,0,0)*XLS(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(8*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*XLS(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*XLS(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*r*X(1,Elcuthat,r,0,1)*XLS(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*Elcuthat*X(1,Elcuthat,r,1,0)*XLS(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*r*X(1,Elcuthat,r,0,0)*XLS(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(4*Elcuthat*X(1,Elcuthat,r,0,0)*XLS(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +XLS(4,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0)+(r*X(0,Elcuthat,r,0,1)*XLS(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*X(0,Elcuthat,r,1,0)*XLS(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(r*XLS(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)-(Elcuthat*XLS(4,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)))
            +flagNLOMuPi*mupi*((12*X(1,Elcuthat,r,0,0)**4*nlopw.X1ElMuPi(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
            -(18*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*nlopw.X1ElMuPi(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(8*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*nlopw.X1ElMuPi(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(X(4,Elcuthat,r,0,0)*nlopw.X1ElMuPi(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(12*X(1,Elcuthat,r,0,0)**3*nlopw.X1ElMuPi(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            +(12*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlopw.X1ElMuPi(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(4*X(3,Elcuthat,r,0,0)*nlopw.X1ElMuPi(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(6*X(1,Elcuthat,r,0,0)**2*nlopw.X1ElMuPi(2,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            -(4*X(1,Elcuthat,r,0,0)*nlopw.X1ElMuPi(3,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +nlopw.X1ElMuPi(4,Elcuthat,r)/X(0,Elcuthat,r,0,0)-(60*X(1,Elcuthat,r,0,0)**4*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**6
            +(72*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(24*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(2*X(4,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(48*X(1,Elcuthat,r,0,0)**3*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(36*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(8*X(3,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(18*X(1,Elcuthat,r,0,0)**2*nlo.X1El(2,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(8*X(1,Elcuthat,r,0,0)*nlo.X1El(3,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(nlo.X1El(4,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(48*X(1,Elcuthat,r,0,0)**3*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(36*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(8*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(36*X(1,Elcuthat,r,0,0)**2*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*X(1,Elcuthat,r,0,0)*nlo.X1El(2,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*nlo.X1El(3,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(18*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(nlo.X1El(0,'SM',Elcuthat,r)*Xpi(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +deltamcMS1*((-60*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**4*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**6
            +(48*r*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(72*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(36*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(24*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(8*r*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(2*r*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(r*X(4,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(12*r*X(1,Elcuthat,r,0,0)**4*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**5
            -(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            +(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(r*X(4,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(48*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(36*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(36*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(8*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*r*X(3,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(12*r*X(1,Elcuthat,r,0,0)**3*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(4*r*X(3,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(12*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(6*r*X(1,Elcuthat,r,0,0)**2*Xpi(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(8*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(4*r*X(1,Elcuthat,r,0,1)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(4*r*X(1,Elcuthat,r,0,0)*Xpi(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(r*X(0,Elcuthat,r,0,1)*Xpi(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(r*Xpi(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0))+deltambkin1*((24*X(1,Elcuthat,r,0,0)**4*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(60*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**4*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**6
            +(60*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**4*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**6
            -(48*r*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(48*Elcuthat*X(1,Elcuthat,r,0,0)**3*X(1,Elcuthat,r,1,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(36*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(72*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(72*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(36*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(36*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,1,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(16*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(24*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(24*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(8*r*X(1,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*Elcuthat*X(1,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*Elcuthat*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,1,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*X(4,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(2*r*X(0,Elcuthat,r,0,1)*X(4,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(2*Elcuthat*X(0,Elcuthat,r,1,0)*X(4,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(r*X(4,Elcuthat,r,0,1)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*X(4,Elcuthat,r,1,0)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(12*r*X(1,Elcuthat,r,0,0)**4*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**5
            +(18*r*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(8*r*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(r*X(4,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            -(12*Elcuthat*X(1,Elcuthat,r,0,0)**4*Xpi(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**5
            +(18*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            -(8*Elcuthat*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(Elcuthat*X(4,Elcuthat,r,0,0)*Xpi(0,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            -(24*X(1,Elcuthat,r,0,0)**3*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(48*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**3*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            -(48*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**3*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(36*r*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(36*Elcuthat*X(1,Elcuthat,r,0,0)**2*X(1,Elcuthat,r,1,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(24*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(36*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(36*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,1)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*Elcuthat*X(1,Elcuthat,r,1,0)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,1,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*X(3,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(8*r*X(0,Elcuthat,r,0,1)*X(3,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*Elcuthat*X(0,Elcuthat,r,1,0)*X(3,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*r*X(3,Elcuthat,r,0,1)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*Elcuthat*X(3,Elcuthat,r,1,0)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(12*r*X(1,Elcuthat,r,0,0)**3*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            +(4*r*X(3,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(12*Elcuthat*X(1,Elcuthat,r,0,0)**3*Xpi(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**4
            -(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            +(4*Elcuthat*X(3,Elcuthat,r,0,0)*Xpi(1,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(12*X(1,Elcuthat,r,0,0)**2*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(18*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)**2*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            +(18*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)**2*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*r*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,0,1)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*Elcuthat*X(1,Elcuthat,r,0,0)*X(1,Elcuthat,r,1,0)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(6*r*X(1,Elcuthat,r,0,0)**2*Xpi(2,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**3
            -(6*Elcuthat*X(1,Elcuthat,r,0,0)**2*Xpi(2,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**3
            -(8*X(1,Elcuthat,r,0,0)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(8*r*X(0,Elcuthat,r,0,1)*X(1,Elcuthat,r,0,0)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*Elcuthat*X(0,Elcuthat,r,1,0)*X(1,Elcuthat,r,0,0)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*r*X(1,Elcuthat,r,0,1)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*Elcuthat*X(1,Elcuthat,r,1,0)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(4*r*X(1,Elcuthat,r,0,0)*Xpi(3,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)**2
            +(4*Elcuthat*X(1,Elcuthat,r,0,0)*Xpi(3,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0)**2
            +(2*Xpi(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)+(r*X(0,Elcuthat,r,0,1)*Xpi(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(Elcuthat*X(0,Elcuthat,r,1,0)*Xpi(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(r*Xpi(4,Elcuthat,r,0,1))/X(0,Elcuthat,r,0,0)-(Elcuthat*Xpi(4,Elcuthat,r,1,0))/X(0,Elcuthat,r,0,0))))
        if( flagDEBUG == 1):
            print("Elmoment n. 4 NLO pw = api*",resNLO*par.mbkin**4)
        res += api*resNLO

        resNNLO = 0
        resNNLO +=(flagNLORhoD*(Rhodpert1*((-12*X(1,Elcuthat,r,0,0)**4*nlopw.X1ElRhoD(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
            +(18*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*nlopw.X1ElRhoD(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            -(8*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*nlopw.X1ElRhoD(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(X(4,Elcuthat,r,0,0)*nlopw.X1ElRhoD(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(12*X(1,Elcuthat,r,0,0)**3*nlopw.X1ElRhoD(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            -(12*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlopw.X1ElRhoD(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(4*X(3,Elcuthat,r,0,0)*nlopw.X1ElRhoD(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(6*X(1,Elcuthat,r,0,0)**2*nlopw.X1ElRhoD(2,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(4*X(1,Elcuthat,r,0,0)*nlopw.X1ElRhoD(3,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -nlopw.X1ElRhoD(4,Elcuthat,r)/X(0,Elcuthat,r,0,0))+Rhodpert1*((60*X(1,Elcuthat,r,0,0)**4*nlo.X1El(0,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**6
            -(72*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(24*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(2*X(4,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(48*X(1,Elcuthat,r,0,0)**3*nlo.X1El(1,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(36*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(8*X(3,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(18*X(1,Elcuthat,r,0,0)**2*nlo.X1El(2,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(8*X(1,Elcuthat,r,0,0)*nlo.X1El(3,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(nlo.X1El(4,'SM',Elcuthat,r)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(48*X(1,Elcuthat,r,0,0)**3*nlo.X1El(0,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(36*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(8*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(36*X(1,Elcuthat,r,0,0)**2*nlo.X1El(1,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*X(1,Elcuthat,r,0,0)*nlo.X1El(2,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*nlo.X1El(3,'SM',Elcuthat,r)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(18*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*nlo.X1El(1,'SM',Elcuthat,r)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(nlo.X1El(0,'SM',Elcuthat,r)*XD(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +FLAGcD*((-12*X(1,Elcuthat,r,0,0)**4*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(18*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(8*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(X(4,Elcuthat,r,0,0)*XD(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(12*X(1,Elcuthat,r,0,0)**3*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*X(3,Elcuthat,r,0,0)*XD(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(6*X(1,Elcuthat,r,0,0)**2*XD(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*X(1,Elcuthat,r,0,0)*XD(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -XD(4,Elcuthat,r,0,0)/X(0,Elcuthat,r,0,0))))+flagNLOMuPi*(Mupipert1*((
            -12*X(1,Elcuthat,r,0,0)**4*nlopw.X1ElMuPi(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**5
            +(18*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*nlopw.X1ElMuPi(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            -(8*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*nlopw.X1ElMuPi(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(X(4,Elcuthat,r,0,0)*nlopw.X1ElMuPi(0,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            +(12*X(1,Elcuthat,r,0,0)**3*nlopw.X1ElMuPi(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**4
            -(12*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlopw.X1ElMuPi(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(4*X(3,Elcuthat,r,0,0)*nlopw.X1ElMuPi(1,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -(6*X(1,Elcuthat,r,0,0)**2*nlopw.X1ElMuPi(2,Elcuthat,r))/X(0,Elcuthat,r,0,0)**3
            +(4*X(1,Elcuthat,r,0,0)*nlopw.X1ElMuPi(3,Elcuthat,r))/X(0,Elcuthat,r,0,0)**2
            -nlopw.X1ElMuPi(4,Elcuthat,r)/X(0,Elcuthat,r,0,0))+Mupipert1*((60*X(1,Elcuthat,r,0,0)**4*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**6
            -(72*X(1,Elcuthat,r,0,0)**2*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(24*X(1,Elcuthat,r,0,0)*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(2*X(4,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(48*X(1,Elcuthat,r,0,0)**3*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(36*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(8*X(3,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(18*X(1,Elcuthat,r,0,0)**2*nlo.X1El(2,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(8*X(1,Elcuthat,r,0,0)*nlo.X1El(3,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(nlo.X1El(4,'SM',Elcuthat,r)*Xpi(0,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            -(48*X(1,Elcuthat,r,0,0)**3*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**5
            +(36*X(1,Elcuthat,r,0,0)*X(2,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(8*X(3,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(36*X(1,Elcuthat,r,0,0)**2*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*X(2,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(12*X(1,Elcuthat,r,0,0)*nlo.X1El(2,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*nlo.X1El(3,'SM',Elcuthat,r)*Xpi(1,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(18*X(1,Elcuthat,r,0,0)**2*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**4
            -(12*X(1,Elcuthat,r,0,0)*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(2,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            -(8*X(1,Elcuthat,r,0,0)*nlo.X1El(0,'SM',Elcuthat,r)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**3
            +(4*nlo.X1El(1,'SM',Elcuthat,r)*Xpi(3,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2
            +(nlo.X1El(0,'SM',Elcuthat,r)*Xpi(4,Elcuthat,r,0,0))/X(0,Elcuthat,r,0,0)**2)))
        if( flagDEBUG == 1):
            print("Elmoment n. 4 NNLO from NLO pw = api^2*",resNNLO*par.mbkin**4)
        res += api**2*resNNLO

    return res*par.mbkin**4


