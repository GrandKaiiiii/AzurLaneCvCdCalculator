from WarshipData import *
from EquipmentData import *

# 模拟输入区
team = [Implacable, Shinano, Amagi]  # 定身辅位于首位
favorabilities = [200,200,200]  # 三船好感度
# if YorkTown2 in team:core = YorkTown2
if Shinano in team:core = Shinano
if August in team:freeze = August
if Implacable in team:freeze = Implacable
# if Enterprise in team:maincarrier = Enterprise
if Hakuryu in team:maincarrier = Hakuryu
if Amagi in team:maincarrier = Amagi
favorabilities = [favorabilities[team.index(freeze)],favorabilities[team.index(core)],favorabilities[team.index(maincarrier)]]
team = [freeze,core,maincarrier]  # 将输入的舰船和好感度按此顺序重整
tech_atk = 69
tech_acc = 23
tech_load = 42
mode = 'monthly'
defence_type = 'heavy'  # 敌方护甲
cd_min_limit = 20  # 手动设置空袭cd上下限，单位s
cd_max_limit = 21
Independence_buff = True  # 空域辅助4%装填航空加成
Cat_percentage_buff = True  # 涉及指挥喵4.041%航空加成及天赋生效
Cat_extra_percentage_buff = True  # 是否将毗沙丸置于参谋位触发技能Lv1效果，1.288%航空/装填加成
ijn_commander = 0  # 指挥猫重樱指挥官的等级，可填入0-3的整数
N_valid = True  # 选择是否多展示几个伤害排名前几的方案的开关
N = 10  # 选择N的数量（若上面那行选择为False，则此项不生效）
# 指挥猫配置前四位：火 ACE 林 既定，数据类型为布尔，后三位：空中杀手 格纳库之主 苍穹猎手，数据类型为0-3之间的整数
cat1 = [True, True, False, True, 3, 0, 3]
cat2 = [True, True, False, False, 3, 0, 3]
auto_enemy_data = True  # 是否使用预设敌人数据
enemy = [75, 50]  # 手动填入敌方机动 幸运数据
if auto_enemy_data:  #如果上面auto_enemy_data选了True，就会在这里覆盖掉
    if mode == 'monthly':
        if defence_type == 'light': enemy = [95, 45]
        if defence_type == 'middle': enemy = [90, 45]
        if defence_type == 'heavy': enemy = [74, 45]
    if mode == 'META':
        if defence_type == 'light': enemy = [75, 50]
        if defence_type == 'middle': enemy = [75, 50]
        if defence_type == 'heavy': enemy = [75, 50]
enemy_mobility, enemy_fortune = enemy
August_targeted_enabled = False  # 用于配置奥古斯特对轻巡/重巡增伤，月困可自动适配，META需手动调整
Frequent_only = True  # 用于配置是否仅使用常用飞机
Equipment_Stock_Limit = dict()  # 用于配置某类飞机使用的上限个数
Equipment_Stock_Limit[F6F_HellCat_HVAR] = 4  # 限制方案使用飞机个数的上限

# 计算猫天赋带来的固定值加成（空域辅助的装填加成与猫的加成环境相同且乘区相同，故合并在此）
# 未在此部分计算的指挥猫系列加成：重樱指挥官加日航航空，侵掠如火加增伤乘区
cat_atk = 0  # 固定值加成（4项）
cat_load = 0
cat_acc = 0
cat_luck = 0
cat_atk_pre_percentage = 0  # 百分比加成（靠前的乘区，来源为指挥猫能力值转化来的百分比加成，注意使用的数据并非百分数而是纯小数，计算时不需要除以100）
cat_atk_final_percentage = 0  # 百分比加成（2项，最终乘算乘区，来源为猫的主技能（不是天赋）加成，注意使用的数据并非百分数而是纯小数，计算时不需要除以100）
cat_load_final_percentage = 0


