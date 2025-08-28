class Aircraft:
    def __init__(self,name,type,atk,cd,main_dmg_n,main_dmg_u,main_light,main_mid,main_heavy,main_eff,main_acc,co_dmg_n,co_dmg_u,co_light,co_mid,co_heavy,co_eff,co_acc):
        self.name = name#民间简称
        self.type = type#飞机类型
        self.atk = atk#航空加成
        self.cd = cd#标准cd
        self.main_dmg_n = main_dmg_n#主武器标伤
        self.main_dmg_u = main_dmg_u#主武器强化+11/+13伤害
        self.main_light = main_light/100#主武器对轻补正
        self.main_mid = main_mid/100#主武器对中补正
        self.main_heavy = main_heavy/100#主武器对重补正
        self.main_eff = main_eff/100#主武器属性效率（火箭弹/鱼雷100，航弹80，天袭者的火箭弹也为80）
        self.main_acc = main_acc#主武器命中率
        # 以下为副武器数据
        self.co_dmg_n = co_dmg_n
        self.co_dmg_u = co_dmg_u
        self.co_light = co_light/100
        self.co_mid = co_mid/100
        self.co_heavy = co_heavy/100
        self.co_eff = co_eff/100
        self.co_acc = co_acc

class Facility:
    def __init__(self,name,atk_n,atk_u,cd_buff,dmg_buff):
        self.name = name#民间简称
        self.atk_n = atk_n#标准航空加成
        self.atk_u = atk_u#强化+11/+13航空加成
        self.cd_buff = cd_buff/100#对cd影响
        self.dmg_buff = dmg_buff/100#对伤害影响

#战斗机区
La_9 = Aircraft('La-9','Fighter',65,11.6986,4*225,4*266,80,140,80,100,1,0,0,0,0,0,0,0)#试作舰载型La-9
F4U_VF17_JollyRogers = Aircraft('金海盗','Fighter',45,10.2022,2*380,2*448,80,90,110,80,0.474,0,0,0,0,0,0,0)#F4U(VF-17“海盗”中队)
#F6F_HellCat = Aircraft('地狱猫','Fighter',45,10.9,2*360,2*425,80,90,110,80,0.474,0,0,0,0,0,0,0)#F6F地狱猫
F6F_HellCat_HVAR = Aircraft('地狱火','Fighter',45,10.6478,6*100,6*118,140,110,50,100,1,0,0,0,0,0,0,0)#F6F地狱猫(HVAR搭载型)
BF_109G = Aircraft('BF109','Fighter',45,10.5813,4*160,4*189,110,140,50,100,1,0,0,0,0,0,0,0)#试作舰载型BF-109G
FW190A6 = Aircraft('FW190A','Fighter',45,11.1001,2*300,2*354,110,110,80,100,1,0,0,0,0,0,0,0)#试作舰载型FW-190 A-6/R6
XF5U_FlyingPancake = Aircraft('飞碟','Fighter',45,11.0003,2*416,2*491,80,95,115,80,0.478,0,0,0,0,0,0,0)#试作型XF5U飞碟
F7F_TigerCat = Aircraft('虎猫','Fighter',45,10.8141,2*416,2*491,80,95,115,80,0.478,0,0,0,0,0,0,0)#F7F虎猫
Hornet = Aircraft('海大黄蜂','Fighter',45,10.6146,2*416,2*491,80,95,115,80,0.478,0,0,0,0,0,0,0)#海大黄蜂

Fighters = [La_9,F4U_VF17_JollyRogers,F6F_HellCat_HVAR,BF_109G,FW190A6,XF5U_FlyingPancake,F7F_TigerCat,Hornet]
Fighters_Frequent = [La_9,F6F_HellCat_HVAR,BF_109G,FW190A6,XF5U_FlyingPancake]#可选择仅使用常用战斗机：La9，地狱火，BF109，FW190，飞碟

#轰炸机区
SB2C_HellDiver = Aircraft('SB2C','Bomber',25,11.8782,456,474,70,105,125,80,0.597,2*360,2*374,80,90,110,80,0.474)#SB2C地狱俯冲者
Su_2 = Aircraft('Su-2','Bomber',45,12.0046,200,236,100,100,100,80,0.478,0,0,0,0,0,0,0)#试作舰载型Su-2
J5N = Aircraft('天雷','Bomber',65,11.9979,3*432,3*510,80,110,130,80,0.559,0,0,0,0,0,0,0)#试作舰载型天雷
AD1_SkyRaider = Aircraft('天袭者','Bomber',65,13.1950,8*100,8*118,140,110,50,80,1,440,519,85,95,110,80,0.478)#AD-1天袭者
D4Y2A = Aircraft('彗星改','Bomber',45,9.9761,440,519,80,95,115,80,0.478,2*185,2*218,80,85,100,80,0.447)#彗星一二型甲

Bombers = [SB2C_HellDiver,Su_2,J5N,AD1_SkyRaider,D4Y2A]
Bombers_Frequent = [SB2C_HellDiver,J5N,AD1_SkyRaider,D4Y2A]#可选择仅使用常用轰炸机：天袭者，天雷，彗星一二甲，sb2c

#鱼雷机区
C6N1 = Aircraft('彩云','Torpedo',45,10.6013,2*362,2*427,80,110,130,100,1,0,0,0,0,0,0,0)#试作型彩云（舰攻型）
Ju_87 = Aircraft('Ju-87','Torpedo',45,11.1732,3*254,3*300,80,110,130,100,1,0,0,0,0,0,0,0)#Ju-87 D-4
B7A1 = Aircraft('流星','Torpedo',45,11.3727,3*260,3*307,80,110,130,100,1,0,0,0,0,0,0,0)#流星
VIT_2_G = Aircraft('VIT2改','Torpedo',45,11.5989,4*200,4*236,80,110,130,100,1,0,0,0,0,0,0,0)#试作型VIT-2（模式调整）

Torpedoes = [C6N1,Ju_87,B7A1,VIT_2_G]

Aircrafts = Fighters + Bombers + Torpedoes

#设备区
Catapult = Facility('金液压',100,118,0,0)#液压弹射装置
Beacon = Facility('信标',60,65,-4,0)#归航信标
Maintenance = Facility('整备',60,65,4,4)#航空整备小组
Facilities = [Catapult,Beacon,Maintenance]







