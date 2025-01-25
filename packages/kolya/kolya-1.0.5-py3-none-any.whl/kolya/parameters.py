import numpy as np
from kolya import interface_rundec

class physical_parameters:
    """class to store values of physical parameters"""

    def __init__(
            self,
            mbkin: float = 4.563,
            scale_mbkin: float = 1.0,
            mcMS: float = 0.989,
            scale_mcMS: float = 3.0,
            alphas: float = 0.2182,
            scale_alphas: float = 4.563, 
            MB: float = 5.279,
            ):
        self.mbkin = mbkin
        self.scale_mbkin = scale_mbkin
        self.mcMS = mcMS
        self.scale_mcMS = scale_mcMS
        self.alphas = alphas
        self.scale_alphas = scale_alphas
        self.scale_muG = self.mbkin
        self.scale_rhoLS = self.mbkin
        self.scale_rhoD = self.mbkin
        self.MB = MB

    def __repr__(self):
        lines = f'bottom mass:       mbkin({self.scale_mbkin} GeV)     = {self.mbkin} GeV\n'
        lines += f'charm mass:        mcMS({self.scale_mcMS} GeV)      = {self.mcMS} GeV\n'
        lines +=f'coupling constant: alpha_s({self.scale_alphas} GeV) = {self.alphas}'
        return lines

    def FLAG2024(self, **kwargs):
        scale_mbkin   = kwargs.get('scale_mbkin', 1.0)
        scale_mcMS    = kwargs.get('scale_mcMS' , 3.0)
        scale_alphas  = kwargs.get('scale_alphas' , 4.563)
        self.scale_mbkin   = scale_mbkin 
        self.scale_mcMS    = scale_mcMS
        self.scale_alphas  = scale_alphas

        if (kwargs.get('flag_DEBUG', 0) == 1):
            print("#set scale_alphas = ",scale_alphas)
            print("#set scale_mbkin  = ",scale_mbkin)
            print("#set scale_mcMS   = ",scale_mcMS)

        
        self.mbkin = interface_rundec.calculate_mbkin(scale_mbkin)
        self.mcMS = interface_rundec.calculate_mcMS(scale_mcMS)
        self.alphas = interface_rundec.as4(scale_alphas)
        self.scale_muG   = self.mbkin
        self.scale_rhoLS = self.mbkin
        self.scale_rhoD  = self.mbkin
        
        if (kwargs.get('flag_DEBUG', 0) == 1):
            print("#new value: alphas = ",self.alphas)
            print("#new value: mbkin  = ",self.mbkin)
            print("#new value: mcMS   = ",self.mcMS)

    def show(self):
        print("bottom mass:       mbkin(",self.scale_mbkin," GeV)    = ",self.mbkin," GeV")
        print("charm mass:        mbMS(",self.scale_mcMS," GeV)      = ",self.mcMS," GeV")
        print("coupling constant: alpha_s(",self.scale_alphas," GeV) = ",self.alphas)


class physical_parameters_FLAG2023:
    """class to store values of physical parameters"""

    def __init__(
            self,
            scale_mbkin: float = 1.0,
            scale_mcMS: float = 3.0,
            scale_alphas: float = 4.563,
            MB: float = 5.279,
            ):
        self.scale_mbkin = scale_mbkin
        self.mbkin = interface_rundec.calculate_mbkin(scale_mbkin)
        self.scale_mcMS = scale_mcMS
        self.mcMS = interface_rundec.calculate_mcMS(scale_mcMS)
        self.alphas = interface_rundec.as4(scale_alphas)
        self.scale_alphas = scale_alphas
        self.scale_muG = self.mbkin
        self.scale_rhoLS = self.mbkin
        self.scale_rhoD = self.mbkin
        self.MB = MB

