from kolya import parameters
from kolya.NLOpartonic import X1Q2
import math

def X_Gamma_KIN_MS_NP(par, hqe, wc, **kwargs):

    r=par.mcMS/par.mbkin
    mu0=par.scale_mcMS/par.mbkin
    muWC=par.scale_mbkin/par.mbkin
    api=par.alphas/math.pi

    rhoD=hqe.rhoD/par.mbkin**3
    rhoLS=hqe.rhoLS/par.mbkin**3
    muG=hqe.muG/par.mbkin**2
    mupi=hqe.mupi/par.mbkin**2

    res = 0.

    if wc.ReVL != 0:
      resNP = 0
      resNP +=(2-16*r**2+16*r**6-2*r**8-48*r**4*math.log(r))
      resNP += (muG*(-3+8*r**2-24*r**4+24*r**6
          -5*r**8-24*r**4*math.log(r)))
      resNP += (mupi*(-1+8*r**2-8*r**6+r**8+24*r**4*math.log(r))
          )
      resNP += (rhoLS*(3-8*r**2+24*r**4-24*r**6+5*r**8+24*r**4*math.log(r)))
      resNP += (rhoD*(77/3
          -(88*r**2)/3+8*r**4-(8*r**6)/3-(5*r**8)/3+(32+24*r**4)*math.log(r)))
      resNP += (api*((
          -128*r**2)/3-64*r**4+128*r**6-(64*r**8)/3-256*r**4*math.log(r)+math.log(mu0**2/r**2)*(
          -32*r**2-48*r**4+96*r**6-16*r**8-192*r**4*math.log(r))+muWC*(160/9-(256*r**2)/3
          +(256*r**4)/3-(256*r**6)/9+(32*r**8)/3-(256*r**4*math.log(r))/3)+muWC**2*(8
          -(128*r**2)/3+32*r**4+(8*r**8)/3-64*r**4*math.log(r))+muWC**3*(-616/27+(704*r**2)/27
          -(64*r**4)/9+(64*r**6)/27+(40*r**8)/27+(-256/9-(64*r**4)/3)*math.log(r))
          +X1Q2(0,'VL',0,r)))
      res += resNP*wc.ReVL

    if wc.ReVR != 0:
      resNP = 0
      resNP +=(-4*r-36*r**3+36*r**5+4*r**7+(-48*r**3-48*r**5)*math.log(r))
      resNP += (muG*((-26*r)/3
          +18*r**3-18*r**5+(26*r**7)/3+(-16*r+24*r**3-24*r**5)*math.log(r)))
      resNP += (rhoD*(
          -50*r+78*r**3-30*r**5+2*r**7+(-48*r-24*r**3+24*r**5)*math.log(r)))
      resNP += (rhoLS*((26*r)/3
          -18*r**3+18*r**5-(26*r**7)/3+(16*r-24*r**3+24*r**5)*math.log(r)))
      resNP += (mupi*(2*r
          +18*r**3-18*r**5-2*r**7+(24*r**3+24*r**5)*math.log(r)))
      resNP += (api*((-16*r)/3-208*r**3
          +176*r**5+(112*r**7)/3+(-192*r**3-320*r**5)*math.log(r)+muWC*((-256*r)/9
          -(128*r**3)/3+(256*r**5)/3-(128*r**7)/9-(512*r**3*math.log(r))/3)+math.log(mu0**2/r**2)*(
          -4*r-156*r**3+132*r**5+28*r**7+(-144*r**3-240*r**5)*math.log(r))+muWC**2*((
          -40*r)/3-40*r**3+56*r**5-(8*r**7)/3+(-96*r**3-32*r**5)*math.log(r))+muWC**3*((400*r)/9
          -(208*r**3)/3+(80*r**5)/3-(16*r**7)/9+((128*r)/3+(64*r**3)/3-(64*r**5)/3)*math.log(r))
          +X1Q2(0,'VR',0,r)))
      res += resNP*wc.ReVR

    if wc.SL2 != 0:
      resNP = 0
      resNP +=(1/4-2*r**2+2*r**6-r**8/4-6*r**4*math.log(r))
      resNP += (mupi*(-1/8+r**2-r**6+r**8/8
          +3*r**4*math.log(r)))
      resNP += (muG*(13/8+4*r**2-9*r**4+4*r**6-(5*r**8)/8+(12*r**2
          -3*r**4)*math.log(r)))
      resNP += (rhoLS*(-13/8-4*r**2+9*r**4-4*r**6+(5*r**8)/8+(-12*r**2
          +3*r**4)*math.log(r)))
      resNP += (rhoD*(197/24-(23*r**2)/3-r**6/3-(5*r**8)/24+(8+8*r**2
          +3*r**4)*math.log(r)))
      resNP += (api*((-16*r**2)/3-8*r**4+16*r**6-(8*r**8)/3-32*r**4*math.log(r)
          +math.log(mu0**2/r**2)*(-4*r**2-6*r**4+12*r**6-2*r**8-24*r**4*math.log(r))+muWC*(20/9
          -(32*r**2)/3+(32*r**4)/3-(32*r**6)/9+(4*r**8)/3-(32*r**4*math.log(r))/3)
          +muWC**2*(1-(16*r**2)/3+4*r**4+r**8/3-8*r**4*math.log(r))+muWC**3*(-197/27
          +(184*r**2)/27+(8*r**6)/27+(5*r**8)/27+(-64/9-(64*r**2)/9-(8*r**4)/3)*math.log(r))
          +X1Q2(0,'SL2',0,r)))
      res += resNP*wc.SL2

    if wc.SR2 != 0:
      resNP = 0
      resNP +=(1/4-2*r**2+2*r**6-r**8/4-6*r**4*math.log(r))
      resNP += (mupi*(-1/8+r**2-r**6+r**8/8
          +3*r**4*math.log(r)))
      resNP += (muG*(13/8+4*r**2-9*r**4+4*r**6-(5*r**8)/8+(12*r**2
          -3*r**4)*math.log(r)))
      resNP += (rhoLS*(-13/8-4*r**2+9*r**4-4*r**6+(5*r**8)/8+(-12*r**2
          +3*r**4)*math.log(r)))
      resNP += (rhoD*(197/24-(23*r**2)/3-r**6/3-(5*r**8)/24+(8+8*r**2
          +3*r**4)*math.log(r)))
      resNP += (api*((-16*r**2)/3-8*r**4+16*r**6-(8*r**8)/3-32*r**4*math.log(r)
          +math.log(mu0**2/r**2)*(-4*r**2-6*r**4+12*r**6-2*r**8-24*r**4*math.log(r))+muWC*(20/9
          -(32*r**2)/3+(32*r**4)/3-(32*r**6)/9+(4*r**8)/3-(32*r**4*math.log(r))/3)
          +muWC**2*(1-(16*r**2)/3+4*r**4+r**8/3-8*r**4*math.log(r))+muWC**3*(-197/27
          +(184*r**2)/27+(8*r**6)/27+(5*r**8)/27+(-64/9-(64*r**2)/9-(8*r**4)/3)*math.log(r))
          +X1Q2(0,'SR2',0,r)))
      res += resNP*wc.SR2

    if wc.VL2 != 0:
      resNP = 0
      resNP +=(1-8*r**2+8*r**6-r**8-24*r**4*math.log(r))
      resNP += (muG*(-3/2+4*r**2-12*r**4+12*r**6
          -(5*r**8)/2-12*r**4*math.log(r)))
      resNP += (mupi*(-1/2+4*r**2-4*r**6+r**8/2+12*r**4*math.log(r))
          )
      resNP += (rhoLS*(3/2-4*r**2+12*r**4-12*r**6+(5*r**8)/2+12*r**4*math.log(r)))
      resNP += (rhoD*(77/6
          -(44*r**2)/3+4*r**4-(4*r**6)/3-(5*r**8)/6+(16+12*r**4)*math.log(r)))
      resNP += (api*((
          -64*r**2)/3-32*r**4+64*r**6-(32*r**8)/3-128*r**4*math.log(r)+math.log(mu0**2/r**2)*(
          -16*r**2-24*r**4+48*r**6-8*r**8-96*r**4*math.log(r))+muWC*(80/9-(128*r**2)/3
          +(128*r**4)/3-(128*r**6)/9+(16*r**8)/3-(128*r**4*math.log(r))/3)+muWC**2*(4
          -(64*r**2)/3+16*r**4+(4*r**8)/3-32*r**4*math.log(r))+muWC**3*(-308/27+(352*r**2)/27
          -(32*r**4)/9+(32*r**6)/27+(20*r**8)/27+(-128/9-(32*r**4)/3)*math.log(r))
          +X1Q2(0,'VL2',0,r)))
      res += resNP*wc.VL2

    if wc.SLSR != 0:
      resNP = 0
      resNP +=(2*r+18*r**3-18*r**5-2*r**7+(24*r**3+24*r**5)*math.log(r))
      resNP += (mupi*(-r-9*r**3
          +9*r**5+r**7+(-12*r**3-12*r**5)*math.log(r)))
      resNP += (rhoLS*(33*r-27*r**3-9*r**5
          +3*r**7+(24*r+60*r**3-12*r**5)*math.log(r)))
      resNP += (rhoD*((143*r)/3-51*r**3+3*r**5
          +r**7/3+(40*r+60*r**3-12*r**5)*math.log(r)))
      resNP += (muG*(-33*r+27*r**3+9*r**5
          -3*r**7+(-24*r-60*r**3+12*r**5)*math.log(r)))
      resNP += (api*((8*r)/3+104*r**3-88*r**5
          -(56*r**7)/3+(96*r**3+160*r**5)*math.log(r)+muWC*((128*r)/9+(64*r**3)/3
          -(128*r**5)/3+(64*r**7)/9+(256*r**3*math.log(r))/3)+muWC**3*((-1144*r)/27
          +(136*r**3)/3-(8*r**5)/3-(8*r**7)/27+((-320*r)/9-(160*r**3)/3+(32*r**5)/3)*math.log(r))
          +muWC**2*((20*r)/3+20*r**3-28*r**5+(4*r**7)/3+(48*r**3+16*r**5)*math.log(r))
          +math.log(mu0**2/r**2)*(2*r+78*r**3-66*r**5-14*r**7+(72*r**3+120*r**5)*math.log(r))
          +X1Q2(0,'SLSR',0,r)))
      res += resNP*wc.SLSR

    if wc.VR2 != 0:
      resNP = 0
      resNP +=(1-8*r**2+8*r**6-r**8-24*r**4*math.log(r))
      resNP += (muG*(-3/2+4*r**2-12*r**4+12*r**6
          -(5*r**8)/2-12*r**4*math.log(r)))
      resNP += (mupi*(-1/2+4*r**2-4*r**6+r**8/2+12*r**4*math.log(r))
          )
      resNP += (rhoLS*(3/2-4*r**2+12*r**4-12*r**6+(5*r**8)/2+12*r**4*math.log(r)))
      resNP += (rhoD*(77/6
          -(44*r**2)/3+4*r**4-(4*r**6)/3-(5*r**8)/6+(16+12*r**4)*math.log(r)))
      resNP += (api*((
          -64*r**2)/3-32*r**4+64*r**6-(32*r**8)/3-128*r**4*math.log(r)+math.log(mu0**2/r**2)*(
          -16*r**2-24*r**4+48*r**6-8*r**8-96*r**4*math.log(r))+muWC*(80/9-(128*r**2)/3
          +(128*r**4)/3-(128*r**6)/9+(16*r**8)/3-(128*r**4*math.log(r))/3)+muWC**2*(4
          -(64*r**2)/3+16*r**4+(4*r**8)/3-32*r**4*math.log(r))+muWC**3*(-308/27+(352*r**2)/27
          -(32*r**4)/9+(32*r**6)/27+(20*r**8)/27+(-128/9-(32*r**4)/3)*math.log(r))
          +X1Q2(0,'VR2',0,r)))
      res += resNP*wc.VR2

    if wc.VLVR != 0:
      resNP = 0
      resNP +=(-4*r-36*r**3+36*r**5+4*r**7+(-48*r**3-48*r**5)*math.log(r))
      resNP += (muG*((-26*r)/3
          +18*r**3-18*r**5+(26*r**7)/3+(-16*r+24*r**3-24*r**5)*math.log(r)))
      resNP += (rhoD*(
          -50*r+78*r**3-30*r**5+2*r**7+(-48*r-24*r**3+24*r**5)*math.log(r)))
      resNP += (rhoLS*((26*r)/3
          -18*r**3+18*r**5-(26*r**7)/3+(16*r-24*r**3+24*r**5)*math.log(r)))
      resNP += (mupi*(2*r
          +18*r**3-18*r**5-2*r**7+(24*r**3+24*r**5)*math.log(r)))
      resNP += (api*((-16*r)/3-208*r**3
          +176*r**5+(112*r**7)/3+(-192*r**3-320*r**5)*math.log(r)+muWC*((-256*r)/9
          -(128*r**3)/3+(256*r**5)/3-(128*r**7)/9-(512*r**3*math.log(r))/3)+math.log(mu0**2/r**2)*(
          -4*r-156*r**3+132*r**5+28*r**7+(-144*r**3-240*r**5)*math.log(r))+muWC**2*((
          -40*r)/3-40*r**3+56*r**5-(8*r**7)/3+(-96*r**3-32*r**5)*math.log(r))+muWC**3*((400*r)/9
          -(208*r**3)/3+(80*r**5)/3-(16*r**7)/9+((128*r)/3+(64*r**3)/3-(64*r**5)/3)*math.log(r))
          +X1Q2(0,'VLVR',0,r)))
      res += resNP*wc.VLVR

    if wc.SLT != 0:
      resNP = 0
      resNP +=(api*X1Q2(0,'SLT',0,r))
      res += resNP*wc.SLT

    if wc.T2 != 0:
      resNP = 0
      resNP +=(12-96*r**2+96*r**6-12*r**8-288*r**4*math.log(r))
      resNP += (mupi*(-6+48*r**2-48*r**6
          +6*r**8+144*r**4*math.log(r)))
      resNP += (muG*(-50-48*r**4+128*r**6-30*r**8+(-192*r**2
          -144*r**4)*math.log(r)))
      resNP += (rhoD*(74-112*r**2+64*r**4-16*r**6-10*r**8+(128
          -128*r**2+144*r**4)*math.log(r)))
      resNP += (rhoLS*(50+48*r**4-128*r**6+30*r**8+(192*r**2
          +144*r**4)*math.log(r)))
      resNP += (api*(-256*r**2-384*r**4+768*r**6-128*r**8-1536*r**4*math.log(r)
          +math.log(mu0**2/r**2)*(-192*r**2-288*r**4+576*r**6-96*r**8-1152*r**4*math.log(r))
          +muWC*(320/3-512*r**2+512*r**4-(512*r**6)/3+64*r**8-512*r**4*math.log(r))
          +muWC**2*(48-256*r**2+192*r**4+16*r**8-384*r**4*math.log(r))+muWC**3*(-592/9
          +(896*r**2)/9-(512*r**4)/9+(128*r**6)/9+(80*r**8)/9+(-1024/9+(1024*r**2)/9
          -128*r**4)*math.log(r))+X1Q2(0,'T2',0,r)))
      res += resNP*wc.T2

    return res