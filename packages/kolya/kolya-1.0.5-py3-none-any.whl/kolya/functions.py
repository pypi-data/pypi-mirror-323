import numpy as np
from numba import jit


@jit(cache=True, nopython=True)
def ChebyshevPoints(a, b, n):
    cos = np.linspace(1,n,n)
    cos = np.cos(np.pi*(2*cos-1)/2/n)
    return (a+b)/2+cos*(b-a)/2
    

@jit(cache=True, nopython=True)
def ChebyshevCoefficients(a, b, n, fpoints):
    c = np.zeros(n)
    for i in range(n):
        for j in range(n):
            cos = np.cos((2*j+1)*i*np.pi/2/n)
            c[i] += fpoints[j]*cos
            #print("i = ",i," j = ",j," cos = ",cos," c[",i,"] = ", c[i])
    return 2*c/n


@jit(cache=True, nopython=True)
def ChebyshevPolynomial(c, a, b, s):
    x = (2*s-a-b)/(b-a)
    d = 0.
    dd = 0.
    for i in range(c.size-1,0,-1):
        sv = d
        d = 2*x*d-dd+c[i]
        dd = sv
        #print(" i = ",i," d = ",d," dd = ",dd)
    return x*d-dd+c[0]/2
   