def buff_from_cat(ace: bool, Lin: bool, determination: bool, pure_atk, pure_load,
                  both_atk_load):  # 这一步只算ace林既定苍穹猎手空中杀手格纳库等作用于全体且为固定值的加成
    global cat_atk, cat_load, cat_acc, cat_luck
    if ace:
        cat_atk += 15
        cat_load += 8
    if Lin:
        cat_acc += 3
    if determination:
        cat_luck -= 3
        cat_atk += 10
    if 0 <= pure_load <= 3:
        cat_load += 2 * pure_load
    if 0 <= pure_atk <= 3:
        if pure_atk == 1:
            cat_atk += 10
        if pure_atk == 2:
            cat_atk += 14
        if pure_atk == 3:
            cat_atk += 20
    if 0 <= both_atk_load <= 3:
        cat_load += 2 * both_atk_load
        if both_atk_load == 1:
            cat_atk += 10
        if both_atk_load == 2:
            cat_atk += 14
        if both_atk_load == 3:
            cat_atk += 20
    return cat_atk, cat_load, cat_acc, cat_luck


if mode == 'monthly':
    c0, c1, c2, c3, c4, c5 = cat1[1:]
    c6, c7, c8, c9, c10, c11 = cat2[1:]
    buff_from_cat(c0, c1, c2, c3, c4, c5)
    buff_from_cat(c6, c7, c8, c9, c10, c11)
    cat_atk_pre_percentage += 0.04041
    if Independence_buff: cat_load_final_percentage += 0.04
    if Cat_extra_percentage_buff:
        cat_load_final_percentage += 0.01288
        cat_atk_final_percentage += 0.01288


# 指定船和装备的cd计算器
def cd_calculator(ship: Warship, load, equip1: Aircraft, equip2: Aircraft, equip3: Aircraft, equip4: Facility,
                  equip5: Facility):
    cd1 = equip1.cd * ((200 / (load + 100)) ** 0.5)
    cd2 = equip2.cd * ((200 / (load + 100)) ** 0.5)
    cd3 = equip3.cd * ((200 / (load + 100)) ** 0.5)
    atk_cd = 2.2 * (ship.count_arm1 * cd1 + ship.count_arm2 * cd2 + ship.count_arm3 * cd3) / (
                ship.count_arm1 + ship.count_arm2 + ship.count_arm3)
    real_cd = atk_cd * (0.96 if equip4 == Beacon or equip5 == Beacon else 1) * (
        1.04 if equip4 == Maintenance or equip5 == Maintenance else 1)
    return real_cd


# 飞机伤害计算器（依据局内航空值计算，只算了理论伤害（包含因航弹因散布等原因导致的命中率），未计算命中属性引起的命中率，暴击率，技能增伤等）
def aircraft_norm_dgm_calculator(eff, count, equip: Aircraft, upgrade: bool, atk,
                                 defence):  # 参数：装备槽位的效率 武器数 装备 强化与否 航空值 敌方护甲种类
    main_defence_rate = co_defence_rate = 0
    if defence == 'light':
        main_defence_rate = equip.main_light
        co_defence_rate = equip.co_light
    if defence == 'middle':
        main_defence_rate = equip.main_mid
        co_defence_rate = equip.co_mid
    if defence == 'heavy':
        main_defence_rate = equip.main_heavy
        co_defence_rate = equip.co_heavy
    main_damage = (100 + atk * equip.main_eff) / 100 * (
        equip.main_dmg_u if upgrade else equip.main_dmg_n) * equip.main_acc * main_defence_rate * eff * count
    if equip.co_dmg_n != 0:
        co_damage = (100 + atk * equip.co_eff) / 100 * (
            equip.co_dmg_u if upgrade else equip.co_dmg_n) * equip.co_acc * co_defence_rate * eff * count
        main_damage += co_damage
    return main_damage


