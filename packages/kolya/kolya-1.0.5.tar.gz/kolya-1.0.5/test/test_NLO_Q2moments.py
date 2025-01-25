import unittest
import kolya

class TestNLO_Q2Moments(unittest.TestCase):

    def test_moment0(self):
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(0,'SM',0.202052,0.29397),-0.3741950774374182367702108741966560018,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(0,'SM',0.204759,0.223142),-0.60184610864179322287637910051578923690,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(0,'SM',0.436552,0.204079),-0.1439768822718428448984498798051425168,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(0,'SM',0.0482,0.230047),-1.0662824387492513233985143562841780617,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(0,'SM',0.00831386,0.261884),-1.0332392827392591390173781069690332646,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(0,'SM',0.128973,0.27345),-0.6240168027198770470928476411697984776,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(0,'SM',0.418726,0.281097),-0.050686453214004940745989430811329136,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(0,'SM',0.359461,0.276915),-0.1254579984011359634040339156859197736,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(0,'SM',0.130662,0.201297),-0.9237291533743479267656439628129713179,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(0,'SM',0.507682,0.269566),-0.0048801344594300928746986095465735171,delta=1e-5)

    def test_moment1(self):
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(1,'SM',0.292796,0.229791),-0.1404225791134492353899884960465120459,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(1,'SM',0.0484892,0.26025),-0.2086652208115846325717430829809963760,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(1,'SM',0.0316629,0.273052),-0.1924912851213970298975948055921389241,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(1,'SM',0.373905,0.262528),-0.0566149632756560825720706746391975299,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(1,'SM',0.50665,0.264595),-0.0039474477197736452563779773673979045,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(1,'SM',0.0682501,0.295679),-0.157794221730074564398555077525516837,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(1,'SM',0.428207,0.271153),-0.0249710111742321069194625877541435820,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(1,'SM',0.129156,0.284835),-0.1551908003468334331933613088845460579,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(1,'SM',0.449597,0.259753),-0.0230311003870030348234764513318465916,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(1,'SM',0.447306,0.206866),-0.0631232597353422885782249796051171291,delta=1e-5)

    def test_moment2(self):
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(2,'SM',0.376949,0.240021),-0.033881727731211756864124946529500830,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(2,'SM',0.463717,0.22773),-0.0191040430282888406273877513021856024,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(2,'SM',0.32703,0.203308),-0.0666326544695584828148462634217504864,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(2,'SM',0.329424,0.248793),-0.0398473806751100548457288083652966338,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(2,'SM',0.237696,0.22333),-0.0709928066040496364747008595290662464,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(2,'SM',0.465883,0.207037),-0.027300537595921657723315485555561018,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(2,'SM',0.47075,0.252961),-0.009419539608956499173483004850367011,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(2,'SM',0.453041,0.271436),-0.0075535135384098195493673576706551487,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(2,'SM',0.443499,0.274751),-0.008211626401448744953015727299858677,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(2,'SM',0.309104,0.27016),-0.033771718337172748689055095448973289,delta=1e-5)

    def test_moment3(self):
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(3,'SM',0.329914,0.216964),-0.025637834318308101605703848291423157,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(3,'SM',0.383055,0.27642),-0.0079246770713890366031782266537491378,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(3,'SM',0.303986,0.234097),-0.0224004447770680143040142571405733409,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(3,'SM',0.320428,0.255606),-0.016051363794340472440326416972373748,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(3,'SM',0.500128,0.279223),-0.000417687691708998012515301899321069,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(3,'SM',0.386834,0.299059),-0.004623306994710844846015142567118297,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(3,'SM',0.391142,0.266421),-0.00898549925837751830647913230860647,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(3,'SM',0.0705728,0.285102),-0.015551174398918772086154032727745563,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(3,'SM',0.592912,0.217452),-0.000460850040205508266356856975187777,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(3,'SM',0.370879,0.203024),-0.0264823686616728922527636610710697327,delta=1e-5)

    def test_moment4(self):
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(4,'SM',0.310205,0.287794),-0.004178610990928565917706177549207100,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(4,'SM',0.185275,0.256581),-0.008102747656108422824425217464204899,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(4,'SM',0.347538,0.239893),-0.0080564990031777990465533697419426667,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(4,'SM',0.46373,0.259446),-0.002187459020557342696966802517156678,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(4,'SM',0.124387,0.267926),-0.00701837362441931990145112633620372,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(4,'SM',0.0423298,0.217584),-0.013605601275056271946900351522811551,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(4,'SM',0.0138499,0.246811),-0.00937391691466916558756098435219277,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(4,'SM',0.409822,0.255115),-0.00447269598392886607187624116976419,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(4,'SM',0.434027,0.266437),-0.002712375697122813870537443150840450,delta=1e-5)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2(4,'SM',0.18937,0.232136),-0.0111972609608763404212019221262045052,delta=1e-5)

