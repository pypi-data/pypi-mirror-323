import numpy as np
from numba import jit, int64, float64
from kolya import functions
from kolya.grids.NNLOpartonic import grid_BLM_Elmoments
from kolya.grids.NNLOpartonic import grid_BLM_mixmoments
from kolya.grids.NNLOpartonic import grid_NNLO_Q2moments

@jit(float64(int64, float64, float64), cache=True, nopython=True)
def X2Q2(moment, Q2cut, r):
    """ NNLO partonic correction in the SM to Q2 moments at arbitray values of r and  Q2_cut
    by use of interpolation grids

    Parameters
    ----------

    - `moment`: the order of the moment n=0,1,2,3,4
    - `Q2cut`: lower cut on Q2 in natural units.
    - `r`: the mass ratio mc/mb
    """
    if (not (0<= Q2cut <= (1-r)**2) ):
        raise ValueError("Q2_cut value out of bound [0,(1-r)^2]")
        return 0
    
    #do not change these values!
    rmin = 1./6.
    rmax = 1./3.
    orderm = 13

    if (not (rmin<= r <= rmax) ):
        raise ValueError("r value currently not supported: r must be in [",rmin,rmax,"]")
        return 0
    
    mpoints = functions.ChebyshevPoints(rmin, rmax, orderm)

    fvalues = np.zeros(orderm)
    q2values = Q2cut/(1-r)**2*(1-mpoints)**2

    for i in range(orderm):
        fvalues[i] = functions.ChebyshevPolynomial(grid_NNLO_Q2moments.grid_Q2moments[moment][i], 0, (1-mpoints[i])**2, q2values[i])
    
    coeff = functions.ChebyshevCoefficients(rmin, rmax, orderm, fvalues)
    return functions.ChebyshevPolynomial(coeff, rmin, rmax, r)

@jit(float64(int64, float64, float64), cache=True, nopython=True)
def X2ElBLM(moment, Elcut, r):
    """ NNLO BLM partonic correction in the SM to El moments at arbitray values of r and  El_cut
    by use of interpolation grids

    Parameters
    ----------

    - `moment`: the order of the moment n=1,2,3,4
    - `Elcut`: lower cut on El in natural units.
    - `r`: the mass ratio mc/mb
    """
    if (not (0<= Elcut <= (1-r**2)/2) ):
        raise ValueError("El_cut value out of bound [0,(1-r^2)/2]")
        return 0
    
    #do not change these values!
    rmin = 1./6.
    rmax = 1./3.
    orderm = 13

    if (not (rmin<= r <= rmax) ):
        raise ValueError("r value currently not supported: r must be in [",rmin,rmax,"]")
        return 0
    
    mpoints = functions.ChebyshevPoints(rmin, rmax, orderm)

    fvalues = np.zeros(orderm)
    Elvalues = Elcut/(1-r**2)*(1-mpoints**2)

    for i in range(orderm):
        fvalues[i] = functions.ChebyshevPolynomial(grid_BLM_Elmoments.grid_BLM_Elmoments[moment][i], 0, (1-mpoints[i]**2)/2, Elvalues[i])
    
    coeff = functions.ChebyshevCoefficients(rmin, rmax, orderm, fvalues)
    return functions.ChebyshevPolynomial(coeff, rmin, rmax, r)