# 信浓cd和伤害计算器
def shinano_calculator(cd_only:bool, favorability, equip1, lv1, equip2, lv2, equip3, lv3, equip4, lv4, equip5, lv5):
    # 船坞白值
    init_atk = Shinano.atk_100 if favorability == 100 else Shinano.atk_200
    init_load = Shinano.load_100 if favorability == 100 else Shinano.load_200
    init_acc = Shinano.accurate_100 if favorability == 100 else Shinano.accurate_200
    init_fortune = Shinano.fortune_100 if favorability == 100 else Shinano.fortune_200
    # 进图白值
    ijn_atk = 0
    if mode == 'monthly' and ijn_commander != 0:  # 毗沙丸重樱指挥官天赋结算
        if ijn_commander == 1: ijn_atk = 6
        if ijn_commander == 2: ijn_atk = 8
        if ijn_commander == 3: ijn_atk = 12
    real_atk = init_atk * (1 + cat_atk_pre_percentage) + tech_atk + equip1.atk + equip2.atk + equip3.atk + (
        equip4.atk_u if lv4 else equip4.atk_n) + (equip5.atk_u if lv5 else equip5.atk_n) + cat_atk + ijn_atk
    real_load = init_load + tech_load + cat_load
    real_acc = init_acc + tech_acc + cat_acc
    real_fortune = init_fortune + cat_luck
    # 结算各种船技能加成（猫的大技能加属性位于此乘区）
    final_atk = (1.3 + cat_atk_final_percentage) * real_atk
    final_acc = 1.15 * real_acc
    final_load = (1 + cat_load_final_percentage) * real_load
    cd_shinano = cd_calculator(Shinano, final_load, equip1, equip2, equip3, equip4, equip5)
    if cd_only:return cd_shinano
    if Independence_buff:
        final_atk += 0.04 * real_atk  # 装填buff已归入指挥猫buff类，不可重复计算
    final_fortune = real_fortune
    init_damage1 = aircraft_norm_dgm_calculator(Shinano.eff_arm1, Shinano.count_arm1, equip1, lv1, final_atk,
                                                defence_type) * (
                       1.15 if Amagi in team and equip1.type == 'Torpedo' else 1)  # 天城对航空鱼雷加伤15%
    init_damage2 = aircraft_norm_dgm_calculator(Shinano.eff_arm2, Shinano.count_arm2, equip2, lv2, final_atk,
                                                defence_type) * (
                       1.15 if Amagi in team and equip2.type == 'Torpedo' else 1)
    init_damage3 = aircraft_norm_dgm_calculator(Shinano.eff_arm3, Shinano.count_arm3, equip3, lv3, final_atk,
                                                defence_type) * (
                       1.15 if Amagi in team and equip3.type == 'Torpedo' else 1)
    accuracy = 0.1 + final_acc / (final_acc + enemy_mobility + 2) + (
                final_fortune - enemy_fortune + 125 - (130 if mode == 'monthly' else 126)) / 1000  # 命中率公式
    real_accuracy = max(0.1, min(1, accuracy))
    critical = 0.05 + final_acc / (final_acc + enemy_mobility + 2000) + (
                final_fortune - enemy_fortune + 125 - (130 if mode == 'monthly' else 126)) / 5000  # 暴击率公式
    init_total_damage = (init_damage1 + init_damage2 + init_damage3) * real_accuracy * (
                1 + critical * 0.5)  # 计算命中率和暴击率的总伤
    siren_rate = 1  # 计算塞壬增伤系数
    siren_rate += lv1 * (0.01 if equip1.atk == 25 else 0.03)  # 判断是否紫飞机，若是，塞壬增伤1%，否则3%，由控制强化与否的lv决定是否累计
    siren_rate += lv2 * (0.01 if equip2.atk == 25 else 0.03)
    siren_rate += lv3 * (0.01 if equip3.atk == 25 else 0.03)
    siren_rate += lv4 * (0.03 if equip4 == Catapult else 0.01)  # 判断是否是金液压，若是，塞壬增伤3%，否则1%
    siren_rate += lv5 * (0.03 if equip5 == Catapult else 0.01)
    siren_rate = min(1.2, siren_rate)  # 高于1.2的修正回1.2
    final_total_damage = init_total_damage * siren_rate * (
        1.04 if equip4 == Maintenance or equip5 == Maintenance else 1)
    return cd_shinano, final_total_damage


