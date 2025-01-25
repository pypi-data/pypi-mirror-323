import numpy as np
from numba import jit, int64, float64, types
from kolya import functions
from kolya.grids.NLOpw import grid_NLO_RhoD_Q2moments
from kolya.grids.NLOpw import grid_NLO_MuG_Q2moments
from kolya.grids.NLOpw import grid_NLO_MuPi_Elmoments
from kolya.grids.NLOpw import grid_NLO_MuG_Elmoments
from kolya.grids.NLOpw import grid_NLO_MuPi_mixmoments
from kolya.grids.NLOpw import grid_NLO_MuG_mixmoments

@jit(float64(int64, float64, float64), nopython=True)
def X1Q2MuG(moment, Q2cut, r):
    """ NLO correction to Mu_G in the SM and on-shell scheme to Q2 moments at arbitray values of r and  Q2_cut
    by use of interpolation grids. 

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

    #due to bad behaviour of the function close to endpoint
    #we construct grids up to 98% of the physical range in q2_cut
    rescalefactor = 0.98

    if (not (rmin<= r <= rmax) ):
        raise ValueError("r value currently not supported: r must be in [",rmin,rmax,"]")
        return 0
    
    mpoints = functions.ChebyshevPoints(rmin, rmax, orderm)

    fvalues = np.zeros(orderm)
    q2values = Q2cut/(1-r)**2*(1-mpoints)**2

    for i in range(orderm):
        fvalues[i] = functions.ChebyshevPolynomial(grid_NLO_MuG_Q2moments.grid_Q2moments[moment][i], 0, rescalefactor*(1-mpoints[i])**2, q2values[i])
    
    coeff = functions.ChebyshevCoefficients(rmin, rmax, orderm, fvalues)
    return functions.ChebyshevPolynomial(coeff, rmin, rmax, r)

@jit(float64(int64, float64, float64), nopython=True)
def X1Q2RhoD(moment, Q2cut, r):
    """ NLO correction to Rho_D in the SM and on-shell scheme to Q2 moments at arbitray values of r and  Q2_cut
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

    #due to bad behaviour of the function close to endpoint
    #we construct grids up to 98% of the physical range in q2_cut
    rescalefactor = 0.98

    if (not (rmin<= r <= rmax) ):
        raise ValueError("r value currently not supported: r must be in [",rmin,rmax,"]")
        return 0
    
    mpoints = functions.ChebyshevPoints(rmin, rmax, orderm)

    fvalues = np.zeros(orderm)
    q2values = Q2cut/(1-r)**2*(1-mpoints)**2

    for i in range(orderm):
        fvalues[i] = functions.ChebyshevPolynomial(grid_NLO_RhoD_Q2moments.grid_Q2moments[moment][i], 0, rescalefactor*(1-mpoints[i])**2, q2values[i])
    
    coeff = functions.ChebyshevCoefficients(rmin, rmax, orderm, fvalues)
    return functions.ChebyshevPolynomial(coeff, rmin, rmax, r)

@jit(float64(int64, float64, float64), nopython=True)
def X1ElMuG(moment, Elcut, r):
    """ NLO correction to Mu_G in the SM and on-shell scheme to El moments at arbitray values of r and  El_cut
    by use of interpolation grids. 

    Parameters
    ----------

    - `moment`: the order of the moment n=0,1,2,3,4
    - `Elcut`: lower cut on El in natural units.
    - `r`: the mass ratio mc/mb
    """
    if (not (0<= Elcut <= (1-r**2)) ):
        raise ValueError("Elcut value out of bound [0,(1-r^2)]")
        return 0
    
    #do not change these values!
    rmin = 1./6.
    rmax = 1./3.
    orderm = 13

    #due to bad behaviour of the function close to endpoint
    #we construct grids up to 95% of the physical range in Elcut
    rescalefactor = 0.95

    if (not (rmin<= r <= rmax) ):
        raise ValueError("r value currently not supported: r must be in [",rmin,rmax,"]")
        return 0
    
    mpoints = functions.ChebyshevPoints(rmin, rmax, orderm)

    fvalues = np.zeros(orderm)
    Elvalues = Elcut/(1-r**2)*(1-mpoints**2)

    for i in range(orderm):
        fvalues[i] = functions.ChebyshevPolynomial(grid_NLO_MuG_Elmoments.grid_Elmoments[moment][i], 0, rescalefactor*(1-mpoints[i]**2)/2, Elvalues[i])
    
    coeff = functions.ChebyshevCoefficients(rmin, rmax, orderm, fvalues)
    return functions.ChebyshevPolynomial(coeff, rmin, rmax, r)