class TestNLO_Q2Moments_DerivativeQ2(unittest.TestCase):

    def test_moment0(self):
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(0,0.202052,0.29397),0.2212955179331370507202606682680996315e1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(0,0.204759,0.223142),0.28439721862942092946907153209961489326e1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(0,0.436552,0.204079),0.14607710368382999546991410750262208098e1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(0,0.0482,0.230047),0.34093675891450356422988738701821607013e1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(0,0.00831386,0.261884),0.31742013914905893858017810162885954449e1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(0,0.128973,0.27345),0.27160585005681709845795962902526358982e1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(0,0.418726,0.281097),0.91734482373050225502981701721614488284e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(0,0.359461,0.276915),0.13946144397883998454367134084045012403e1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(0,0.130662,0.201297),0.34072177871277854921900056996533502629e1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(0,0.507682,0.269566),0.31377496464152314185597166698713519206e0,delta=1e-4)

    def test_moment1(self):
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(1,0.292796,0.229791),0.66246115504065149518065376202921988363e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(1,0.0484892,0.26025),0.15016844991155405064160940069036387577e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(1,0.0316629,0.273052),0.95182968193405357005811576866686096016e-1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(1,0.373905,0.262528),0.5297807165023036398334738079118163420e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(1,0.50665,0.264595),0.19090388962336997259364576564334148988e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(1,0.0682501,0.295679),0.183880305145539116603708813429820375e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(1,0.428207,0.271153),0.40048164344827319075154924167762559595e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(1,0.129156,0.284835),0.33693475275359089000525527600187445548e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(1,0.449597,0.259753),0.39320404571815182955871937782501441351e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(1,0.447306,0.206866),0.6064058007987206643797272155219387116e0,delta=1e-4)

    def test_moment2(self):
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(2,0.376949,0.240021),0.226187364446939017055485459710666472e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(2,0.463717,0.22773),0.22617254101814682547585823266423641691e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(2,0.32703,0.203308),0.24258411701233352493634666963965926828e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(2,0.329424,0.248793),0.20081017439597776495329447833242432076e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(2,0.237696,0.22333),0.15026052869662612263699965351855397392e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(2,0.465883,0.207037),0.2634320842361954323927786202378102870e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(2,0.47075,0.252961),0.17143198419113966798856149693139399594e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(2,0.453041,0.271436),0.15187264952396140844437769637748448323e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(2,0.443499,0.274751),0.15414232889629629015097628166410977485e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(2,0.309104,0.27016),0.1719444758363687620563017441292931963e0,delta=1e-4)

    def test_moment3(self):
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(3,0.329914,0.216964),0.76399047965771859655351362829921539593e-1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(3,0.383055,0.27642),0.6901256405848001549179863238045514324e-1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(3,0.303986,0.234097),0.60423555404614063522001714814253067192e-1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(3,0.320428,0.255606),0.6091911697940491524197233244377242990e-1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(3,0.500128,0.279223),0.33556277331059107276407210337418344992e-1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(3,0.386834,0.299059),0.57724035557905445382576553753911871e-1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(3,0.391142,0.266421),0.75196708240703390608262409890652536118e-1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(3,0.0705728,0.285102),0.9809873882722852047014974414748443275e-3,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(3,0.592912,0.217452),0.38850017576057883855704073857987642392e-1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(3,0.370879,0.203024),0.99922021162949101898457120402186195702e-1,delta=1e-4)

    def test_moment4(self):
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(4,0.310205,0.287794),0.151762078592023293489738435316424685264e-1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(4,0.185275,0.256581),0.31013371304317490476295242387569949058e-2,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(4,0.347538,0.239893),0.263031356875236709573745105546990951201e-1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(4,0.46373,0.259446),0.35527734734713366730884407348711485599e-1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(4,0.124387,0.267926),0.66680826174882853993336718118566816345e-3,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(4,0.0423298,0.217584),0.114176237826633548465903692989607195928e-4,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(4,0.0138499,0.246811),0.12223276139820397522847650765979311617e-6,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(4,0.409822,0.255115),0.34346509571109940111320714417764386486e-1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(4,0.434027,0.266437),0.33125149256733440329637180096414453225e-1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_DerivativeQ2(4,0.18937,0.232136),0.36514207646412367285806395431996686039e-2,delta=1e-4)