# 天城cd和伤害计算器
def amagi_calculator(cd_only:bool, favorability, equip1, lv1, equip2, lv2, equip3, lv3, equip4, lv4, equip5, lv5):
    # 船坞白值
    init_atk = Amagi.atk_100 if favorability == 100 else Amagi.atk_200
    init_load = Amagi.load_100 if favorability == 100 else Amagi.load_200
    init_acc = Amagi.accurate_100 if favorability == 100 else Amagi.accurate_200
    init_fortune = Amagi.fortune_100 if favorability == 100 else Amagi.fortune_200
    # 进图白值
    ijn_atk = 0
    if mode == 'monthly' and ijn_commander != 0:  # 毗沙丸重樱指挥官天赋结算
        if ijn_commander == 1: ijn_atk = 6
        if ijn_commander == 2: ijn_atk = 8
        if ijn_commander == 3: ijn_atk = 12
    real_atk = init_atk * (1 + cat_atk_pre_percentage) + tech_atk + equip1.atk + equip2.atk + equip3.atk + (
        equip4.atk_u if lv4 else equip4.atk_n) + (equip5.atk_u if lv5 else equip5.atk_n) + cat_atk + ijn_atk
    real_load = init_load + tech_load + cat_load
    real_acc = init_acc + tech_acc + cat_acc
    real_fortune = init_fortune + cat_luck
    # 结算各种船技能加成（猫的大技能加属性位于此乘区）
    final_atk = (1.15 + cat_atk_final_percentage + (0.15 if Shinano in team else 0)) * real_atk
    final_acc = (1 + (0.15 if Shinano in team else 0)) * real_acc
    final_load = (1 + cat_load_final_percentage) * real_load
    cd_amagi = cd_calculator(Amagi, final_load, equip1, equip2, equip3, equip4, equip5)
    if cd_only:return cd_amagi
    if Independence_buff:
        final_atk += 0.04 * real_atk  # 装填buff已归入指挥猫buff类，不可重复计算
    final_fortune = real_fortune
    init_damage1 = aircraft_norm_dgm_calculator(Amagi.eff_arm1, Amagi.count_arm1, equip1, lv1, final_atk,
                                                defence_type) * (
                       1.15 if equip1.type == 'Torpedo' else 1)  # 天城对航空鱼雷加伤15%
    init_damage2 = aircraft_norm_dgm_calculator(Amagi.eff_arm2, Amagi.count_arm2, equip2, lv2, final_atk,
                                                defence_type) * (1.15 if equip2.type == 'Torpedo' else 1)
    init_damage3 = aircraft_norm_dgm_calculator(Amagi.eff_arm3, Amagi.count_arm3, equip3, lv3, final_atk,
                                                defence_type) * (1.15 if equip3.type == 'Torpedo' else 1)
    accuracy = 0.1 + final_acc / (final_acc + enemy_mobility + 2) + (
            final_fortune - enemy_fortune + 125 - (130 if mode == 'monthly' else 126)) / 1000  # 命中率公式
    real_accuracy = max(0.1, min(1, accuracy))
    critical = 0.05 + final_acc / (final_acc + enemy_mobility + 2000) + (
            final_fortune - enemy_fortune + 125 - (130 if mode == 'monthly' else 126)) / 5000  # 暴击率公式
    init_total_damage = (init_damage1 + init_damage2 + init_damage3) * real_accuracy * (
            1 + critical * 0.5)  # 计算命中率和暴击率的总伤
    siren_rate = 1  # 计算塞壬增伤系数
    siren_rate += lv1 * (0.01 if equip1.atk == 25 else 0.03)  # 判断是否紫飞机，若是，塞壬增伤1%，否则3%，由控制强化与否的lv决定是否累计
    siren_rate += lv2 * (0.01 if equip2.atk == 25 else 0.03)
    siren_rate += lv3 * (0.01 if equip3.atk == 25 else 0.03)
    siren_rate += lv4 * (0.03 if equip4 == Catapult else 0.01)  # 判断是否是金液压，若是，塞壬增伤3%，否则1%
    siren_rate += lv5 * (0.03 if equip5 == Catapult else 0.01)
    siren_rate = min(1.2, siren_rate)  # 高于1.2的修正回1.2
    final_total_damage = init_total_damage * siren_rate * 1.18 * (
        1.04 if equip4 == Maintenance or equip5 == Maintenance else 1)
    return cd_amagi, final_total_damage