class HQE_parameters:
    """class to store values of HQE parameters"""

    def __init__(
            self,
            mupi: float = 0,
            muG: float = 0,
            rhoD: float = 0,
            rhoLS: float = 0,
            m1: float = 0,
            m2: float = 0,
            m3: float = 0,
            m4: float = 0,
            m5: float = 0,
            m6: float = 0,
            m7: float = 0,
            m8: float = 0,
            m9: float = 0,
            r1: float = 0,
            r2: float = 0,
            r3: float = 0,
            r4: float = 0,
            r5: float = 0,
            r6: float = 0,
            r7: float = 0,
            r8: float = 0,
            r9: float = 0,
            r10: float = 0,
            r11: float = 0,
            r12: float = 0,
            r13: float = 0,
            r14: float = 0,
            r15: float = 0,
            r16: float = 0,
            r17: float = 0,
            r18: float = 0,
            ):
        self.mupi = mupi
        self.muG  = muG
        self.rhoD = rhoD
        self.rhoLS = rhoLS
        self.m1 = m1
        self.m2 = m2
        self.m3 = m3
        self.m4 = m4
        self.m5 = m5
        self.m6 = m6
        self.m7 = m7
        self.m8 = m8
        self.m9 = m9
        self.r1 = r1
        self.r2 = r2
        self.r3 = r3
        self.r4 = r4
        self.r5 = r5
        self.r6 = r6
        self.r7 = r7
        self.r8 = r8
        self.r9 = r9
        self.r10 = r10
        self.r11 = r11
        self.r12 = r12
        self.r13 = r13
        self.r14 = r14
        self.r15 = r15
        self.r16 = r16
        self.r17 = r17
        self.r18 = r18

    def __repr__(self):    
        lines = f'mupi  = {self.mupi} GeV^2\n'
        lines += f'muG   = {self.muG} GeV^2\n'
        lines += f'rhoD  = {self.rhoD} GeV^3\n'
        lines += f'rhoLS = {self.rhoLS} GeV^3'
        return lines

    def show(self, **kwargs):
        print("mupi  = ",self.mupi," GeV^2")
        print("muG   = ",self.muG, " GeV^2")
        print("rhoD  = ",self.rhoD," GeV^3")
        print("rhoLS = ",self.rhoLS," GeV^3")

        if (kwargs.get('flagmb4', 0)==1):
            print("")
            print("m1 = ",self.m1," GeV^4")
            print("m2 = ",self.m2," GeV^4")
            print("m3 = ",self.m3," GeV^4")
            print("m4 = ",self.m4," GeV^4")
            print("m5 = ",self.m5," GeV^4")
            print("m6 = ",self.m6," GeV^4")
            print("m7 = ",self.m7," GeV^4")
            print("m8 = ",self.m8," GeV^4")
            print("m9 = ",self.m9," GeV^4")

        if (kwargs.get('flagmb5', 0)==1):
            print("")
            print("r1  = ",self.r1," GeV^5")
            print("r2  = ",self.r2," GeV^5")
            print("r3  = ",self.r3," GeV^5")
            print("r4  = ",self.r4," GeV^5")
            print("r5  = ",self.r5," GeV^5")
            print("r6  = ",self.r6," GeV^5")
            print("r7  = ",self.r7," GeV^5")
            print("r8  = ",self.r8," GeV^5")
            print("r9  = ",self.r9," GeV^5")
            print("r10 = ",self.r10," GeV^5")
            print("r11 = ",self.r11," GeV^5")
            print("r12 = ",self.r12," GeV^5")
            print("r13 = ",self.r13," GeV^5")
            print("r14 = ",self.r14," GeV^5")
            print("r15 = ",self.r15," GeV^5")
            print("r16 = ",self.r16," GeV^5")
            print("r17 = ",self.r17," GeV^5")
            print("r18 = ",self.r18," GeV^5")

