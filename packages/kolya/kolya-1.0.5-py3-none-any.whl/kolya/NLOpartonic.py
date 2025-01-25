import numpy as np
from numba import jit, int64, float64, types
from kolya import functions
from kolya.grids.NLOpartonic import grid_np_Q2moments
from kolya.grids.NLOpartonic import grid_np_Elmoments
from kolya.grids.NLOpartonic import grid_np_mixmoments
from kolya.grids.NLOpartonic import grid_SM_Q2moments_DerivativeQ2
from kolya.grids.NLOpartonic import grid_SM_Q2moments_Derivativer
from kolya.grids.NLOpartonic import grid_SM_Elmoments_DerivativeEl
from kolya.grids.NLOpartonic import grid_SM_Elmoments_Derivativer
from kolya.grids.NLOpartonic import grid_SM_mixmoments_DerivativeEl
from kolya.grids.NLOpartonic import grid_SM_mixmoments_Derivativer

@jit(float64(int64, types.unicode_type, float64, float64), cache=True, nopython=True)
def X1Q2(moment, cNP, Q2cut, r):
    """ NLO partonic correction to Q2 moments at arbitray values of r and Q2_cut
    by use of interpolation grids

    Parameters
    ----------

    - `moment`: the order of the moment n=1,2,3,4
    - `cNP`: a string to specify the NP contribution. Possible values are
            'SM', 'VL', 'VR', 'SL2', 'SR2', 'VL2', 'SLSR', 'VR2', 'VLVR', 'SLT', 'T2' 
    - `Q2cut`: lower cut on Q2 in natural units.
    - `r`: the mass ratio mc/mb
    """
    if (not (0<= Q2cut <= (1-r)**2) ):
        raise ValueError("Q2cut value out of bound [0,(1-r)^2]")
        return 0
    
    #do not change these values!
    rmin = 1./6.
    rmax = 1./3.
    orderm = 13

    if (not (rmin<= r <= rmax) ):
        raise ValueError("r value currently not supported: r must be in [",rmin,rmax,"]")
        return 0
    
    # Dictionary to grid elements relative to each NP contribution
    # Note that SR*T has no alphas contribution
    wc = {'SM': 0,'VL': 1,'VR': 2,'SL2': 3,'SR2': 4,'VL2': 5,'SLSR': 6,'VR2': 7,'VLVR': 8,'SLT': 9,'T2': 10}
    
    mpoints = functions.ChebyshevPoints(rmin, rmax, orderm)

    fvalues = np.zeros(orderm)
    q2values = Q2cut/(1-r)**2*(1-mpoints)**2

    for i in range(orderm):
        #fvalues[i] = functions.ChebyshevPolynomial(grid_Q2moments[wc[cNP]][moment][i], 0, (1-mpoints[i])**2, q2values[i])
        fvalues[i] = functions.ChebyshevPolynomial(grid_np_Q2moments.grid_Q2moments[wc[cNP]][moment][i], 0, (1-mpoints[i])**2, q2values[i])
    
    coeff = functions.ChebyshevCoefficients(rmin, rmax, orderm, fvalues)
    return functions.ChebyshevPolynomial(coeff, rmin, rmax, r)