# 怨仇cd和伤害计算器
def implacable_calculator(cd_only:bool, favorability, equip1, lv1, equip2, lv2, equip3, lv3, equip4, lv4, equip5, lv5):
    # 船坞白值
    init_atk = Implacable.atk_100 if favorability == 100 else Implacable.atk_200
    init_load = Implacable.load_100 if favorability == 100 else Implacable.load_200
    init_acc = Implacable.accurate_100 if favorability == 100 else Implacable.accurate_200
    init_fortune = Implacable.fortune_100 if favorability == 100 else Implacable.fortune_200
    # 进图白值
    real_atk = init_atk * (1 + cat_atk_pre_percentage) + tech_atk + equip1.atk + equip2.atk + equip3.atk + (
        equip4.atk_u if lv4 else equip4.atk_n) + (equip5.atk_u if lv5 else equip5.atk_n) + cat_atk
    real_load = init_load + tech_load + cat_load
    real_acc = init_acc + tech_acc + cat_acc
    real_fortune = init_fortune + cat_luck
    # 结算各种船技能加成
    final_atk = (1.1 + cat_atk_final_percentage) * real_atk
    final_acc = 1.1 * real_acc
    final_load = (1 + cat_load_final_percentage + (0.1 if equip2.type == 'Bomber' else 0)) * real_load
    cd_implacable = cd_calculator(Implacable, final_load, equip1, equip2, equip3, equip4, equip5)
    if cd_only: return cd_implacable
    if Independence_buff:
        final_atk += 0.04 * real_atk  # 装填buff已归入指挥猫buff类，不可重复计算
    final_fortune = real_fortune
    init_damage1 = aircraft_norm_dgm_calculator(Implacable.eff_arm1, Implacable.count_arm1, equip1, lv1, final_atk,
                                                defence_type)
    init_damage2 = aircraft_norm_dgm_calculator(Implacable.eff_arm2, Implacable.count_arm2, equip2, lv2, final_atk,
                                                defence_type)
    init_damage3 = aircraft_norm_dgm_calculator(Implacable.eff_arm3, Implacable.count_arm3, equip3, lv3, final_atk,
                                                defence_type)
    accuracy = 0.1 + final_acc / (final_acc + enemy_mobility + 2) + (
            final_fortune - enemy_fortune + 125 - (130 if mode == 'monthly' else 126)) / 1000  # 命中率公式
    real_accuracy = max(0.1, min(1, accuracy))
    critical = 0.05 + final_acc / (final_acc + enemy_mobility + 2000) + (
            final_fortune - enemy_fortune + 125 - (130 if mode == 'monthly' else 126)) / 5000  # 暴击率公式
    init_total_damage = (init_damage1 + init_damage2 + init_damage3) * real_accuracy * (
            1 + critical * 0.5)  # 计算命中率和暴击率的总伤
    siren_rate = 1  # 计算塞壬增伤系数
    siren_rate += lv1 * (0.01 if equip1.atk == 25 else 0.03)  # 判断是否紫飞机，若是，塞壬增伤1%，否则3%，由控制强化与否的lv决定是否累计
    siren_rate += lv2 * (0.01 if equip2.atk == 25 else 0.03)
    siren_rate += lv3 * (0.01 if equip3.atk == 25 else 0.03)
    siren_rate += lv4 * (0.03 if equip4 == Catapult else 0.01)  # 判断是否是金液压，若是，塞壬增伤3%，否则1%
    siren_rate += lv5 * (0.03 if equip5 == Catapult else 0.01)
    siren_rate = min(1.2, siren_rate)  # 高于1.2的修正回1.2
    final_total_damage = init_total_damage * siren_rate * (
        1.04 if equip4 == Maintenance or equip5 == Maintenance else 1)
    print(init_damage1,init_damage2,init_damage3,real_accuracy,critical)
    return cd_implacable, final_total_damage