@jit(float64(int64, float64, float64), nopython=True)
def X1ElMuPi(moment, Elcut, r):
    """ NLO correction to Mu_Pi in the SM and on-shell scheme to El moments at arbitray values of r and  El_cut
    by use of interpolation grids. 

    Parameters
    ----------

    - `moment`: the order of the moment n=0,1,2,3,4
    - `Elcut`: lower cut on El in natural units.
    - `r`: the mass ratio mc/mb
    """
    if (not (0<= Elcut <= (1-r**2)) ):
        raise ValueError("Elcut value out of bound [0,(1-r^2)]")
        return 0
    
    #do not change these values!
    rmin = 1./6.
    rmax = 1./3.
    orderm = 13

    #due to bad behaviour of the function close to endpoint
    #we construct grids up to 95% of the physical range in Elcut
    rescalefactor = 0.95

    if (not (rmin<= r <= rmax) ):
        raise ValueError("r value currently not supported: r must be in [",rmin,rmax,"]")
        return 0
    
    mpoints = functions.ChebyshevPoints(rmin, rmax, orderm)

    fvalues = np.zeros(orderm)
    Elvalues = Elcut/(1-r**2)*(1-mpoints**2)

    for i in range(orderm):
        fvalues[i] = functions.ChebyshevPolynomial(grid_NLO_MuPi_Elmoments.grid_Elmoments[moment][i], 0, rescalefactor*(1-mpoints[i]**2)/2, Elvalues[i])
    
    coeff = functions.ChebyshevCoefficients(rmin, rmax, orderm, fvalues)
    return functions.ChebyshevPolynomial(coeff, rmin, rmax, r)

@jit(float64(int64, float64, float64), nopython=True)
def X1ElRhoD(moment, Elcut, r):
    """ NLO correction to Rho_D in the SM and on-shell scheme to El moments at arbitray values of r and  El_cut
    by use of interpolation grids. (Currently unknown so the function returns 0!)

    Parameters
    ----------

    - `moment`: the order of the moment n=0,1,2,3,4
    - `Elcut`: lower cut on El in natural units.
    - `r`: the mass ratio mc/mb
    """

    return 0

@jit(float64(int64, float64, float64), nopython=True)
def X1ElRhoLS(moment, Elcut, r):
    """ NLO correction to Rho_LS in the SM and on-shell scheme to El moments at arbitray values of r and  El_cut
    by use of interpolation grids. (Currently unknown so the function returns 0!)

    Parameters
    ----------

    - `moment`: the order of the moment n=0,1,2,3,4
    - `Elcut`: lower cut on El in natural units.
    - `r`: the mass ratio mc/mb
    """

    return 0

