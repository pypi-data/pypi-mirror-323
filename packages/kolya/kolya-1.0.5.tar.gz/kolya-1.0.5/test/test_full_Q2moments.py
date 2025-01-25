import unittest
import kolya

class TestFull_Q2Moments(unittest.TestCase):

    def test_moment1(self):
        par = kolya.parameters.physical_parameters(mbkin=4.573,mcMS=1.092,scale_mcMS=2.0,scale_alphas=4.573)
        hqe = kolya.parameters.LSSA_HQE_parameters(muG = 0.306, rhoD = 0.185, rhoLS = -0.13, mupi = 0.477)
        wc = kolya.parameters.WCoefficients()
        #LO and power corrections up to 1/mb^3
        par.alphas = 0
        self.assertAlmostEqual(kolya.Q2moments.moment_1_KIN_MS(1, par, hqe, wc, flag_includeNLOpw=0, flag_includeNNLO=0)/(4.860330845379277),1.0,delta=1e-7)

        #NLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.Q2moments.moment_1_KIN_MS(1, par, hqe, wc, flag_includeNLOpw=0, flag_includeNNLO=0)/(4.888060949140881),1.,delta=1e-7)

        #NNLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.Q2moments.moment_1_KIN_MS(1, par, hqe, wc, flag_includeNLOpw=0, flag_includeNNLO=1)/(4.908936327219284),1.,delta=1e-7)

        #NNLO partonic and NLO power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.Q2moments.moment_1_KIN_MS(1, par, hqe, wc, flag_includeNLOpw=1, flag_includeNNLO=1)/(4.876084903039209),1.,delta=1e-7)

    def test_moment2(self):
        par = kolya.parameters.physical_parameters(mbkin=4.573,mcMS=1.092,scale_mcMS=2.0,scale_alphas=4.573)
        hqe = kolya.parameters.LSSA_HQE_parameters(muG = 0.306, rhoD = 0.185, rhoLS = -0.13, mupi = 0.477)
        wc = kolya.parameters.WCoefficients()
        #LO and power corrections up to 1/mb^3
        par.alphas = 0
        self.assertAlmostEqual(kolya.Q2moments.moment_2_KIN_MS(1, par, hqe, wc, flag_includeNLOpw=0, flag_includeNNLO=0)/(5.939600917387921),1.0,delta=1e-7)

        #NLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.Q2moments.moment_2_KIN_MS(1, par, hqe, wc, flag_includeNLOpw=0, flag_includeNNLO=0)/(5.9905935491408755),1.,delta=1e-7)

        #NNLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.Q2moments.moment_2_KIN_MS(1, par, hqe, wc, flag_includeNLOpw=0, flag_includeNNLO=1)/(6.060115045058632),1.,delta=1e-7)

        #NNLO partonic and NLO power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.Q2moments.moment_2_KIN_MS(1, par, hqe, wc, flag_includeNLOpw=1, flag_includeNNLO=1)/(6.022626173802175),1.,delta=1e-7)

    def test_moment3(self):
        par = kolya.parameters.physical_parameters(mbkin=4.573,mcMS=1.092,scale_mcMS=2.0,scale_alphas=4.573)
        hqe = kolya.parameters.LSSA_HQE_parameters(muG = 0.306, rhoD = 0.185, rhoLS = -0.13, mupi = 0.477)
        wc = kolya.parameters.WCoefficients()
        #LO and power corrections up to 1/mb^3
        par.alphas = 0
        self.assertAlmostEqual(kolya.Q2moments.moment_3_KIN_MS(1, par, hqe, wc, flag_includeNLOpw=0, flag_includeNNLO=0)/(2.104096270341188),1.0,delta=1e-7)

        #NLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.Q2moments.moment_3_KIN_MS(1, par, hqe, wc, flag_includeNLOpw=0, flag_includeNNLO=0)/(2.3772794345439596),1.,delta=1e-7)

        #NNLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.Q2moments.moment_3_KIN_MS(1, par, hqe, wc, flag_includeNLOpw=0, flag_includeNNLO=1)/(2.6263429790243924),1.,delta=1e-7)

        #NNLO partonic and NLO power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.Q2moments.moment_3_KIN_MS(1, par, hqe, wc, flag_includeNLOpw=1, flag_includeNNLO=1)/(3.261125213393213),1.,delta=1e-7)

    def test_moment4(self):
        par = kolya.parameters.physical_parameters(mbkin=4.573,mcMS=1.092,scale_mcMS=2.0,scale_alphas=4.573)
        hqe = kolya.parameters.LSSA_HQE_parameters(muG = 0.306, rhoD = 0.185, rhoLS = -0.13, mupi = 0.477)
        wc = kolya.parameters.WCoefficients()
        #LO and power corrections up to 1/mb^3
        par.alphas = 0
        self.assertAlmostEqual(kolya.Q2moments.moment_4_KIN_MS(1, par, hqe, wc, flag_includeNLOpw=0, flag_includeNNLO=0)/(44.881410632624466),1.0,delta=1e-7)

        #NLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.Q2moments.moment_4_KIN_MS(1, par, hqe, wc, flag_includeNLOpw=0, flag_includeNNLO=0)/(50.14494226134187),1.,delta=1e-7)

        #NNLO partonic and power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.Q2moments.moment_4_KIN_MS(1, par, hqe, wc, flag_includeNLOpw=0, flag_includeNNLO=1)/(53.588745353937924),1.,delta=1e-7)

        #NNLO partonic and NLO power corrections up to 1/mb^3
        par.alphas = 0.2186
        self.assertAlmostEqual(kolya.Q2moments.moment_4_KIN_MS(1, par, hqe, wc, flag_includeNLOpw=1, flag_includeNNLO=1)/(60.68895506838997),1.,delta=1e-7)


if __name__ == '__main__':
   unittest.main()
