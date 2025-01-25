import math
from kolya import parameters
from kolya import schemechange_KINMS
from kolya import interface_rundec

def mupi2mupi(mupi_scale1, scale1, scale_mus, scale2):
    """mupi2mupi computes mu_pi(scale2) for B mesons from 
    the knowledge of mupi(scale1) with alpha_s(scale_mus). 
    It employs scheme (B) as defined in 2011.11655 [hep-ph]. """
    
    api = interface_rundec.as3(scale_mus)/math.pi

    par1 = parameters.physical_parameters(scale_alphas=scale_mus, scale_mbkin=scale1)
    par2 = parameters.physical_parameters(scale_alphas=scale_mus, scale_mbkin=scale2)

    mupi_scale2 = mupi_scale1 
    for i in [1,2,3]:
        mupi_scale2 += api**i*(schemechange_KINMS.MuPiPert(i,par2) - schemechange_KINMS.MuPiPert(i,par1))

    return mupi_scale2

def rhoD2rhoD(rhoD_scale1, scale1, scale_mus, scale2):
    """rhoD2rhoD computes rho_D(scale2) for B mesons from 
    the knowledge of rho_D(scale1) with alpha_s(scale_mus). 
    It employs scheme (B) as defined in 2011.11655 [hep-ph]. """
        
    api = interface_rundec.as3(scale_mus)/math.pi

    par1 = parameters.physical_parameters(scale_alphas=scale_mus, scale_mbkin=scale1)
    par2 = parameters.physical_parameters(scale_alphas=scale_mus, scale_mbkin=scale2)

    rhoD_scale2 = rhoD_scale1 
    for i in [1,2,3]:
        rhoD_scale2 += api**i*(schemechange_KINMS.RhoDPert(i,par2) - schemechange_KINMS.RhoDPert(i,par1))

    return rhoD_scale2

if __name__ == '__main__':
    print(mupi2mupi(0.45,1.0, 4.562481357, 0.75))
    print(mupi2mupi(0.45,1.0, 4.562481357, 1.25))
    print(rhoD2rhoD(0.17,1.0, 4.562481357, 0.75))
    print(rhoD2rhoD(0.17,1.0, 4.562481357, 1.25))