# 白龙cd和伤害计算器
def hakuryu_calculator(cd_only:bool, favorability, equip1, lv1, equip2, lv2, equip3, lv3, equip4, lv4, equip5, lv5):
    # 船坞白值
    init_atk = Hakuryu.atk_100 if favorability == 100 else Hakuryu.atk_200
    init_load = Hakuryu.load_100 if favorability == 100 else Hakuryu.load_200
    init_acc = Hakuryu.accurate_100 if favorability == 100 else Hakuryu.accurate_200
    init_fortune = Hakuryu.fortune_100 if favorability == 100 else Hakuryu.fortune_200
    # 进图白值
    ijn_atk = 0
    if mode == 'monthly' and ijn_commander != 0:  # 毗沙丸重樱指挥官天赋结算
        if ijn_commander == 1: ijn_atk = 6
        if ijn_commander == 2: ijn_atk = 8
        if ijn_commander == 3: ijn_atk = 12
    real_atk = init_atk * (1 + cat_atk_pre_percentage) + tech_atk + equip1.atk + equip2.atk + equip3.atk + (
        equip4.atk_u if lv4 else equip4.atk_n) + (equip5.atk_u if lv5 else equip5.atk_n) + cat_atk + ijn_atk
    real_load = init_load + tech_load + cat_load
    real_acc = init_acc + tech_acc + cat_acc
    real_fortune = init_fortune + cat_luck
    # 结算各种船技能加成（猫的大技能加属性位于此乘区）
    final_atk = (1.2 + cat_atk_final_percentage + (0.15 if Shinano in team else 0)) * real_atk
    final_acc = (1.2 + (0.15 if Shinano in team else 0)) * real_acc
    final_load = (1 + cat_load_final_percentage) * real_load
    cd_hakuryu = cd_calculator(Hakuryu, final_load, equip1, equip2, equip3, equip4, equip5)
    if cd_only: return cd_hakuryu
    if Independence_buff:
        final_atk += 0.04 * real_atk  # 装填buff已归入指挥猫buff类，不可重复计算
    final_fortune = real_fortune
    init_damage1 = aircraft_norm_dgm_calculator(Hakuryu.eff_arm1 + 0.1, Hakuryu.count_arm1, equip1, lv1, final_atk,
                                                defence_type) * (
                       1.15 if Amagi in team and equip1.type == 'Torpedo' else 1)  # 天城对航空鱼雷加伤15%
    init_damage2 = aircraft_norm_dgm_calculator(Hakuryu.eff_arm2 + 0.1, Hakuryu.count_arm2, equip2, lv2, final_atk,
                                                defence_type) * (
                       1.15 if Amagi in team and equip2.type == 'Torpedo' else 1)
    init_damage3 = aircraft_norm_dgm_calculator(Hakuryu.eff_arm3 + 0.1, Hakuryu.count_arm3, equip3, lv3, final_atk,
                                                defence_type) * (
                       1.15 if Amagi in team and equip3.type == 'Torpedo' else 1)
    accuracy = 0.1 + final_acc / (final_acc + enemy_mobility + 2) + (
            final_fortune - enemy_fortune + 125 - (130 if mode == 'monthly' else 126)) / 1000  # 命中率公式
    real_accuracy = max(0.1, min(1, accuracy))
    critical = 0.05 + final_acc / (final_acc + enemy_mobility + 2000) + (
            final_fortune - enemy_fortune + 125 - (130 if mode == 'monthly' else 126)) / 5000  # 暴击率公式
    init_total_damage = (init_damage1 + init_damage2 + init_damage3) * real_accuracy * (
            1 + critical * 0.5)  # 计算命中率和暴击率的总伤
    siren_rate = 1.15  # 计算塞壬增伤系数
    siren_rate += lv1 * (0.01 if equip1.atk == 25 else 0.03)  # 判断是否紫飞机，若是，塞壬增伤1%，否则3%，由控制强化与否的lv决定是否累计
    siren_rate += lv2 * (0.01 if equip2.atk == 25 else 0.03)
    siren_rate += lv3 * (0.01 if equip3.atk == 25 else 0.03)
    siren_rate += lv4 * (0.03 if equip4 == Catapult else 0.01)  # 判断是否是金液压，若是，塞壬增伤3%，否则1%
    siren_rate += lv5 * (0.03 if equip5 == Catapult else 0.01)
    siren_rate = min(1.2, siren_rate)  # 高于1.2的修正回1.2
    final_total_damage = init_total_damage * siren_rate * (
        1.04 if equip4 == Maintenance or equip5 == Maintenance else 1)
    return cd_hakuryu, final_total_damage


