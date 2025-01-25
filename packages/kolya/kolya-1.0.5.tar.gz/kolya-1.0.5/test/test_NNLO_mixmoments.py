import unittest
import kolya

class TestBLM_MixMoments(unittest.TestCase):

    def test_moment_0_0(self):
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,0,0.00350034,0.255325),-1.17404942099908669882211860632991122735,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,0,0.392515,0.266493),-0.29902914670744505095175338672978910934,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,0,0.165407,0.286664),-0.87925323458214389058838280230652854604,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,0,0.35659,0.237666),-0.58169340908515140649265556854256499569,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,0,0.303456,0.261172),-0.67493922480138903335127323187094862447,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,0,0.376698,0.275126),-0.33092379456258705509573798923291308200,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,0,0.317446,0.283195),-0.513864142031193101831381043266050069131,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,0,0.0776987,0.257369),-1.14905632881274702901836531931292271394,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,0,0.211043,0.216826),-1.26545871884429462813543672159826672164,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,0,0.202294,0.228022),-1.20326534198858268494747980875657733790,delta=1e-5)

    def test_moment_0_1(self):
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,1,0.137983,0.245292),-0.73822308012205236412714496290380689876,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,1,0.0321878,0.256022),-0.71804368252752825360432420346449819143,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,1,0.275729,0.216519),-0.67176856184331906531994726229841019367,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,1,0.347845,0.270465),-0.27319044482765410769077634199925940215,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,1,0.128921,0.245887),-0.741397136767712645371386530873169784118,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,1,0.0557448,0.239791),-0.80004135746914091989498496998000039552,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,1,0.08731,0.288855),-0.55855905083233562649501462557726981902,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,1,0.100069,0.258731),-0.69169503935488401518295881554562126870,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,1,0.303424,0.267153),-0.38635034488520358408341196859998483566,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,1,0.191611,0.212546),-0.85904479301313963932797768215183261067,delta=1e-5)

    def test_moment_0_2(self):
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,2,0.219508,0.230122),-0.45266623918910840617503628841904126180,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,2,0.197402,0.275458),-0.32391218589913419866127887521155651374,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,2,0.287453,0.207803),-0.43999442912882559921510815503757495895,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,2,0.250649,0.209025),-0.49415805737198544909265851155125186147,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,2,0.1443,0.26594),-0.3837720861359278102538751842063750124,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,2,0.454613,0.251117),-0.01174650743242538202036502438259587602,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,2,0.329248,0.288825),-0.1535382249166208572837271561642994045,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,2,0.0644105,0.295619),-0.31442840894704888113827867238738250294,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,2,0.385629,0.295982),-0.07361875304247606784483072872806189096,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,2,0.340018,0.286111),-0.14480308212765450150211701433830509622,delta=1e-5)

    def test_moment_0_3(self):
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,3,0.308718,0.215693),-0.23963956643181755549411354815864720138,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,3,0.105815,0.226022),-0.34085099756912536557640490661371790591,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,3,0.250513,0.253487),-0.20976753932736826175629694856944941201,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,3,0.063348,0.223491),-0.35262215942110634140666064079938133664,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,3,0.330062,0.271822),-0.11208640208198349518378501568693694692,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,3,0.343486,0.291689),-0.0769129077377077293753013928419500997,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,3,0.113827,0.216349),-0.36760945091257504194077941541458519576,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,3,0.122752,0.239569),-0.30087553594493698567073553653505005134,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,3,0.108066,0.244425),-0.2910405632327661912086621487776525974,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,3,0.114465,0.287695),-0.19463355689454026796449596827338822010,delta=1e-5)

    def test_moment_0_4(self):
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,4,0.0257309,0.241872),-0.1883313207725278884834983418264391646,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,4,0.127033,0.226077),-0.21289420632911371235669191965956633313,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,4,0.29528,0.236117),-0.13202403943601903604663220790927696743,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,4,0.306302,0.233936),-0.12798384588324443231965289010035349978,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,4,0.153663,0.280571),-0.1203369613925040627555369997082834175,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,4,0.0330403,0.262221),-0.15425317921725578844493598757017746473,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,4,0.210055,0.222313),-0.19986267617291908052591140108483924268,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,4,0.0675221,0.293413),-0.1109906969943722422471431128654079252,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,4,0.409311,0.264688),-0.0280057887436685443834818712052660754,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(0,4,0.0903433,0.264868),-0.14864483501291476695512599791448741765,delta=1e-5)

    def test_moment_1_0(self):
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,0,0.0851139,0.296537),-0.17227695480619515093137458184490658207,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,0,0.401591,0.287622),-0.0387026594992803761977068593904999387,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,0,0.409831,0.274171),-0.04149167019859668338911757430151242291,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,0,0.200918,0.256802),-0.2251090346959032392321751546242015590,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,0,0.171456,0.255403),-0.23689956143582352082318457657939491274,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,0,0.147325,0.290007),-0.1777198471504734275834704897993824915,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,0,0.125177,0.271917),-0.21224266122604748360187554098014284929,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,0,0.154614,0.270307),-0.21118054887392331234780865207753795672,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,0,0.0764261,0.252311),-0.25426602280300993403802939480920281372,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,0,0.391343,0.253419),-0.08109611741393943013624783318790716931,delta=1e-5)

    def test_moment_1_1(self):
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,1,0.318446,0.296819),-0.0571302917108834421282349421963940150,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,1,0.132882,0.276357),-0.1278588608595374484147268536865065412,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,1,0.18574,0.224159),-0.20159637745367492235040422389877198108,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,1,0.380304,0.27022),-0.04545098429294366903730966310606226797,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,1,0.167329,0.27479),-0.12645067867670249930132095398164437675,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,1,0.086833,0.262162),-0.1490645267740594116857350583662816867,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,1,0.00231883,0.252266),-0.1642306014418285728752711656951480542,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,1,0.0391734,0.260422),-0.1520303923738140180715055649109798818,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,1,0.0644586,0.299744),-0.1026733204711169993319654401038304038,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,1,0.0148976,0.278907),-0.1270228561411505288638094436184277963,delta=1e-5)

    def test_moment_1_2(self):
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,2,0.0146306,0.231355),-0.13088629465723650198731722320184075219,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,2,0.124867,0.278729),-0.0786437364455174080129347219065964407,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,2,0.124689,0.22839),-0.13349900882486231132187565539684718202,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,2,0.000641003,0.29465),-0.0666692159137724048471839584957334872,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,2,0.28346,0.23459),-0.0969541251280702003731831259227635411,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,2,0.190028,0.258966),-0.0926901222520863255249806679049961720,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,2,0.282028,0.297743),-0.0439676736272194124428542692102754233,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,2,0.108429,0.229107),-0.13309764810164243315601834269562681690,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,2,0.377576,0.266058),-0.03150997566462464594787054875570451701,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,2,0.0197941,0.261971),-0.09556252196893089259066259472157174803,delta=1e-5)

    def test_moment_1_3(self):
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,3,0.3209,0.210934),-0.0734536649190104496149649539414418463,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,3,0.0907473,0.264634),-0.0590182217898097949033304543317826999,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,3,0.0911363,0.250407),-0.06962487139551953632358083869425319483,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,3,0.342431,0.241885),-0.0419624146761869846257287950668349886,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,3,0.45668,0.231758),-0.00236203040606156337251279698493720464,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,3,0.42695,0.253569),-0.00906740522099312125817401507416823759,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,3,0.221739,0.215493),-0.0944181467243835568498950965973127183,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,3,0.354714,0.236643),-0.0410364180370739912230625756616933199,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,3,0.432826,0.299856),-0.0010412786308232768811057964162061833,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(1,3,0.345495,0.249946),-0.03629671566358195967853755365436201083,delta=1e-5)

    def test_moment_2_0(self):
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,0,0.179738,0.240347),-0.08495402509662309129591537542438060997,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,0,0.135101,0.288722),-0.0506317066217403055560909875231495688,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,0,0.308889,0.22124),-0.07855363903270282658164179877758020156,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,0,0.166392,0.227653),-0.09787771186269598214374157842396944516,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,0,0.146275,0.236361),-0.0901442323759919902100461421194106621,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,0,0.324803,0.224722),-0.0694296990876755332388655975254979943,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,0,0.226879,0.265751),-0.06013492519455761485305265758758101884,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,0,0.0730014,0.220438),-0.10711970142668150930238905008053959767,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,0,0.157701,0.262077),-0.06794629006813787897364721829649489238,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,0,0.134742,0.238803),-0.08815675990170998845879075116725140365,delta=1e-5)

    def test_moment_2_1(self):
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,1,0.279101,0.234018),-0.0516108625134515532855682009210169746,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,1,0.403423,0.258862),-0.0116248775964484907917531950345744158,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,1,0.433101,0.278374),-0.0018943593315370125278168027649816092,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,1,0.151306,0.22306),-0.07053689176890450111091300095147916359,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,1,0.319309,0.261132),-0.02914488637158642533272214227343110947,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,1,0.381772,0.271242),-0.0131450201613733850819313924225615356,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,1,0.215655,0.236984),-0.0573539306386694613390571963598478445,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,1,0.184776,0.208967),-0.0812164263610442243468588569974865932,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,1,0.308,0.270719),-0.0271108907520656908688990442506046635,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,1,0.0592975,0.22376),-0.07065570375859376950044502254773971850,delta=1e-5)

    def test_moment_2_2(self):
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,2,0.289053,0.21408),-0.04461356042887980161069610492140245706,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,2,0.357013,0.249434),-0.01723804132438261111213767215075262970,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,2,0.396453,0.231318),-0.01504873970361187334276050720653036863,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,2,0.0677698,0.235483),-0.0417771962473792267395581771601211394,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,2,0.201716,0.261495),-0.0285155064813935823203736173510303267,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,2,0.248452,0.229061),-0.04080789360428689000267201688836175831,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,2,0.0158082,0.242396),-0.03830352295972534095483041487978451577,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,2,0.0397928,0.253978),-0.0330116435185878431835042374026252795,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,2,0.43893,0.243863),-0.0031594386221397372814100511735476922,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(2,2,0.0229302,0.225335),-0.0473610757784942762190833808247272543,delta=1e-5)

    def test_moment_3_0(self):
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(3,0,0.365418,0.245152),-0.01419076182051267227817191168403216138,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(3,0,0.408029,0.277985),-0.0032572851516981084422709870337433334,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(3,0,0.44,0.21966),-0.00548320425731693542928005982039541030,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(3,0,0.29467,0.259372),-0.0188851230414143977386431537868746941,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(3,0,0.0777221,0.262888),-0.0235570639530119806778159857228310682,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(3,0,0.128794,0.287567),-0.0166670995647128869688823068576039033,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(3,0,0.173848,0.211141),-0.04529892301989411489107457266738800361,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(3,0,0.143042,0.203447),-0.05001838570038973227134520577225767285,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(3,0,0.0409879,0.220392),-0.0408439203834381545744330575798124152,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(3,0,0.0324135,0.270269),-0.0213049283551181108317521887283660544,delta=1e-5)

    def test_moment_3_1(self):
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(3,1,0.342616,0.281319),-0.0059964674250048199017531308120786344,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(3,1,0.232442,0.249221),-0.0179251223104167656430296955305995059,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(3,1,0.318019,0.289324),-0.0064175446820397500603881284637006290,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(3,1,0.195626,0.233192),-0.02345111471032334765538439497994591815,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(3,1,0.0119678,0.223746),-0.0272423283972869546224735307388021842,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(3,1,0.0788443,0.216194),-0.0301422117223545952202873070085645370,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(3,1,0.0384819,0.210461),-0.03251606392813263691517405148103651036,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(3,1,0.094832,0.291992),-0.0100998459407464981775775230213813031,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(3,1,0.458629,0.239505),-0.000108883906979760764901502652398851,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(3,1,0.0436058,0.285302),-0.0112064196245005525116752167051984830,delta=1e-5)

    def test_moment_4_0(self):
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(4,0,0.211753,0.250545),-0.0104944116891273227130330493348266678,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(4,0,0.268645,0.250999),-0.0094695006461800645394002299083923813,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(4,0,0.356606,0.252439),-0.0053752917191815997763779900426431926,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(4,0,0.00663449,0.22188),-0.01669308744609585503629068552473637240,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(4,0,0.25488,0.273502),-0.0066780897540199637227731569275787118,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(4,0,0.309474,0.270886),-0.0055239728486659182737303571348392588,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(4,0,0.392246,0.230638),-0.0054917435416727152928130834248339052,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(4,0,0.0754374,0.258275),-0.0095475361018558283554236395227243137,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(4,0,0.430569,0.260935),-0.0006614551113967214089544186198523321,delta=1e-5)
      self.assertAlmostEqual(kolya.NNLOpartonic.X2mixBLM(4,0,0.367529,0.270904),-0.0031373912042888304542463443312537129,delta=1e-5)


if __name__ == '__main__':
   unittest.main()