class HQE_parameters_RPI:
    """class to store values of HQE parameters in RPI basis"""

    def __init__(
            self,
            mupi: float = 0,
            muG: float = 0,
            rhoD: float = 0,
            rhoLS: float = 0,
            rEtilde: float = 0,
            rG: float = 0,
            sEtilde: float = 0,
            sB: float = 0,
            sqB: float = 0,
            X1: float = 0,
            X2: float = 0,
            X3: float = 0,
            X4: float = 0,
            X5: float = 0,
            X6: float = 0,
            X7: float = 0,
            X8: float = 0,
            X9: float = 0,
            X10: float = 0,
            ):
        self.mupi = mupi
        self.muG  = muG
        self.rhoD = rhoD
        self.rhoLS = rhoLS
        self.rEtilde = rEtilde
        self.rG = rG
        self.sEtilde = sEtilde
        self.sB = sB
        self.sqB = sqB
        self.X1 = X1
        self.X2 = X2
        self.X3 = X3
        self.X4 = X4
        self.X5 = X5
        self.X6 = X6
        self.X7 = X7
        self.X8 = X8
        self.X9 = X9
        self.X10 = X10
    
    def __repr__(self):    
        lines = f'mupi  = {self.mupi} GeV^2\n'
        lines += f'muG   = {self.muG} GeV^2\n'
        lines += f'rhoD  = {self.rhoD} GeV^3\n'
        lines += f'rhoLS = {self.rhoLS} GeV^3'
        return lines
     
    def show(self, **kwargs):
        print("mupi  = ",self.mupi," GeV^2")
        print("muG   = ",self.muG, " GeV^2")
        print("rhoD  = ",self.rhoD," GeV^3")
        print("rhoLS = ",self.rhoLS," GeV^3")

        if (kwargs.get('flagmb4', 0)==1):
            print("")
            print("rEtilde = ",self.rEtilde," GeV^4")
            print("rG      = ",self.rG," GeV^4")
            print("sEtilde = ",self.sEtilde," GeV^4")
            print("sB      = ",self.sB," GeV^4")
            print("sqB     = ",self.sqB," GeV^4")


        if (kwargs.get('flagmb5', 0)==1):
            print("")
            print("X1  = ",self.X1," GeV^5")
            print("X2  = ",self.X2," GeV^5")
            print("X3  = ",self.X3," GeV^5")
            print("X4  = ",self.X4," GeV^5")
            print("X5  = ",self.X5," GeV^5")
            print("X6  = ",self.X6," GeV^5")
            print("X7  = ",self.X7," GeV^5")
            print("X8  = ",self.X8," GeV^5")
            print("X9  = ",self.X9," GeV^5")
            print("X10 = ",self.X10," GeV^5")
            
    def perp_to_RPI(self, par, hqe, **kwargs):
        #Converts HQE parameters in historical/perp basis (hqe) to RPI basis
        fmb4 = kwargs.get('flagmb4', 0)
        fmb5 = kwargs.get('flagmb5', 0)
        mb = par.mbkin

        mupi = hqe.mupi
        muG = hqe.muG
        rhoD = hqe.rhoD
        rhoLS = hqe.rhoLS

        m1 = hqe.m1
        m2 = hqe.m2
        m3 = hqe.m3
        m4 = hqe.m4
        m5 = hqe.m5
        m6 = hqe.m6
        m7 = hqe.m7
        m8 = hqe.m8
        m9 = hqe.m9

        r1=hqe.r1
        r2=hqe.r2
        r3=hqe.r3
        r4=hqe.r4
        r5=hqe.r5
        r6=hqe.r6
        r7=hqe.r7
        r8=hqe.r8
        r9=hqe.r9
        r10=hqe.r10
        r11=hqe.r11
        r12=hqe.r12
        r13=hqe.r13
        r14=hqe.r14
        r15=hqe.r15
        r16=hqe.r16
        r17=hqe.r17
        r18=hqe.r18

        mupi_RPI = 0
        mupi_RPI += mupi
        if fmb4 == 1:
            mupi_RPI += (-1*m1/4 -m2/4 -m4/12 -m5/4 -m6/4 -m8/16)/mb**2
        if fmb5 == 1:
            mupi_RPI += (-1*r1/4 +r2/2 -r3/2 +r4/2 -r8/4 +r9/2 +r10/2 -r11/2 -r12/2 +r13/2 +r14/2)/mb**3
        self.mupi = mupi_RPI

        muG_RPI = 0
        muG_RPI += muG
        muG_RPI += -1*(rhoD + rhoLS)/mb
        if fmb4 == 1:
            muG_RPI += (m2/2 + m5/2)/mb**2
        if fmb5 == 1:
            muG_RPI += (-1*r2 +r3 -r4 +r5/2 +r6/2 -r7/2 -r9 -r10 +r11 +r12 -r13 -r14 +r15 +r16/2 +r17/2)/(2 * mb**3)
        self.muG = muG_RPI

        rhoD_RPI = 0
        rhoD_RPI += rhoD
        if fmb4 == 1:
            rhoD_RPI += (m2 -m3 -m4/2)/(2*mb)
        if fmb5 == 1:
            rhoD_RPI += (-1*r2 +r5 -r10 +r15)/(2 * mb**2)
        self.rhoD = rhoD_RPI

        if fmb4 == 1:
            rEtilde_RPI = 0
            rEtilde_RPI += -1*m2
            if fmb5 == 1:
                rEtilde_RPI += (r2-r4)/mb
            self.rEtilde = rEtilde_RPI

            rG_RPI = 0
            rG_RPI += -2*m2 +m3
            if fmb5 == 1:
                rG_RPI += 0
            self.rG = rG_RPI

            sEtilde_RPI = 0
            sEtilde_RPI += -1*m5
            if fmb5 == 1:
                sEtilde_RPI += (r9-r14)/mb
            self.sEtilde = sEtilde_RPI

            sB_RPI = 0
            sB_RPI += -1*m5 -m6
            if fmb5 == 1:
                sB_RPI += (r2 -2*r3 +r4 -r6 +r7 +r10 -r11 -r12 +r14 -r17 +r18)/mb
            self.sB = sB_RPI

            sqB_RPI = 0
            sqB_RPI += -4*m6 +2*m9
            if fmb5 == 1:
                sqB_RPI += 2*(r1 -r2 -2*r3 -r4 +r5 -r6 +3*r7 +r8 -r9 -2*r11 -r14 -r16 -r17 +4*r18)/mb
            self.sqB = sqB_RPI
        else:
            self.rEtilde = 0
            self.rG= 0
            self.sEtilde = 0
            self.sB = 0
            self.sqB = 0
        if fmb5 == 1:
            self.X1 = r1
            self.X2 = 2*r6 - 2*r7
            self.X3 = -1*r2 +2*r3 -r4 +r6 -r7
            self.X4 = 2*(r2 +2*r3 +r4 -r5 -r6 -r7)
            self.X5 = r8
            self.X6 = r16 +r17 -2*r18
            self.X7 = r11 - r12 -r13 +r14 +r16 -r18
            self.X8 = -1*r9 +r11 +r12 -r13 +r16 -r18
            self.X9 = 4*r10 -2*r15
            self.X10 = 2*(r10 +r13 -r15)
        else:
            self.X1 = 0
            self.X2 = 0
            self.X3 = 0
            self.X4 = 0
            self.X5 = 0
            self.X6 = 0
            self.X7 = 0
            self.X8 = 0
            self.X9 = 0
            self.X10 = 0

