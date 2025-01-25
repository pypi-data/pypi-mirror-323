import rundec


def as5(mu, alphasZ=0.1180):
    """Value of the strong couplig constant alpha_s^(5)(mu) at the scale mu. """
    crd = rundec.CRunDec()
    return crd.AlphasExact(alphasZ, 91.187, mu, 5, 4)


def as4(mu, mbMSin=4.196, alphasZ=0.1180):
    """Value of the strong couplig constant alpha_s^(4)(mu) at the scale mu. 
        Bottom quark decouples at 2*mbMS(mbMS)"""
    crd = rundec.CRunDec()
    asdec = crd.DecAsDownSI(as5(2*mbMSin, alphasZ=alphasZ), mbMSin, 2*mbMSin, 4, 4)
    return crd.AlphasExact(asdec, 2*mbMSin, mu, 4, 4)


def as3(mu, mc3MSin=0.989, scale_mc3MS=3.0, mbMSin=4.196, alphasZ=0.1180):
    """Value of the strong couplig constant alpha_s^(3)(mu) at the scale mu. 
        Charm quark decouples at 2*mcMS(3Gev) 
        Default parameters for charm quark mass MS scheme Nf = 4
        from FLAG 2023 Eq. 61.: mc(3 GeV) = 0.989(10) GeV 
    """
    crd = rundec.CRunDec()
    asdec = crd.DecAsDownMS(as4(scale_mc3MS, mbMSin=mbMSin, alphasZ=alphasZ), mc3MSin, scale_mc3MS, 3, 4)
    return crd.AlphasExact(asdec, scale_mc3MS, mu, 3, 4)


def calculate_mcMS(mu0, mc3MSin=0.989, scale_mc3MS=3.0, mbMSin=4.196, alphasZ=0.1180):
    """Calculate the value of the charm MS mass at the scale mu0.
        Default parameters for charm quark mass MS scheme Nf = 4
        from FLAG 2023 Eq. 61.: mc(3 GeV) = 0.989(10) GeV 
    """
    crd = rundec.CRunDec()
    nf    = 4
    loops = 4
    return crd.mMS2mMS(mc3MSin, 
                       as4(scale_mc3MS, mbMSin=mbMSin, alphasZ=alphasZ), 
                       as4(mu0, mbMSin=mbMSin, alphasZ=alphasZ), 
                       nf, loops)


def calculate_mbkin(muWC, mc3MSin=0.989, scale_mc3MS=3.0, mbMSin=4.196, alphasZ=0.1180):
    """Calculate the value of the kinetic mass at the scale muWC.
        Default parameters for charm quark mass MS scheme Nf = 4
        from FLAG 2023 Eq. 61.: mc(3 GeV) = 0.989(10) GeV 
        Default parameters for bottom quark mass MS scheme Nf = 5
        converted from FLAG 2023 Eq. 68. mbMS(mbMS) = 4.203(11) GeV
    """

    crd = rundec.CRunDec()
    # calculate mbMS with Nf=5 from mbMS with Nf=5 
    # step1: calculate mbOS
    #crd.mq.first = mc3MSin
    #crd.mq.second = scale_mc3MS
    #nf = 5
    #nloops = 4
    #mbOS = crd.mMS2mOS(mbMSin, crd.mq, as4(mbMSin), mbMSin, nf, nloops)

    #step2: decouple mbMS^(4) ---> mbMS^(5)
    #temporay scale for mbMS5
    #scale_tmp = 5.0
    #nloops = 5

    #crd.nfMmu.Mth = mbOS
    #crd.nfMmu.muth = 2*mbOS
    #crd.nfMmu.nf = 5

    #mbMStmp = crd.mL2mH(mbMSin, as4(mbMSin), mbMSin, crd.nfMmu, scale_tmp, nloops)

    #calculate scale invariant mbMS5(mbMS5)

    #nf = 5
    #nloops = 5
    #mbMS5 = crd.mMS2mSI(mbMStmp, as4(scale_tmp), scale_tmp, nf, nloops)

    mcMS = rundec.RunDecPair()
    mcMS.first  = mc3MSin
    mcMS.second = scale_mc3MS

    #convert mbMS5 to kinetic mass using scheme "B"
    scheme = 1
    nloops = 3
    return crd.mMS2mKIN(mbMSin, mcMS, as4(mbMSin, mbMSin=mbMSin, alphasZ=alphasZ), mbMSin, muWC, nloops,scheme)


if __name__ == '__main__':
    print("as5(3 Gev) = ", as5(3.))
    print("as4(3 Gev) = ", as4(3.))
    print("as3(3 Gev) = ", as3(3.))
    print("mbkin(1GeV) = ",calculate_mbkin(1.))
    print("as4(mbkin) = ",as4(calculate_mbkin(1.)))
    print("mcMS (2 GeV) = ",calculate_mcMS(2))
    print("mcMS (3 GeV) = ",calculate_mcMS(3))
