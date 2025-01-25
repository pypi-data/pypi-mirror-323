import unittest
import kolya

class TestFull_MXMoments(unittest.TestCase):

    def test_moment1(self):
        par = kolya.parameters.physical_parameters(mbkin=4.573,mcMS=1.092,scale_mcMS=2.0,scale_alphas=4.573)
        hqe = kolya.parameters.LSSA_HQE_parameters(muG = 0.306, rhoD = 0.185, rhoLS = -0.13, mupi = 0.477)
        wc = kolya.parameters.WCoefficients()
        #LO and power corrections up to 1/mb^3
        par.alphas = 0
        self.assertAlmostEqual(kolya.MXmoments.moment_1_KIN_MS(1, par, hqe, wc, flag_TEST=0, flag_includeNLOpw=0, flag_includeNNLO=0)/(4.3081119873532),1.,delta=1e-7)

        #NLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.MXmoments.moment_1_KIN_MS(1, par, hqe, wc, flag_TEST=0, flag_includeNLOpw=0, flag_includeNNLO=0)/(4.35834766900633),1.,delta=1e-7)

        #NNLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.MXmoments.moment_1_KIN_MS(1, par, hqe, wc, flag_TEST=0, flag_includeNLOpw=0, flag_includeNNLO=1)/(4.384736822567139),1.,delta=1e-7)

    def test_moment2(self):
        par = kolya.parameters.physical_parameters(mbkin=4.573,mcMS=1.092,scale_mcMS=2.0,scale_alphas=4.573)
        hqe = kolya.parameters.LSSA_HQE_parameters(muG = 0.306, rhoD = 0.185, rhoLS = -0.13, mupi = 0.477)
        wc = kolya.parameters.WCoefficients()
        #LO and power corrections up to 1/mb^3
        par.alphas = 0
        self.assertAlmostEqual(kolya.MXmoments.moment_2_KIN_MS(1, par, hqe, wc, flag_TEST=0, flag_includeNLOpw=0, flag_includeNNLO=0)/(0.9649336577797742),1.,delta=1e-7)

        #NLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.MXmoments.moment_2_KIN_MS(1, par, hqe, wc, flag_TEST=0, flag_includeNLOpw=0, flag_includeNNLO=0)/(1.1713598673586554),1.,delta=1e-7)

        #NNLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.MXmoments.moment_2_KIN_MS(1, par, hqe, wc, flag_TEST=0, flag_includeNLOpw=0, flag_includeNNLO=1)/(1.347168702186871),1.,delta=1e-7)

    def test_moment3(self):
        par = kolya.parameters.physical_parameters(mbkin=4.573,mcMS=1.092,scale_mcMS=2.0,scale_alphas=4.573)
        hqe = kolya.parameters.LSSA_HQE_parameters(muG = 0.306, rhoD = 0.185, rhoLS = -0.13, mupi = 0.477)
        wc = kolya.parameters.WCoefficients()
        #LO and power corrections up to 1/mb^3
        par.alphas = 0
        self.assertAlmostEqual(kolya.MXmoments.moment_3_KIN_MS(1, par, hqe, wc, flag_TEST=0, flag_includeNLOpw=0, flag_includeNNLO=0)/(4.931150093901361),1.,delta=1e-7)

        #NLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.MXmoments.moment_3_KIN_MS(1, par, hqe, wc, flag_TEST=0, flag_includeNLOpw=0, flag_includeNNLO=0)/(4.561377947316313),1.,delta=1e-7)

        #NNLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.MXmoments.moment_3_KIN_MS(1, par, hqe, wc, flag_TEST=0, flag_includeNLOpw=0, flag_includeNNLO=1)/(4.374808189227854),1.,delta=1e-7)

    def test_moment4(self):
        par = kolya.parameters.physical_parameters(mbkin=4.573,mcMS=1.092,scale_mcMS=2.0,scale_alphas=4.573)
        hqe = kolya.parameters.LSSA_HQE_parameters(muG = 0.306, rhoD = 0.185, rhoLS = -0.13, mupi = 0.477)
        wc = kolya.parameters.WCoefficients()
        #LO and power corrections up to 1/mb^3
        par.alphas = 0
        self.assertAlmostEqual(kolya.MXmoments.moment_4_KIN_MS(1, par, hqe, wc, flag_TEST=0, flag_includeNLOpw=0, flag_includeNNLO=0)/(5.166344589757122),1.,delta=1e-7)

        #NLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.MXmoments.moment_4_KIN_MS(1, par, hqe, wc, flag_TEST=0, flag_includeNLOpw=0, flag_includeNNLO=0)/(9.47454857835687),1.,delta=1e-7)

        #NNLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.MXmoments.moment_4_KIN_MS(1, par, hqe, wc, flag_TEST=0, flag_includeNLOpw=0, flag_includeNNLO=1)/(12.82885491852754),1.,delta=1e-7)


if __name__ == '__main__':
   unittest.main()