class TestNLO_Q2Moments_Derivativer(unittest.TestCase):

    def test_moment0(self):
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(0,0.202052,0.29397),0.292403e1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(0,0.204759,0.223142),0.366665e1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(0,0.436552,0.204079),0.177021e1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(0,0.0482,0.230047),0.513407e1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(0,0.00831386,0.261884),0.51855e1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(0,0.128973,0.27345),0.383606e1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(0,0.418726,0.281097),0.116815e1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(0,0.359461,0.276915),0.17421e1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(0,0.130662,0.201297),0.456152e1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(0,0.507682,0.269566),0.433307e0,delta=1e-4)

    def test_moment1(self):
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(1,0.292796,0.229791),0.12643e1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(1,0.0484892,0.26025),0.146203e1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(1,0.0316629,0.273052),0.138602e1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(1,0.373905,0.262528),0.828058e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(1,0.50665,0.264595),0.272003e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(1,0.0682501,0.295679),0.122188e1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(1,0.428207,0.271153),0.581278e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(1,0.129156,0.284835),0.12343e1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(1,0.449597,0.259753),0.567955e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(1,0.447306,0.206866),0.899268e0,delta=1e-4)

    def test_moment2(self):
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(2,0.376949,0.240021),0.471227e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(2,0.463717,0.22773),0.383626e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(2,0.32703,0.203308),0.664465e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(2,0.329424,0.248793),0.490769e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(2,0.237696,0.22333),0.652868e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(2,0.465883,0.207037),0.459836e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(2,0.47075,0.252961),0.272967e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(2,0.453041,0.271436),0.238999e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(2,0.443499,0.274751),0.244997e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(2,0.309104,0.27016),0.432336e0,delta=1e-4)

    def test_moment3(self):
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(3,0.329914,0.216964),0.309236e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(3,0.383055,0.27642),0.15675e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(3,0.303986,0.234097),0.275287e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(3,0.320428,0.255606),0.22274e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(3,0.500128,0.279223),0.498498e-1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(3,0.386834,0.299059),0.114632e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(3,0.391142,0.266421),0.172168e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(3,0.0705728,0.285102),0.187847e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(3,0.592912,0.217452),0.603575e-1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(3,0.370879,0.203024),0.328752e0,delta=1e-4)

    def test_moment4(self):
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(4,0.310205,0.287794),0.724516e-1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(4,0.185275,0.256581),0.111137e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(4,0.347538,0.239893),0.124428e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(4,0.46373,0.259446),0.698285e-1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(4,0.124387,0.267926),0.980686e-1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(4,0.0423298,0.217584),0.166782e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(4,0.0138499,0.246811),0.124076e0,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(4,0.409822,0.255115),0.929845e-1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(4,0.434027,0.266437),0.725324e-1,delta=1e-4)
      self.assertAlmostEqual(kolya.NLOpartonic.X1Q2_Derivativer(4,0.18937,0.232136),0.144096e0,delta=1e-4)


if __name__ == '__main__':
   unittest.main()
