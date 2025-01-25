import unittest
import kolya

class TestNNLO_Q2Moments(unittest.TestCase):

    def test_moment0(self):
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(0,0.2533419586350071,0.2343866413487073),-3.839941403875702,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(0,0.2700445176408042,0.2438747687227233),-3.226363176983251,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(0,0.3998392385483405,0.2650518492716973),-0.8231354645337,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(0,0.314312032257619,0.2206924465651549),-3.085894792309638,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(0,0.1621035863424065,0.2748658685063988),-4.285301365970013,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(0,0.3329294080537699,0.2373907588453299),-2.30213469407281,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(0,0.2086574233517941,0.2755785375854265),-3.402167341834448,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(0,0.2441713914390166,0.2680169852075127),-2.993815098503445,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(0,0.2850772706152723,0.2949923026329988),-1.694516454435454,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(0,0.2917679202576056,0.2701635422198509),-2.152795165547662,delta=1e-5)

    def test_moment1(self):
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(1,0.4051111205398817,0.261985799318543),-0.370126986894653,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(1,0.1571956425283412,0.2818806225357643),-1.203218908608645,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(1,0.3838733409657933,0.2710099483350997),-0.3936579208688438,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(1,0.1658110476561441,0.2570508282043242),-1.487684418811294,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(1,0.4251605778689352,0.2192553566623165),-0.6497656095152269,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(1,0.4120380542454972,0.2929225977194618),-0.1578235315409456,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(1,0.0832454983695175,0.2854922594986116),-1.330174758515578,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(1,0.1740531105068807,0.2208197042685982),-2.002621035924855,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(1,0.1112002279263786,0.2016280900228591),-2.561994247877796,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(1,0.0836092311312032,0.2193921199562485),-2.304336507403694,delta=1e-5)

    def test_moment2(self):
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(2,0.4201542496787878,0.2931177721393452),-0.05989158787590583,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(2,0.3963859360853227,0.2224796812916041),-0.3703936927685208,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(2,0.07171807286425347,0.205617206531785),-0.891811676225995,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(2,0.1738501909516447,0.2696436292375997),-0.4307250823139493,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(2,0.1687330346468034,0.2585869708488234),-0.4914560595636873,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(2,0.02966408613728938,0.2099838285577213),-0.858407880195115,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(2,0.3123192016115292,0.2002187046355946),-0.7090463165135682,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(2,0.2405024998810754,0.2488957405702003),-0.4864174594905871,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(2,0.01497575505743409,0.2077614926404165),-0.876982108417004,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(2,0.1336979637549896,0.2243404975114056),-0.7276405503077353,delta=1e-5)

    def test_moment3(self):
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(3,0.4713960618056971,0.2331044103137491),-0.07782622691600373,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(3,0.05044101496438014,0.2774125263728268),-0.1421547762256339,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(3,0.06301032809821027,0.2255795827286314),-0.2787728988310595,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(3,0.3862646444002633,0.279517668685715),-0.06192025811843417,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(3,0.2195516090218646,0.2587768555282135),-0.1711479572883179,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(3,0.121015109064587,0.2125224104391681),-0.3252391306133142,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(3,0.3476861391681463,0.2743388385007445),-0.0918298131476576,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(3,0.2601328318715642,0.2837020274841251),-0.110742832331363,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(3,0.3918263622492314,0.2258819103964762),-0.1718110756501725,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(3,0.3045945220243244,0.2156254478370369),-0.2685165035307379,delta=1e-5)

    def test_moment4(self):
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(4,0.02506783777789018,0.2700016769464447),-0.05836601527062431,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(4,0.001263469033419895,0.2643750674037002),-0.06386230790260533,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(4,0.0819527909534268,0.2471314114598355),-0.0835938806365643,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(4,0.3741558208928819,0.2711825267454641),-0.03619847390097064,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(4,0.1632126891174207,0.2701619281460059),-0.0577551763285618,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(4,0.0842808768560721,0.2160821573385567),-0.132576702159918,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(4,0.0794712632718293,0.2863958863565778),-0.04462775035269788,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(4,0.3453058168103717,0.2109693229333171),-0.122650394452903,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(4,0.0904313811295192,0.2612663751969972),-0.06706245513764149,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2Q2(4,0.3584311189498905,0.2127922236971076),-0.1155799811834115,delta=1e-5)


if __name__ == '__main__':
   unittest.main()