@jit(float64(int64, float64, float64), cache=True, nopython=True)
def X2ElnonBLM(moment, Elcut, r):
    """ NNLO nonBLM partonic correction in the SM to El moments at arbitray values of r and  El_cut
    by use of interpolation grids

    Parameters
    ----------

    - `moment`: the order of the moment n=1,2,3,4
    - `Elcut`: lower cut on El in natural units.
    - `r`: the mass ratio mc/mb
    """
    if (not (0<= Elcut <= (1-r**2)/2) ):
        raise ValueError("El_cut value out of bound [0,(1-r^2)/2]")
        return 0
    
    #do not change these values!
    rmin = 0.2
    rmax = 1./3.
    orderm = 11

    if (not (rmin<= r <= rmax) ):
        raise ValueError("r value currently not supported: r must be in [",rmin,rmax,"]")
        return 0
    
    #Ldef00 = 1 - 8*(r**2) + 8*(r**6) - r**8 + 12*(r**4)*np.log(1/r**2)
    #nonBLM = []
    #xi =2*Elcut

    #nonBLM.append(Ldef00*(6.37845 - 11.9464*r + (-0.253645 + 1.43042*r)*xi + (11.3464 - 55.3957*r)*xi**2 + (-89.8547 + 346.146*r)*xi**3 + (146.476 - 575.716*r)*xi**4 + (-71.8734 + 284.144*r)*xi**5))
    #nonBLM.append(Ldef00*( 2.39453 - 5.12195*r + (-0.206895 + 0.979901*r)*xi + (-0.7126 + 1.22294*r)*xi**2 + (15.5098 - 59.7789*r)*xi**3 + (-55.3289 + 206.401*r)*xi**4 + (47.1612 - 178.571*r)*xi**5))
    #nonBLM.append(Ldef00*( 0.957906 - 2.23792*r + (-0.495481 + 1.62156*r)*xi + (6.57586 - 21.3014*r)*xi**2 + (-28.8398 + 93.4803*r)*xi**3 + (49.8075 - 164.098*r)*xi**4 + (-30.3741 + 99.9346*r)*xi**5))
    #nonBLM.append(Ldef00*( 0.397317 - 0.988273*r + (-0.0638918 + 0.302701*r)*xi + (1.06109 - 4.93022*r)*xi**2 + (-5.25769 + 24.1057*r)*xi**3 + (9.87631 - 44.9729*r)*xi**4 + (-6.55612 + 28.6761*r)*xi**5))
    #nonBLM.append(0)
    
    return 0

@jit(float64(int64, float64, float64), cache=True, nopython=True)
def X2El(moment, Elcut, r):
    """ NNLO partonic correction in the SM to El moments at arbitray values of r and  El_cut
    by use of interpolation grids

    Parameters
    ----------

    - `moment`: the order of the moment n=1,2,3,4
    - `Elcut`: lower cut on El in natural units.
    - `r`: the mass ratio mc/mb
    """
    if (not (0<= Elcut <= (1-r**2)/2) ):
        raise ValueError("El_cut value out of bound [0,(1-r^2)/2]")
        return 0
    
    #do not change these values!
    rmin = 0.2
    rmax = 1./3.
    orderm = 11

    if (not (rmin<= r <= rmax) ):
        raise ValueError("r value currently not supported: r must be in [",rmin,rmax,"]")
        return 0
    
    BLMpart = X2ElBLM(moment, Elcut, r) 

    beta0 = 9

    return 0

@jit(float64(int64, int64, float64, float64), cache=True, nopython=True)
def X2mixBLM(moment, moment2, Elcut, r):
    """ BLM NNLO partonic correction to mix moments in the SM at arbitray values of r and  El_cut
    by use of interpolation grids. Used in the prediction of MX moments.
    These are moments with of

    (Q2)^moment (q0)^moment2 with i+j<=4

    Parameters
    ----------

    - `moment`: the order of the moment Q2 n=1,2,3,4
    - `moment2`: the order of the moment q0 n=1,2,3,4
    - `Elcut`: lower cut on El in natural units.
    - `r`: the mass ratio mc/mb
    """
    if (not (0<= Elcut <= (1-r**2)/2) ):
        raise ValueError("El_cut value out of bound [0,(1-r^2)/2]")
        return 0
    
    #do not change these values!
    rmin = 1./6.
    rmax = 1./3.
    orderm = 13

    if (not (rmin<= r <= rmax) ):
        raise ValueError("r value currently not supported: r must be in [",rmin,rmax,"]")
        return 0
    
    mpoints = functions.ChebyshevPoints(rmin, rmax, orderm)

    fvalues = np.zeros(orderm)
    Elvalues = Elcut/(1-r**2)*(1-mpoints**2)

    for i in range(orderm):
        fvalues[i] = functions.ChebyshevPolynomial(grid_BLM_mixmoments.grid_mixmoments[moment][moment2][i], 0, (1-mpoints[i]**2)/2, Elvalues[i])
    
    coeff = functions.ChebyshevCoefficients(rmin, rmax, orderm, fvalues)
    return functions.ChebyshevPolynomial(coeff, rmin, rmax, r)

