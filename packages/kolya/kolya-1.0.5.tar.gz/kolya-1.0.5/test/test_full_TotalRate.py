import unittest
import kolya

class TestFull_TotalRate3GeV(unittest.TestCase):

    def test_totalratemom(self):
        par = kolya.parameters.physical_parameters(mbkin=4.526, mcMS=0.993, scale_mcMS=3.0,scale_alphas=4.526)
        hqe = kolya.parameters.LSSA_HQE_parameters(muG = 0.306, rhoD = 0.185, rhoLS = -0.13, mupi = 0.477)
        wc = kolya.parameters.WCoefficients()
        #LO and power corrections up to 1/mb^3
        par.alphas = 0
        self.assertAlmostEqual(kolya.TotalRate.X_Gamma_KIN_MS(par, hqe, wc, flag_includeNLOpw=0, flag_includeNNLO=0, flag_includeN3LO=0)/(0.6465973638906712),1.0,delta=1e-7)

        #NLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.TotalRate.X_Gamma_KIN_MS(par, hqe, wc, flag_includeNLOpw=0, flag_includeNNLO=0, flag_includeN3LO=0)/(0.5649963005151616),1.,delta=1e-7)

        #NNLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.TotalRate.X_Gamma_KIN_MS(par, hqe, wc, flag_includeNLOpw=0, flag_includeNNLO=1, flag_includeN3LO=0)/(0.5403196002657105),1.,delta=1e-7)

        #N3LO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.TotalRate.X_Gamma_KIN_MS(par, hqe, wc, flag_includeNLOpw=0, flag_includeNNLO=1, flag_includeN3LO=1)/(0.5336005435221307),1.,delta=1e-7)

        #N3LO partonic and NLO power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.TotalRate.X_Gamma_KIN_MS(par, hqe, wc, flag_includeNLOpw=1, flag_includeNNLO=1, flag_includeN3LO=1)/(0.5327773269494837),1.,delta=1e-7)


class TestFull_TotalRate2GeV(unittest.TestCase):

    def test_totalratemom(self):
        par = kolya.parameters.physical_parameters(mbkin=4.526, mcMS=1.092, scale_mcMS=2.0,scale_alphas=4.526)
        hqe = kolya.parameters.LSSA_HQE_parameters(muG = 0.306, rhoD = 0.185, rhoLS = -0.13, mupi = 0.477)
        wc = kolya.parameters.WCoefficients()
        #LO and power corrections up to 1/mb^3
        par.alphas = 0
        self.assertAlmostEqual(kolya.TotalRate.X_Gamma_KIN_MS(par, hqe, wc, flag_includeNLOpw=0, flag_includeNNLO=0, flag_includeN3LO=0)/(0.6019511484457933),1.0,delta=1e-7)

        #NLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.TotalRate.X_Gamma_KIN_MS(par, hqe, wc, flag_includeNLOpw=0, flag_includeNNLO=0, flag_includeN3LO=0)/(0.54585401657385),1.,delta=1e-7)

        #NNLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.TotalRate.X_Gamma_KIN_MS(par, hqe, wc, flag_includeNLOpw=0, flag_includeNNLO=1, flag_includeN3LO=0)/(0.5343691469765371),1.,delta=1e-7)

        #N3LO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.TotalRate.X_Gamma_KIN_MS(par, hqe, wc, flag_includeNLOpw=0, flag_includeNNLO=1, flag_includeN3LO=1)/(0.5341465632277341),1.,delta=1e-7)

        #N3LO partonic and NLO power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.TotalRate.X_Gamma_KIN_MS(par, hqe, wc, flag_includeNLOpw=1, flag_includeNNLO=1, flag_includeN3LO=1)/(0.5313467029255363),1.,delta=1e-7)



if __name__ == '__main__':
   unittest.main()