# The function return the NLO correction to El moments at arbitray values of r and El_cut
# by interpolation of the grid
@jit(float64(int64, types.unicode_type, float64, float64), cache=True, nopython=True)
def X1El(moment, cNP, Elcut, r):
    """ NLO partonic correction to El moments at arbitray values of r and  El_cut
    by use of interpolation grids

    Parameters
    ----------

    - `moment`: the order of the moment n=1,2,3,4
    - `cNP`: a string to specify the NP contribution. Possible values are
            'SM', 'VL', 'VR', 'SL2', 'SR2', 'VL2', 'SLSR', 'VR2', 'VLVR', 'SLT', 'T2' 
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
    
    # Dictionary to grid elements relative to each NP contribution
    # Note that SR*T has no alphas contribution
    wc = {'SM': 0,'VL': 1,'VR': 2,'SL2': 3,'SR2': 4,'VL2': 5,'SLSR': 6,'VR2': 7,'VLVR': 8,'SLT': 9,'T2': 10}
    
    mpoints = functions.ChebyshevPoints(rmin, rmax, orderm)

    fvalues = np.zeros(orderm)
    Elvalues = Elcut/(1-r**2)*(1-mpoints**2)

    for i in range(orderm):
        fvalues[i] = functions.ChebyshevPolynomial(grid_np_Elmoments.grid_Elmoments[wc[cNP]][moment][i], 0, (1-mpoints[i]**2)/2, Elvalues[i])
    
    coeff = functions.ChebyshevCoefficients(rmin, rmax, orderm, fvalues)
    return functions.ChebyshevPolynomial(coeff, rmin, rmax, r)

@jit(float64(int64, int64, types.unicode_type, float64, float64), nopython=True)
def X1mix(moment, moment2, cNP, Elcut, r):
    """ NLO partonic correction to mix moments at arbitray values of r and  El_cut
    by use of interpolation grids. Used in the prediction of MX moments.
    These are moments with of

    (Q2)^moment (q0)^moment2 with i+j<4

    Parameters
    ----------

    - `moment`: the order of the moment Q2 n=1,2,3,4
    - `moment2`: the order of the moment q0 n=1,2,3,4
    - `cNP`: a string to specify the NP contribution. Possible values are
            'SM', 'VL', 'VR', 'SL2', 'SR2', 'VL2', 'SLSR', 'VR2', 'VLVR', 'SLT', 'T2' 
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

    # Dictionary to grid elements relative to each NP contribution
    # Note that SR*T has no alphas contribution
    wc = {'SM': 0,'VL': 1,'VR': 2,'SL2': 3,'SR2': 4,'VL2': 5,'SLSR': 6,'VR2': 7,'VLVR': 8,'SLT': 9,'T2': 10}
    
    mpoints = functions.ChebyshevPoints(rmin, rmax, orderm)

    fvalues = np.zeros(orderm)
    Elvalues = Elcut/(1-r**2)*(1-mpoints**2)

    for i in range(orderm):
        fvalues[i] = functions.ChebyshevPolynomial(grid_np_mixmoments.grid_mixmoments[wc[cNP]][moment][moment2][i], 0, (1-mpoints[i]**2)/2, Elvalues[i])
    
    coeff = functions.ChebyshevCoefficients(rmin, rmax, orderm, fvalues)
    return functions.ChebyshevPolynomial(coeff, rmin, rmax, r)

# The function return the derivative w.r.t. El of the 
# NLO correction to El moments in the SM at arbitray values of r and El_cut
# by interpolation of the grid.
@jit(float64(int64, float64, float64), cache=True, nopython=True)
def X1El_DerivativeEl(moment, Elcut, r):
    """ Derivative w.r.t. El of the NLO partonic correction in the SM
    to El moments at arbitray values of r and  El_cut
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
        fvalues[i] = functions.ChebyshevPolynomial(grid_SM_Elmoments_DerivativeEl.grid_Elmoments_DerivativeEl[moment][i], 0, (1-mpoints[i]**2)/2, Elvalues[i])
    
    coeff = functions.ChebyshevCoefficients(rmin, rmax, orderm, fvalues)
    return functions.ChebyshevPolynomial(coeff, rmin, rmax, r)

# The function return the derivative w.r.t. r=mc/mb of the 
# NLO correction to El moments in the SM at arbitray values of r and El_cut
# by interpolation of the grid.
@jit(float64(int64, float64, float64), cache=True, nopython=True)
def X1El_Derivativer(moment, Elcut, r):
    """ Derivative w.r.t. r=mc/mb of the NLO partonic correction in the SM
    to El moments at arbitray values of r and  El_cut
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
        fvalues[i] = functions.ChebyshevPolynomial(grid_SM_Elmoments_Derivativer.grid_Elmoments_Derivativer[moment][i], 0, (1-mpoints[i]**2)/2, Elvalues[i])
    
    coeff = functions.ChebyshevCoefficients(rmin, rmax, orderm, fvalues)
    return functions.ChebyshevPolynomial(coeff, rmin, rmax, r)