@jit(float64(int64, int64, float64, float64), cache=True, nopython=True)
def X2mixnonBLM(moment, moment2, Elcut, r):
    """ Non-BLM NNLO partonic correction to mix moments in the SM at arbitray values of r and  El_cut
    by use of interpolation grids. Used in the prediction of MX moments.
    These are moments with of

    (Q2)^moment (q0)^moment2 with i+j<=4

    Parameters
    ----------

    - `moment`: the order of the moment Q2 n=1,2,3,4
    - `moment2`: the order of the moment q0 n=1,2,3,4
    - `Elcut`: lower cut on El in natural units.
    - `r`: the mass ratio mc/mb
    """
    if (not (0<= Elcut <= (1-r**2)/2) ):
        raise ValueError("El_cut value out of bound [0,(1-r^2)/2]")
        return 0
    
    #do not change these values!
    rmin = 0.2
    rmax = 1./3.
    orderm = 11

    if (not (rmin<= r <= rmax) ):
        raise ValueError("r value currently not supported: r must be in [",rmin,rmax,"]")
        return 0
    
    return 0.

@jit(float64(int64, int64, float64, float64), cache=True, nopython=True)
def X2mix(moment, moment2, Elcut, r):
    """ NNLO partonic correction to mix moments in the SM at arbitray values of r and  El_cut
    by use of interpolation grids. Used in the prediction of MX moments.
    These are moments with of

    (Q2)^moment (q0)^moment2 with i+j<=4

    Parameters
    ----------

    - `moment`: the order of the moment Q2 n=1,2,3,4
    - `moment2`: the order of the moment q0 n=1,2,3,4
    - `Elcut`: lower cut on El in natural units.
    - `r`: the mass ratio mc/mb
    """
    if (not (0<= Elcut <= (1-r**2)/2) ):
        raise ValueError("El_cut value out of bound [0,(1-r^2)/2]")
        return 0

    #do not change these values!
    rmin = 0.2
    rmax = 1./3.
    orderm = 11

    if (not (rmin<= r <= rmax) ):
        raise ValueError("r value currently not supported: r must be in [",rmin,rmax,"]")
        return 0

    BLMpart = X2mixBLM(moment, moment2, Elcut, r)
    beta0 = 9

    return beta0*BLMpart


@jit(float64(int64, float64, float64), cache=True, nopython=True)
def fitElNNLOnonBLM(moment, Elcut, r):
    xi = 2*Elcut

    nonBLM = []
    nonBLM.append(((-4.34578+11.2536*r)*(-1+r**2+xi)+(-24.3165
        +62.6943*r)*(-1+r**2+xi)**2+(-59.2717+157.189*r)*(
        -1+r**2+xi)**3+(-64.6476+177.598*r)*(-1+r**2
        +xi)**4+(-25.6166+72.5719*r)*(-1+r**2+xi)**5))
    nonBLM.append(((1.41581-4.54877*r)*(-1+r**2+xi)+(11.0718
        -36.8932*r)*(-1+r**2+xi)**2+(29.3621-100.357*r)*(
        -1+r**2+xi)**3+(32.2839-112.338*r)*(-1+r**2
        +xi)**4+(12.6108-44.4667*r)*(-1+r**2+xi)**5))
    nonBLM.append(((-0.288623+1.70896*r)*(-1+r**2+xi)+(-4.48723
        +21.5218*r)*(-1+r**2+xi)**2+(-14.6717+67.0648*r)*(
        -1+r**2+xi)**3+(-17.7173+79.3438*r)*(-1+r**2
        +xi)**4+(-7.27568+32.2309*r)*(-1+r**2+xi)**5))
    nonBLM.append(0)

    return nonBLM[moment-1]

@jit(float64(int64, float64, float64), cache=True, nopython=True)
def fitMXNNLOnonBLM(moment, Elcut, r):
    xi = 2*Elcut

    nonBLM = []
    nonBLM.append(xi**5 *(33.1268 - 97.4937*r) + xi**4 *(224.824*r - 71.1566) + 
        xi**3 *(49.0107 - 160.897*r) + xi**2 *(37.7202*r - 10.9241) + 
        xi *(0.731719 - 2.55793*r) + 2.08146*r - 0.916165)
    nonBLM.append(0)
    nonBLM.append(0)
    nonBLM.append(0)
    
    return nonBLM[moment-1]