class LSSA_HQE_parameters:
    """class to store values of HQE parameters in RPI basis, where the default values are the LSSA approximations"""

    def __init__(
            self,
            mupi: float = 0.477,
            muG: float = 0.306,
            rhoD: float = 0.231,
            rhoLS: float = -0.161,
            m1: float = 0.126,
            m2: float = -0.112,
            m3: float = -0.064,
            m4: float = 0.400,
            m5: float = 0.082,
            m6: float = 0.057,
            m7: float = -0.039,
            m8: float = -1.17,
            m9: float = -0.404,
            r1: float = 0.049,
            r2: float = -0.106,
            r3: float = -0.027,
            r4: float = -0.043,
            r5: float = 0.00,
            r6: float = 0.00,
            r7: float = 0.00,
            r8: float = -0.039,
            r9: float = 0.074,
            r10: float = 0.068,
            r11: float = 0.0059,
            r12: float = 0.010,
            r13: float = -0.055,
            r14: float = 0.039,
            r15: float = 0.00,
            r16: float = 0.00,
            r17: float = 0.00,
            r18: float = 0.00,
            ):
        self.mupi = mupi
        self.muG  = muG
        self.rhoD = rhoD
        self.rhoLS = rhoLS
        self.m1 = m1
        self.m2 = m2
        self.m3 = m3
        self.m4 = m4
        self.m5 = m5
        self.m6 = m6
        self.m7 = m7
        self.m8 = m8
        self.m9 = m9
        self.r1 = r1
        self.r2 = r2
        self.r3 = r3
        self.r4 = r4
        self.r5 = r5
        self.r6 = r6
        self.r7 = r7
        self.r8 = r8
        self.r9 = r9
        self.r10 = r10
        self.r11 = r11
        self.r12 = r12
        self.r13 = r13
        self.r14 = r14
        self.r15 = r15
        self.r16 = r16
        self.r17 = r17
        self.r18 = r18