@jit(float64(int64, int64, float64, float64), cache=True, nopython=True)
def X1mix_DerivativeEl(moment, moment2, Elcut, r):
    """ Derivative w.r.t. El of the NLO partonic correction in the SM
    to mix moments at arbitray values of r and  El_cut
    by use of interpolation grids. Used in the prediction of MX moments.
    These are moments with of

    (Q2)^moment (q0)^moment2 with i+j<4

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
        fvalues[i] = functions.ChebyshevPolynomial(grid_SM_mixmoments_DerivativeEl.grid_mixmoments_DerivativeEl[moment][moment2][i], 0, (1-mpoints[i]**2)/2, Elvalues[i])
    
    coeff = functions.ChebyshevCoefficients(rmin, rmax, orderm, fvalues)
    return functions.ChebyshevPolynomial(coeff, rmin, rmax, r)

@jit(float64(int64, int64, float64, float64), cache=True, nopython=True)
def X1mix_Derivativer(moment, moment2, Elcut, r):
    """ Derivative w.r.t. r of the NLO partonic correction in the SM
    to mix moments at arbitray values of r and  El_cut
    by use of interpolation grids. Used in the prediction of MX moments.
    These are moments with of

    (Q2)^moment (q0)^moment2 with i+j<4

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
        fvalues[i] = functions.ChebyshevPolynomial(grid_SM_mixmoments_Derivativer.grid_mixmoments_Derivativer[moment][moment2][i], 0, (1-mpoints[i]**2)/2, Elvalues[i])
    
    coeff = functions.ChebyshevCoefficients(rmin, rmax, orderm, fvalues)
    return functions.ChebyshevPolynomial(coeff, rmin, rmax, r)

@jit(float64(int64, float64, float64), cache=True, nopython=True)
def X1Q2_DerivativeQ2(moment, Q2cut, r):
    """ Derivative w.r.t. Q2cut of the 
    NLO partonic correction in the SM to Q2 moments at arbitray values of r and Q2_cut
    by use of interpolation grids

    Parameters
    ----------

    - `moment`: the order of the moment n=1,2,3,4
    - `Q2cut`: lower cut on Q2 in natural units.
    - `r`: the mass ratio mc/mb
    """
    if (not (0<= Q2cut <= (1-r)**2) ):
        raise ValueError("Q2cut value out of bound [0,(1-r)^2]")
        return 0
    
    #do not change these values!
    rmin = 1/6.
    rmax = 1./3.
    orderm = 13

    if (not (rmin<= r <= rmax) ):
        raise ValueError("r value currently not supported: r must be in [",rmin,rmax,"]")
        return 0
    
    mpoints = functions.ChebyshevPoints(rmin, rmax, orderm)

    fvalues = np.zeros(orderm)
    q2values = Q2cut/(1-r)**2*(1-mpoints)**2

    for i in range(orderm):
        fvalues[i] = functions.ChebyshevPolynomial(grid_SM_Q2moments_DerivativeQ2.grid_Q2moments_DerivativeQ2[moment][i], 0, (1-mpoints[i])**2, q2values[i])
    
    coeff = functions.ChebyshevCoefficients(rmin, rmax, orderm, fvalues)
    return functions.ChebyshevPolynomial(coeff, rmin, rmax, r)

@jit(float64(int64, float64, float64), cache=True, nopython=True)
def X1Q2_Derivativer(moment, Q2cut, r):
    """ Derivative w.r.t. r of the 
    NLO partonic correction in the SM to Q2 moments at arbitray values of r and Q2_cut
    by use of interpolation grids

    Parameters
    ----------

    - `moment`: the order of the moment n=1,2,3,4
    - `Q2cut`: lower cut on Q2 in natural units.
    - `r`: the mass ratio mc/mb
    """
    if (not (0<= Q2cut <= (1-r)**2) ):
        raise ValueError("Q2cut value out of bound [0,(1-r)^2]")
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
        fvalues[i] = functions.ChebyshevPolynomial(grid_SM_Q2moments_Derivativer.grid_Q2moments_Derivativer[moment][i], 0, (1-mpoints[i])**2, q2values[i])
    
    coeff = functions.ChebyshevCoefficients(rmin, rmax, orderm, fvalues)
    return functions.ChebyshevPolynomial(coeff, rmin, rmax, r)

if __name__ == '__main__':
    for i in range(0,5):
        print("i = ",i,X1Q2(i, 'SM', 0., 0.25))