# 奥古斯特cd和伤害计算器
def august_calculator(cd_only:bool, favorability, equip1, lv1, equip2, lv2, equip3, lv3, equip4, lv4, equip5, lv5):
    # 船坞白值
    init_atk = August.atk_100 if favorability == 100 else August.atk_200
    init_load = August.load_100 if favorability == 100 else August.load_200
    init_acc = August.accurate_100 if favorability == 100 else August.accurate_200
    init_fortune = August.fortune_100 if favorability == 100 else August.fortune_200
    # 进图白值
    # 判断技能触发条件
    germany_aircraft_bool = equip1 == BF_109G or equip1 == FW190A6 or equip3 == Ju_87
    targeted_enemy_bool = (mode == 'monthly' and (
                defence_type == 'light' or defence_type == 'middle')) or August_targeted_enabled

    real_atk = init_atk * (1 + cat_atk_pre_percentage) + tech_atk + equip1.atk + equip2.atk + equip3.atk + (
        equip4.atk_u if lv4 else equip4.atk_n) + (equip5.atk_u if lv5 else equip5.atk_n) + cat_atk
    real_load = init_load + tech_load + cat_load
    real_acc = init_acc + tech_acc + cat_acc
    real_fortune = init_fortune + cat_luck
    # 结算各种船技能加成
    final_atk = (1 + cat_atk_final_percentage + (0.12 if germany_aircraft_bool else 0)) * real_atk
    final_acc = real_acc
    final_load = (1 + cat_load_final_percentage + (0.12 if germany_aircraft_bool else 0)) * real_load
    cd_august = cd_calculator(August, final_load, equip1, equip2, equip3, equip4, equip5)
    if cd_only: return cd_august
    if Independence_buff:
        final_atk += 0.04 * real_atk  # 装填buff已归入指挥猫buff类，不可重复计算
    final_fortune = real_fortune
    init_damage1 = aircraft_norm_dgm_calculator(August.eff_arm1 + (0.1 if germany_aircraft_bool else 0),
                                                August.count_arm1, equip1, lv1, final_atk, defence_type)
    init_damage2 = aircraft_norm_dgm_calculator(August.eff_arm2, August.count_arm2, equip2, lv2, final_atk,
                                                defence_type)
    init_damage3 = aircraft_norm_dgm_calculator(August.eff_arm3, August.count_arm3, equip3, lv3, final_atk,
                                                defence_type)
    accuracy = 0.1 + final_acc / (final_acc + enemy_mobility + 2) + (
            final_fortune - enemy_fortune + 125 - (130 if mode == 'monthly' else 126)) / 1000  # 命中率公式
    real_accuracy = max(0.1, min(1, accuracy))
    critical = 0.05 + final_acc / (final_acc + enemy_mobility + 2000) + (
            final_fortune - enemy_fortune + 125 - (130 if mode == 'monthly' else 126)) / 5000  # 暴击率公式
    init_total_damage = (init_damage1 + init_damage2 + init_damage3) * real_accuracy * (
            1 + critical * 0.5)  # 计算命中率和暴击率的总伤
    siren_rate = 1.15  # 计算塞壬增伤系数
    siren_rate += lv1 * (0.01 if equip1.atk == 25 else 0.03)  # 判断是否紫飞机，若是，塞壬增伤1%，否则3%，由控制强化与否的lv决定是否累计
    siren_rate += lv2 * (0.01 if equip2.atk == 25 else 0.03)
    siren_rate += lv3 * (0.01 if equip3.atk == 25 else 0.03)
    siren_rate += lv4 * (0.03 if equip4 == Catapult else 0.01)  # 判断是否是金液压，若是，塞壬增伤3%，否则1%
    siren_rate += lv5 * (0.03 if equip5 == Catapult else 0.01)
    siren_rate = min(1.2, siren_rate)  # 高于1.2的修正回1.2
    final_total_damage = init_total_damage * siren_rate * (1.2 if targeted_enemy_bool else 1) * (
        1.04 if equip4 == Maintenance or equip5 == Maintenance else 1)
    return cd_august, final_total_damage


# print(shinano_calculator(False, 200, Ju_87, 1, J5N, 1, Ju_87, 1, Catapult, 1, Catapult, 1))
# print(amagi_calculator(False, 200, J5N, 1, Ju_87, 1, B7A1, 1, Catapult, 1, Catapult, 1))
print(implacable_calculator(0, 200, La_9, 1, La_9, 1, B7A1, 1, Catapult, 1, Catapult, 1))
print(implacable_calculator(0, 200, La_9, 1, VIT_2_G, 1, B7A1, 1, Catapult, 1, Catapult, 1))
# print(hakuryu_calculator(False, 200, Ju_87, 1, J5N, 1, Ju_87, 1, Catapult, 1, Catapult, 1))
# print(august_calculator(False, 200, FW190A6, 1, J5N, 1, Ju_87, 1, Catapult, 1, Catapult, 1))
