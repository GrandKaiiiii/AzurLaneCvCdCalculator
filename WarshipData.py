class Warship:
    def __init__(self,name,parameter_100,parameter_200,type_arm1,eff_arm1,count_arm1,type_arm2,eff_arm2,count_arm2,type_arm3,eff_arm3,count_arm3,siren_buff):
        self.name = name#船名
        self.parameter_100 = parameter_100#爱100属性（包含[航空,装填,命中,幸运]四项影响输出计算的属性）
        self.atk_100 = self.parameter_100[0]#拆分
        self.load_100 = self.parameter_100[1]
        self.accurate_100 = self.parameter_100[2]
        self.fortune_100 = self.parameter_100[3]
        self.parameter_200 = parameter_200#婚200属性
        self.atk_200 = self.parameter_200[0]#拆分
        self.load_200 = self.parameter_200[1]
        self.accurate_200 = self.parameter_200[2]
        self.fortune_200 = self.parameter_200[3]
        self.type_arm1 = type_arm1#一号机槽可装备的舰载机种类，格式为列表，包含['Fighter','Bomber','Torpedo']中的若干项
        self.eff_arm1 = eff_arm1/100#一号机槽效率
        self.count_arm1 = count_arm1#一号机槽飞机数量
        self.type_arm2 = type_arm2#以下三项为二号机槽
        self.eff_arm2 = eff_arm2/100
        self.count_arm2 = count_arm2
        self.type_arm3 = type_arm3#以下三项为三号机槽
        self.eff_arm3 = eff_arm3/100
        self.count_arm3 = count_arm3
        self.siren_buff = siren_buff/100#科研船塞壬增伤

#舰船数据
Shinano = Warship('信浓',[443,128,80,32],[468,135,85,32],['Fighter','Bomber','Torpedo'],125,2,['Bomber'],130,3,['Torpedo'],140,4,0)#信浓
Hakuryu = Warship('白龙',[468,128,99,25],[488,135,105,25],['Fighter','Torpedo'],125,3,['Bomber'],150,4,['Bomber','Torpedo'],130,2,15)#白龙
Amagi = Warship('天城',[448,136,102,23],[473,144,107,23],['Fighter','Bomber'],145,3,['Bomber','Torpedo'],145,2,['Torpedo'],160,3,0)#天城cv
August = Warship('奥古斯特',[439,121,111,15],[464,128,117,15],['Fighter'],140,2,['Bomber'],110,3,['Torpedo'],140,3,15)#奥古斯特·冯·帕塞瓦尔
Implacable = Warship('怨仇',[444,128,97,79],[469,135,102,79],['Fighter'],140,3,['Fighter','Bomber','Torpedo'],130,3,['Torpedo'],130,3,0)#怨仇
YorkTown2 = Warship('约克城II',[458,137,97,70],[484,145,102,70],['Fighter'],120,2,['Bomber'],135,4,['Fighter','Bomber','Torpedo'],135,3,0)#约克城II
Enterprise = Warship('企业',[435,134,110,93],[459,142,116,93],['Fighter'],125,3,['Bomber'],125,3,['Torpedo'],125,2,0)#企业
Nakhimov = Warship('纳希莫夫',[468,130,110,0],[494,137,116,0],['Fighter'],140,3,['Fighter','Bomber','Torpedo'],140,3,['Torpedo'],140,3,15)#纳希莫夫海军上将

Freeze = [Implacable,August,Nakhimov]#定身辅奥古/怨仇
Core = [Shinano,YorkTown2]#航队核心信浓/约克城II
MainCarrier = [Hakuryu,Amagi,Enterprise]#打手白龙/天城/企业