class LSSA_HQE_parameters_RPI:
    """class to store values of HQE parameters in RPI basis, where the default values are the LSSA approximations"""

    def __init__(
            self,
            mupi: float = 0.478,
            muG: float = 0.290,
            rhoD: float = 0.205,
            rhoLS: float = -0.161,
            rEtilde: float = 0.098,
            rG: float = 0.16,
            sEtilde: float = -0.074,
            sB: float = -0.14,
            sqB: float = -1.00,
            X1: float = 0.049,
            X2: float = 0.00,
            X3: float = 0.094,
            X4: float = -0.41,
            X5: float = -0.039,
            X6: float = 0.00,
            X7: float = 0.091,
            X8: float = -0.0030,
            X9: float = 0.27,
            X10: float = 0.025,
            ):
        self.mupi = mupi
        self.muG  = muG
        self.rhoD = rhoD
        self.rhoLS = rhoLS
        self.rEtilde = rEtilde
        self.rG = rG
        self.sEtilde = sEtilde
        self.sB = sB
        self.sqB = sqB
        self.X1 = X1
        self.X2 = X2
        self.X3 = X3
        self.X4 = X4
        self.X5 = X5
        self.X6 = X6
        self.X7 = X7
        self.X8 = X8
        self.X9 = X9
        self.X10 = X10

class WCoefficients:
    """class to store values of Wilson coefficients
    We define separate coefficients for quadratic terms
    """

    def __init__(
            self,
            VL: complex = 0,
            VR: complex = 0,
            SL: complex = 0,
            SR: complex = 0,
            T:  complex = 0
            ):
        self.VL = VL
        self.VR = VR
        self.SL = SL
        self.SR = SR
        self.T = T


    @property
    def ReVL(self):
        return np.real(self.VL)

    @property
    def ReVR(self):
        return np.real(self.VR)

    @property
    def T2(self):
        return np.abs(self.T)**2
    
    @property
    def SL2(self):
        return np.abs(self.SL)**2
    
    @property
    def SR2(self):
        return np.abs(self.SR)**2
        
    @property
    def SLSR(self):
        return np.real(self.SL*np.conjugate(self.SR))
    
    @property
    def VL2(self):
        return np.abs(self.VL)**2
    
    @property
    def VR2(self):
        return np.abs(self.VR)**2
    
    @property
    def VLVR(self):
        return np.real(self.VL*np.conjugate(self.VR))
    
    @property
    def SLT(self):
        return np.real(self.SL*np.conjugate(self.T))
    
    @property
    def SRT(self):
        return np.real(self.SR*np.conjugate(self.T))
    
    def __repr__(self):
        lines = f'C_{{V_L}} = {self.VL}\n'
        lines += f'C_{{V_R}} = {self.VR}\n'
        lines += f'C_{{S_L}} = {self.SL}\n'
        lines += f'C_{{S_R}} = {self.SR}\n'
        lines += f'C_{{T}} = {self.T}'
        return lines
        
    def show(self, **kwargs):
        print("C_{V_L} = ",self.VL)
        print("C_{V_R} = ",self.VR)
        print("C_{S_L} = ",self.SL)
        print("C_{S_R} = ",self.SR)
        print("C_{T} = ",self.T)

    