@jit(float64(int64, int64, float64, float64), nopython=True)
def X1mixMuPi(moment, moment2, Elcut, r):
    """ NLO correction to Mu_Pi in the SM and on-shell scheme to mix moments at arbitray values of r and  El_cut
    by use of interpolation grids. 

    Parameters
    ----------

    - `moment`: the order of the moment q2^n with n=0,1,2,3,4
    - `moment2`: the order of the moment q0^n with n=0,1,2,3,4
    - `Elcut`: lower cut on El in natural units.
    - `r`: the mass ratio mc/mb
    """
    if (not (0<= Elcut <= (1-r**2)) ):
        raise ValueError("Elcut value out of bound [0,(1-r^2)]")
        return 0
    
    #do not change these values!
    rmin = 1./6.
    rmax = 1./3.
    orderm = 13

    #due to bad behaviour of the function close to endpoint
    #we construct grids up to 95% of the physical range in Elcut
    rescalefactor = 0.95

    if (not (rmin<= r <= rmax) ):
        raise ValueError("r value currently not supported: r must be in [",rmin,rmax,"]")
        return 0
    
    mpoints = functions.ChebyshevPoints(rmin, rmax, orderm)

    fvalues = np.zeros(orderm)
    Elvalues = Elcut/(1-r**2)*(1-mpoints**2)

    for i in range(orderm):
        fvalues[i] = functions.ChebyshevPolynomial(grid_NLO_MuPi_mixmoments.grid_mixmoments[moment][moment2][i], 0, rescalefactor*(1-mpoints[i]**2)/2, Elvalues[i])
    
    coeff = functions.ChebyshevCoefficients(rmin, rmax, orderm, fvalues)
    return functions.ChebyshevPolynomial(coeff, rmin, rmax, r)

@jit(float64(int64, int64, float64, float64), nopython=True)
def X1mixMuG(moment, moment2, Elcut, r):
    """ NLO correction to Mu_G in the SM and on-shell scheme to mix moments at arbitray values of r and  El_cut
    by use of interpolation grids. 

    Parameters
    ----------

    - `moment`: the order of the moment q2^n with n=0,1,2,3,4
    - `moment2`: the order of the moment q0^n with n=0,1,2,3,4
    - `Elcut`: lower cut on El in natural units.
    - `r`: the mass ratio mc/mb
    """
    if (not (0<= Elcut <= (1-r**2)) ):
        raise ValueError("Elcut value out of bound [0,(1-r^2)]")
        return 0
    
    #do not change these values!
    rmin = 1./6.
    rmax = 1./3.
    orderm = 13

    #due to bad behaviour of the function close to endpoint
    #we construct grids up to 95% of the physical range in Elcut
    rescalefactor = 0.95

    if (not (rmin<= r <= rmax) ):
        raise ValueError("r value currently not supported: r must be in [",rmin,rmax,"]")
        return 0
    
    mpoints = functions.ChebyshevPoints(rmin, rmax, orderm)

    fvalues = np.zeros(orderm)
    Elvalues = Elcut/(1-r**2)*(1-mpoints**2)

    for i in range(orderm):
        fvalues[i] = functions.ChebyshevPolynomial(grid_NLO_MuG_mixmoments.grid_mixmoments[moment][moment2][i], 0, rescalefactor*(1-mpoints[i]**2)/2, Elvalues[i])
    
    coeff = functions.ChebyshevCoefficients(rmin, rmax, orderm, fvalues)
    return functions.ChebyshevPolynomial(coeff, rmin, rmax, r)

@jit(float64(int64, int64, float64, float64), nopython=True)
def X1mixRhoD(moment, moment2, Elcut, r):
    """ NLO correction to RhoD in the SM and on-shell scheme to mix moments at arbitray values of r and  El_cut
    by use of interpolation grids. (Currently unknown so the function returns 0!)

    Parameters
    ----------

    - `moment`: the order of the moment q2^n with n=0,1,2,3,4
    - `moment2`: the order of the moment q0^n with n=0,1,2,3,4
    - `Elcut`: lower cut on El in natural units.
    - `r`: the mass ratio mc/mb
    """
    return 0

@jit(float64(int64, int64, float64, float64), nopython=True)
def X1mixRhoLS(moment, moment2, Elcut, r):
    """ NLO correction to RhoLS in the SM and on-shell scheme to mix moments at arbitray values of r and  El_cut
    by use of interpolation grids. (Currently unknown so the function returns 0!)

    Parameters
    ----------

    - `moment`: the order of the moment q2^n with n=0,1,2,3,4
    - `moment2`: the order of the moment q0^n with n=0,1,2,3,4
    - `Elcut`: lower cut on El in natural units.
    - `r`: the mass ratio mc/mb
    """
    return 0

