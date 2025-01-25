import unittest
import kolya

class TestFull_ElMoments(unittest.TestCase):

    def test_moment1(self):
        par = kolya.parameters.physical_parameters(mbkin=4.573,mcMS=1.092,scale_mcMS=2.0,scale_alphas=4.573)
        hqe = kolya.parameters.LSSA_HQE_parameters(muG = 0.306, rhoD = 0.185, rhoLS = -0.13, mupi = 0.477)
        wc = kolya.parameters.WCoefficients()
        #LO and power corrections up to 1/mb^3
        par.alphas = 0
        self.assertAlmostEqual(kolya.Elmoments.moment_1_KIN_MS(1, par, hqe, wc, flag_TEST=0,  flag_includeNLOpw=0, flag_includeNNLO=0)/(1.55444375649646),1.,delta=1e-7)

        #NLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.Elmoments.moment_1_KIN_MS(1, par, hqe, wc, flag_TEST=0,  flag_includeNLOpw=0, flag_includeNNLO=0)/(1.5512362944868165),1.,delta=1e-7)

        #NNLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.Elmoments.moment_1_KIN_MS(1, par, hqe, wc, flag_TEST=0,  flag_includeNLOpw=0, flag_includeNNLO=1)/(1.5501137790271446),1.,delta=1e-7)

    def test_moment2(self):
        par = kolya.parameters.physical_parameters(mbkin=4.573,mcMS=1.092,scale_mcMS=2.0,scale_alphas=4.573)
        hqe = kolya.parameters.LSSA_HQE_parameters(muG = 0.306, rhoD = 0.185, rhoLS = -0.13, mupi = 0.477)
        wc = kolya.parameters.WCoefficients()
        #LO and power corrections up to 1/mb^3
        par.alphas = 0
        self.assertAlmostEqual(kolya.Elmoments.moment_2_KIN_MS(1, par, hqe, wc, flag_TEST=0,  flag_includeNLOpw=0, flag_includeNNLO=0)/(0.09006715988696419),1.,delta=1e-7)

        #NLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.Elmoments.moment_2_KIN_MS(1, par, hqe, wc, flag_TEST=0,  flag_includeNLOpw=0, flag_includeNNLO=0)/(0.08971232000364629),1.,delta=1e-7)

        #NNLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.Elmoments.moment_2_KIN_MS(1, par, hqe, wc, flag_TEST=0,  flag_includeNLOpw=0, flag_includeNNLO=1)/(0.0898933511348814),1.,delta=1e-7)

    def test_moment3(self):
        par = kolya.parameters.physical_parameters(mbkin=4.573,mcMS=1.092,scale_mcMS=2.0,scale_alphas=4.573)
        hqe = kolya.parameters.LSSA_HQE_parameters(muG = 0.306, rhoD = 0.185, rhoLS = -0.13, mupi = 0.477)
        wc = kolya.parameters.WCoefficients()
        #LO and power corrections up to 1/mb^3
        par.alphas = 0
        self.assertAlmostEqual(kolya.Elmoments.moment_3_KIN_MS(1, par, hqe, wc, flag_TEST=0,  flag_includeNLOpw=0, flag_includeNNLO=0)/(0.00032328746320159363),1.,delta=1e-7)

        #NLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.Elmoments.moment_3_KIN_MS(1, par, hqe, wc, flag_TEST=0,  flag_includeNLOpw=0, flag_includeNNLO=0)/(0.00132444795891063),1.,delta=1e-7)

        #NNLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.Elmoments.moment_3_KIN_MS(1, par, hqe, wc, flag_TEST=0,  flag_includeNLOpw=0, flag_includeNNLO=1)/(0.0019771782836996024),1.,delta=1e-7)

    def test_moment4(self):
        par = kolya.parameters.physical_parameters(mbkin=4.573,mcMS=1.092,scale_mcMS=2.0,scale_alphas=4.573)
        hqe = kolya.parameters.LSSA_HQE_parameters(muG = 0.306, rhoD = 0.185, rhoLS = -0.13, mupi = 0.477)
        wc = kolya.parameters.WCoefficients()
        #LO and power corrections up to 1/mb^3
        par.alphas = 0
        self.assertAlmostEqual(kolya.Elmoments.moment_4_KIN_MS(1, par, hqe, wc, flag_TEST=0,  flag_includeNLOpw=0, flag_includeNNLO=0)/(0.015366977146071992),1.,delta=1e-7)

        #NLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.Elmoments.moment_4_KIN_MS(1, par, hqe, wc, flag_TEST=0,  flag_includeNLOpw=0, flag_includeNNLO=0)/(0.015948983488793988),1.,delta=1e-7)

        #NNLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.Elmoments.moment_4_KIN_MS(1, par, hqe, wc, flag_TEST=0,  flag_includeNLOpw=0, flag_includeNNLO=1)/(0.01647516265563161),1.,delta=1e-7)


if __name__ == '__main__':
   unittest.main()
