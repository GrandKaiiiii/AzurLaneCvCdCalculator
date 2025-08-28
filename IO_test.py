from WarshipData import *
from EquipmentData import *
import data
import heapq

freeze = data.freeze
core = data.core
maincarrier = data.maincarrier
favorabilities = data.favorabilities
favorabilities_freeze = data.favorabilities_freeze
favorabilities_core = data.favorabilities_core
favorabilities_maincarrier = data.favorabilities_maincarrier
team = data.team
tech_atk = data.tech_atk
tech_acc = data.tech_acc
tech_load = data.tech_load
mode = data.mode
defence_type = data.defence_type
cd_min_limit = data.cd_min_limit
cd_max_limit = data.cd_max_limit
Independence_buff = data.independence_buff
Cat_percentage_buff = data.cat_percentage_buff
Cat_extra_percentage_buff = data.cat_extra_percentage_buff
ijn_commander = data.ijn_commander
N_valid = data.n_valid
N = data.n
cat1 = data.cat1
cat2 = data.cat2
auto_enemy_data = data.auto_enemy_data
# --- 修改部分 1 结束: 直接使用 data.py 中处理好的 enemy_mobility 和 enemy_fortune ---
enemy_mobility = data.enemy_mobility
enemy_fortune = data.enemy_fortune
August_targeted_enabled = data.august_targeted_enabled
Frequent_only = data.frequent_only
Equipment_Stock_Limit = data.equipment_stock_limit  # 注意变量名大小写可能需要调整


def get_result():
    # 计算猫天赋带来的固定值加成（空域辅助的装填加成与猫的加成环境相同且乘区相同，故合并在此）
    # 未在此部分计算的指挥猫系列加成：重樱指挥官加日航航空，侵掠如火加增伤乘区
    global cat_atk, cat_load, cat_acc, cat_luck, cat_atk_pre_percentage, cat_atk_final_percentage, cat_load_final_percentage
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
    def shinano_calculator(cd_only: bool, favorability, equip1, lv1, equip2, lv2, equip3, lv3, equip4, lv4, equip5,
                           lv5):
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
        if cd_only: return cd_shinano
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
        final_total_damage = init_total_damage * siren_rate * (1 + (0.04 if equip4 == Maintenance or equip5 == Maintenance else 0) + (0.03 if cat1[0] else 0) + (0.03 if cat2[0] else 0))
        return cd_shinano, final_total_damage

    # 天城cd和伤害计算器
    def amagi_calculator(cd_only: bool, favorability, equip1, lv1, equip2, lv2, equip3, lv3, equip4, lv4, equip5, lv5):
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
        if cd_only: return cd_amagi
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
        final_total_damage = init_total_damage * siren_rate * 1.18 * (1 + (0.04 if equip4 == Maintenance or equip5 == Maintenance else 0) + (0.03 if cat1[0] else 0) + (0.03 if cat2[0] else 0))
        return cd_amagi, final_total_damage

    # 怨仇cd和伤害计算器
    def implacable_calculator(cd_only: bool, favorability, equip1, lv1, equip2, lv2, equip3, lv3, equip4, lv4, equip5,
                              lv5):
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
        final_total_damage = init_total_damage * siren_rate * (1 + (0.04 if equip4 == Maintenance or equip5 == Maintenance else 0) + (0.03 if cat1[0] else 0) + (0.03 if cat2[0] else 0))
        return cd_implacable, final_total_damage

    # 白龙cd和伤害计算器
    def hakuryu_calculator(cd_only: bool, favorability, equip1, lv1, equip2, lv2, equip3, lv3, equip4, lv4, equip5,
                           lv5):
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
        final_total_damage = init_total_damage * siren_rate * (1 + (0.04 if equip4 == Maintenance or equip5 == Maintenance else 0) + (0.03 if cat1[0] else 0) + (0.03 if cat2[0] else 0))
        return cd_hakuryu, final_total_damage

    # 奥古斯特cd和伤害计算器
    def august_calculator(cd_only: bool, favorability, equip1, lv1, equip2, lv2, equip3, lv3, equip4, lv4, equip5, lv5):
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
        final_total_damage = init_total_damage * siren_rate * (1.2 if targeted_enemy_bool else 1) * (1 + (0.04 if equip4 == Maintenance or equip5 == Maintenance else 0) + (0.03 if cat1[0] else 0) + (0.03 if cat2[0] else 0))
        return cd_august, final_total_damage

    # 约克城IIcd和伤害计算器
    def yorktown2_calculator(cd_only: bool, favorability, equip1, lv1, equip2, lv2, equip3, lv3, equip4, lv4, equip5,
                             lv5):
        # 船坞白值
        init_atk = YorkTown2.atk_100 if favorability == 100 else YorkTown2.atk_200
        init_load = YorkTown2.load_100 if favorability == 100 else YorkTown2.load_200
        init_acc = YorkTown2.accurate_100 if favorability == 100 else YorkTown2.accurate_200
        init_fortune = YorkTown2.fortune_100 if favorability == 100 else YorkTown2.fortune_200
        # 进图白值
        real_atk = init_atk * (1 + cat_atk_pre_percentage) + tech_atk + equip1.atk + equip2.atk + equip3.atk + (
            equip4.atk_u if lv4 else equip4.atk_n) + (equip5.atk_u if lv5 else equip5.atk_n) + cat_atk
        real_load = init_load + tech_load + cat_load
        real_acc = init_acc + tech_acc + cat_acc
        real_fortune = init_fortune + cat_luck
        # 结算各种船技能加成（猫的大技能加属性位于此乘区）
        final_atk = (1.15 + cat_atk_final_percentage) * real_atk
        final_acc = 1.15 * real_acc
        final_load = (1 + cat_load_final_percentage) * real_load
        cd_yorktown = cd_calculator(YorkTown2, final_load, equip1, equip2, equip3, equip4, equip5)
        if cd_only: return cd_yorktown
        if Independence_buff:
            final_atk += 0.04 * real_atk  # 装填buff已归入指挥猫buff类，不可重复计算
        final_fortune = real_fortune
        init_damage1 = aircraft_norm_dgm_calculator(YorkTown2.eff_arm1, YorkTown2.count_arm1, equip1, lv1, final_atk,
                                                    defence_type)
        init_damage2 = aircraft_norm_dgm_calculator(YorkTown2.eff_arm2, YorkTown2.count_arm2, equip2, lv2, final_atk,
                                                    defence_type)
        init_damage3 = aircraft_norm_dgm_calculator(YorkTown2.eff_arm3, YorkTown2.count_arm3, equip3, lv3, final_atk,
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
                    1 + 0.1 + (0.04 if equip4 == Maintenance or equip5 == Maintenance else 0) + (
                0.03 if cat1[0] else 0) + (0.03 if cat2[0] else 0))

        return cd_yorktown, final_total_damage

    # 企业cd和伤害计算器
    def enterprise_calculator(cd_only: bool, favorability, equip1, lv1, equip2, lv2, equip3, lv3, equip4, lv4, equip5,
                           lv5):
        # 船坞白值
        init_atk = Enterprise.atk_100 if favorability == 100 else Enterprise.atk_200
        init_load = Enterprise.load_100 if favorability == 100 else Enterprise.load_200
        init_acc = Enterprise.accurate_100 if favorability == 100 else Enterprise.accurate_200
        init_fortune = Enterprise.fortune_100 if favorability == 100 else Enterprise.fortune_200
        # 进图白值
        real_atk = init_atk * (1 + cat_atk_pre_percentage) + tech_atk + equip1.atk + equip2.atk + equip3.atk + (
            equip4.atk_u if lv4 else equip4.atk_n) + (equip5.atk_u if lv5 else equip5.atk_n) + cat_atk
        real_load = init_load + tech_load + cat_load
        real_acc = init_acc + tech_acc + cat_acc
        real_fortune = init_fortune + cat_luck
        # 结算各种船技能加成（猫的大技能加属性位于此乘区）
        final_atk = (1 + cat_atk_final_percentage) * real_atk
        final_acc = real_acc
        final_load = (1 + cat_load_final_percentage) * real_load
        cd_enterprise = cd_calculator(Enterprise, final_load, equip1, equip2, equip3, equip4, equip5)
        if cd_only: return cd_enterprise
        if Independence_buff:
            final_atk += 0.04 * real_atk  # 装填buff已归入指挥猫buff类，不可重复计算
        final_fortune = real_fortune
        init_damage1 = aircraft_norm_dgm_calculator(Enterprise.eff_arm1, Enterprise.count_arm1, equip1, lv1, final_atk,
                                                    defence_type)
        init_damage2 = aircraft_norm_dgm_calculator(Enterprise.eff_arm2, Enterprise.count_arm2, equip2, lv2, final_atk,
                                                    defence_type)
        init_damage3 = aircraft_norm_dgm_calculator(Enterprise.eff_arm3, Enterprise.count_arm3, equip3, lv3, final_atk,
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
        final_total_damage = init_total_damage * siren_rate * (1 + (0.1 if YorkTown2 in team else 0) + 0.7 + (0.04 if equip4 == Maintenance or equip5 == Maintenance else 0) + (0.03 if cat1[0] else 0) + (0.03 if cat2[0] else 0))
        return cd_enterprise, final_total_damage

    # 纳希莫夫cd和伤害计算器
    def nakhimov_calculator(cd_only: bool, favorability, equip1, lv1, equip2, lv2, equip3, lv3, equip4, lv4, equip5,
                           lv5):
        # 船坞白值
        init_atk = Nakhimov.atk_100 if favorability == 100 else Nakhimov.atk_200
        init_load = Nakhimov.load_100 if favorability == 100 else Nakhimov.load_200
        init_acc = Nakhimov.accurate_100 if favorability == 100 else Nakhimov.accurate_200
        init_fortune = Nakhimov.fortune_100 if favorability == 100 else Nakhimov.fortune_200
        # 进图白值
        real_atk = init_atk * (1 + cat_atk_pre_percentage) + tech_atk + equip1.atk + equip2.atk + equip3.atk + (
            equip4.atk_u if lv4 else equip4.atk_n) + (equip5.atk_u if lv5 else equip5.atk_n) + cat_atk
        real_load = init_load + tech_load + cat_load
        real_acc = init_acc + tech_acc + cat_acc
        real_fortune = init_fortune + cat_luck
        # 结算各种船技能加成（猫的大技能加属性位于此乘区）
        final_atk = (1.15 + cat_atk_final_percentage) * real_atk
        final_acc = 1.15 * real_acc
        final_load = (1 + cat_load_final_percentage) * real_load
        cd_nakhimov = cd_calculator(Nakhimov, final_load, equip1, equip2, equip3, equip4, equip5)
        if cd_only: return cd_nakhimov
        if Independence_buff:
            final_atk += 0.04 * real_atk  # 装填buff已归入指挥猫buff类，不可重复计算
        final_fortune = real_fortune
        init_damage1 = aircraft_norm_dgm_calculator(Nakhimov.eff_arm1, Nakhimov.count_arm1, equip1, lv1, final_atk,
                                                    defence_type)
        init_damage2 = aircraft_norm_dgm_calculator(Nakhimov.eff_arm2, Nakhimov.count_arm2, equip2, lv2, final_atk,
                                                    defence_type)
        init_damage3 = aircraft_norm_dgm_calculator(Nakhimov.eff_arm3, Nakhimov.count_arm3, equip3, lv3, final_atk,
                                                    defence_type)
        accuracy = 0.1 + final_acc / (final_acc + enemy_mobility + 2) + (
                final_fortune - enemy_fortune + 125 - (130 if mode == 'monthly' else 126)) / 1000  # 命中率公式
        real_accuracy = max(0.1, min(1, accuracy))
        critical = 0.05 + final_acc / (final_acc + enemy_mobility + 2000) + (
                final_fortune - enemy_fortune + 125 - (130 if mode == 'monthly' else 126)) / 5000  # 暴击率公式
        critical += 0.2  # 纳西莫夫加20%暴击
        init_total_damage = (init_damage1 + init_damage2 + init_damage3) * real_accuracy * (
                1 + critical * (0.4 + 0.5))  # 计算命中率和暴击率的总伤 纳西莫夫加40%暴伤
        siren_rate = 1.15  # 计算塞壬增伤系数
        siren_rate += lv1 * (0.01 if equip1.atk == 25 else 0.03)  # 判断是否紫飞机，若是，塞壬增伤1%，否则3%，由控制强化与否的lv决定是否累计
        siren_rate += lv2 * (0.01 if equip2.atk == 25 else 0.03)
        siren_rate += lv3 * (0.01 if equip3.atk == 25 else 0.03)
        siren_rate += lv4 * (0.03 if equip4 == Catapult else 0.01)  # 判断是否是金液压，若是，塞壬增伤3%，否则1%
        siren_rate += lv5 * (0.03 if equip5 == Catapult else 0.01)
        siren_rate = min(1.2, siren_rate)  # 高于1.2的修正回1.2
        final_total_damage = init_total_damage * siren_rate * (1 + (0.04 if equip4 == Maintenance or equip5 == Maintenance else 0) + (0.03 if cat1[0] else 0) + (0.03 if cat2[0] else 0))
        return cd_nakhimov, final_total_damage

    class EquippedWarship:
        def __init__(self, ship, equip1, equip2, equip3, equip4, equip5):
            self.ship = ship
            self.equip1 = equip1
            self.equip2 = equip2
            self.equip3 = equip3
            self.equip4 = equip4
            self.equip5 = equip5

        def cd_calculator(self):
            if self.ship == Shinano: return shinano_calculator(True, favorabilities[team.index(self.ship)], self.equip1,
                                                               1,
                                                               self.equip2, 1, self.equip3, 1, self.equip4, 1,
                                                               self.equip5,
                                                               1)
            if self.ship == Amagi: return amagi_calculator(True, favorabilities[team.index(self.ship)], self.equip1, 1,
                                                           self.equip2,
                                                           1, self.equip3, 1, self.equip4, 1, self.equip5, 1)
            if self.ship == Implacable: return implacable_calculator(True, favorabilities[team.index(self.ship)],
                                                                     self.equip1, 1,
                                                                     self.equip2, 1, self.equip3, 1, self.equip4, 1,
                                                                     self.equip5, 1)
            if self.ship == Hakuryu: return hakuryu_calculator(True, favorabilities[team.index(self.ship)], self.equip1,
                                                               1,
                                                               self.equip2, 1, self.equip3, 1, self.equip4, 1,
                                                               self.equip5,
                                                               1)
            if self.ship == August: return august_calculator(True, favorabilities[team.index(self.ship)], self.equip1,
                                                             1,
                                                             self.equip2, 1, self.equip3, 1, self.equip4, 1,
                                                             self.equip5, 1)
            if self.ship == YorkTown2: return yorktown2_calculator(True, favorabilities[team.index(self.ship)], self.equip1, 1,
                                                                   self.equip2, 1, self.equip3, 1, self.equip4, 1,
                                                                   self.equip5, 1)
            if self.ship == Enterprise: return enterprise_calculator(True, favorabilities[team.index(self.ship)], self.equip1, 1,
                                                                     self.equip2, 1, self.equip3, 1, self.equip4, 1,
                                                                     self.equip5, 1)
            if self.ship == Nakhimov: return nakhimov_calculator(True, favorabilities[team.index(self.ship)], self.equip1, 1,
                                                                 self.equip2, 1, self.equip3, 1, self.equip4, 1,
                                                                 self.equip5, 1)

        def dmg_calculator(self):
            if self.ship == Shinano: return \
            shinano_calculator(False, favorabilities[team.index(self.ship)], self.equip1, 1,
                               self.equip2, 1, self.equip3, 1, self.equip4, 1, self.equip5,
                               1)[1]
            if self.ship == Amagi: return \
            amagi_calculator(False, favorabilities[team.index(self.ship)], self.equip1, 1, self.equip2,
                             1, self.equip3, 1, self.equip4, 1, self.equip5, 1)[1]
            if self.ship == Implacable: return \
            implacable_calculator(False, favorabilities[team.index(self.ship)], self.equip1, 1,
                                  self.equip2, 1, self.equip3, 1, self.equip4, 1,
                                  self.equip5, 1)[1]
            if self.ship == Hakuryu: return \
            hakuryu_calculator(False, favorabilities[team.index(self.ship)], self.equip1, 1,
                               self.equip2, 1, self.equip3, 1, self.equip4, 1, self.equip5,
                               1)[1]
            if self.ship == August: return \
            august_calculator(False, favorabilities[team.index(self.ship)], self.equip1, 1,
                              self.equip2, 1, self.equip3, 1, self.equip4, 1, self.equip5, 1)[1]
            if self.ship == YorkTown2: return yorktown2_calculator(False, favorabilities[team.index(self.ship)], self.equip1, 1,
                                                                   self.equip2, 1, self.equip3, 1, self.equip4, 1,
                                                                   self.equip5, 1)[1]
            if self.ship == Enterprise: return enterprise_calculator(False, favorabilities[team.index(self.ship)], self.equip1, 1,
                                                                     self.equip2, 1, self.equip3, 1, self.equip4, 1,
                                                                     self.equip5, 1)[1]
            if self.ship == Nakhimov: return nakhimov_calculator(False, favorabilities[team.index(self.ship)], self.equip1, 1,
                                                                 self.equip2, 1, self.equip3, 1, self.equip4, 1,
                                                                 self.equip5, 1)[1]

        def print_out(self):
            output_str = f'{self.ship.name}：{" ".join([self.equip1.name, self.equip2.name, self.equip3.name, self.equip4.name, self.equip5.name])}'
            return output_str

    # 生成舰载机可选列表
    def available_aircraft_list(ship: Warship, rank):
        available_type = None
        if rank == 1: available_type = ship.type_arm1
        if rank == 2: available_type = ship.type_arm2
        if rank == 3: available_type = ship.type_arm3
        available_list = []
        for key in ['Fighter', 'Bomber', 'Torpedo']:
            if key in available_type:
                if key == 'Fighter': available_list.extend(Fighters_Frequent if Frequent_only else Fighters)
                if key == 'Bomber': available_list.extend(Bombers_Frequent if Frequent_only else Bombers)
                if key == 'Torpedo': available_list.extend(Torpedoes) if freeze != August else available_list.append(
                    C6N1)
        return available_list

    # 将所有槽位的可选列表整合成一个大列表
    # 此函数同时适配怨仇定身和奥古定身
    def equipment_valid_set(team):
        member1, member2, member3 = team
        Facilities_valid_set = [[Catapult, Beacon], [Maintenance, Beacon], [Catapult, Catapult],
                                [Catapult, Maintenance]]  # 设备只有这四种有效组合，其余都为冗余/负收益，该排列cd也由短到长
        available_equipment_set = []
        available_equipment_set.extend(
            [Facilities_valid_set, available_aircraft_list(member1, 1), available_aircraft_list(member1, 2),
             available_aircraft_list(member1, 3)])
        available_equipment_set.extend(
            [Facilities_valid_set, available_aircraft_list(member2, 1), available_aircraft_list(member2, 2),
             available_aircraft_list(member2, 3)])
        available_equipment_set.extend(
            [Facilities_valid_set, available_aircraft_list(member3, 1), available_aircraft_list(member3, 2),
             available_aircraft_list(member3, 3)])
        for i in range(len(available_equipment_set)):
            if 1 <= (i % 4) <= 3:
                available_equipment_set[i] = sorted(available_equipment_set[i], key=lambda x: x.cd)
                # print([a.name for a in available_equipment_set[i]])
        return available_equipment_set

    # 对方案使用的飞机总数进行限制
    Equipment_Stock = dict()
    Equipment_Stock[AD1_SkyRaider] = 2  # 默认至多使用2架天袭者
    if defence_type == 'heavy':# 对重时ban掉对重补正仅50的的火箭弹飞机，仅保留一架允许用作调速
        Equipment_Stock[AD1_SkyRaider] = 1
        for fighter in Fighters:
            Equipment_Stock[fighter] = 1
    if defence_type == 'light':# 对轻时尽量少使用对轻补正极低的鱼雷机，但考虑到鱼雷机组为多数航母刚需，故仅保留两架用作调速
        for torpedo in Torpedoes:
            Equipment_Stock[torpedo] = 2
    if defence_type == 'middle':# 对中时ban掉地狱火和FW190，每种鱼雷机允许使用2架以便调速
        Equipment_Stock[F6F_HellCat_HVAR] = 1
        Equipment_Stock[FW190A6] = 1
        for torpedo in Torpedoes:
            Equipment_Stock[torpedo] = 2
    if Equipment_Stock_Limit: Equipment_Stock.update({k: v for k, v in Equipment_Stock_Limit.items()})  # 根据设置更新限制名单

    global equip_arr
    equip_arr = [None] * 12

    #  剪枝条件1：利用库存限制剪枝
    def conflict(i,equip):
        if equip in Equipment_Stock:
            if equip_arr[:i+1].count(equip) > Equipment_Stock.get(equip):  # 超出库存限制的判装备冲突
                return True


    # 剪枝条件2：单船cd判定
    def ship_single_valid(arr):
        global equipped_warship0
        equipped_warship0 = EquippedWarship(team[0], arr[1], arr[2], arr[3], arr[0][0], arr[0][1])
        cd0 = equipped_warship0.cd_calculator()
        if (cd_min_limit + 0.03) <= cd0 <= (cd_max_limit - 0.03):
            return cd0
        else:
            return False

    # 剪枝条件3：双船cd判定；附带隐式剪枝：cd从小到大遍历，一旦超出最大cd限制直接跳过后续尝试
    def ship_double_valid(cd0, arr):
        global equipped_warship1
        equipped_warship1 = EquippedWarship(team[1], arr[5], arr[6], arr[7], arr[4][0], arr[4][1])
        cd1 = equipped_warship1.cd_calculator()
        if cd1 < max(cd0 - 0.28, cd_min_limit):
            return False
        elif max(cd0 - (
                (0.28 if mode == 'monthly' else 0.37) if team[0] == Implacable else (
                0.15 if mode == 'monthly' else 0.2)),
                 cd_min_limit) <= cd1 <= cd0 - 0.03:
            return cd1
        else:
            return 'break'

    # 剪枝条件4：三船cd判定；附带隐式剪枝：cd从小到大遍历，一旦超出最大cd限制直接跳过后续尝试
    def ship_triple_valid(cd0, cd1, arr):
        global equipped_warship2
        equipped_warship2 = EquippedWarship(team[2], arr[9], arr[10], arr[11], arr[8][0], arr[8][1])
        cd2 = equipped_warship2.cd_calculator()
        if team[0] == Implacable:
            if cd2 < cd0 + 0.03:
                return False
            elif cd0 + 0.03 <= cd2 <= min(cd_max_limit, (
                    ((0.43 if mode == 'monthly' else 0.5) + cd1) if (
                            cd0 - cd1 < (0.125 if mode == 'monthly' else 0.166)) else (
                            cd0 + (0.28 if mode == 'monthly' else 0.34)))):
                return cd2
            else:
                return 'break'
        if team[0] == August:
            if cd2 < cd0 + 0.03:
                return False
            elif cd0 + 0.03 <= cd2 <= min(cd_max_limit, (
                    ((0.3 if mode == 'monthly' else 0.41) + cd1) if (
                            cd0 - cd1 < (0.125 if mode == 'monthly' else 0.166)) else (
                            cd0 + (0.18 if mode == 'monthly' else 0.25)))):
                return cd2
            else:
                return 'break'

    #  回溯（主函数）
    #  本函数将严格按照cd1 < cd0 < cd2的顺序筛选配装，但显然首飞和尾飞舰船的顺序颠倒也应当算是调速成功，故该主函数需要运行两次，直接运行一次，调换后两艘顺序后再运行一次
    def equip_selection(i):
        global cd0, cd1, cd2
        if i > 11:
            # 计算各船伤害
            ship1_dmg = equipped_warship0.dmg_calculator()
            ship2_dmg = equipped_warship1.dmg_calculator()
            ship3_dmg = equipped_warship2.dmg_calculator()

            # 计算总伤害
            total_damage = ship1_dmg + ship2_dmg + ship3_dmg

            # 生成方案描述字符串
            # 1. 判断是否能进入堆
            can_enter_heap = False
            if len(valid_solutions) < heapN:
                can_enter_heap = True
            elif total_damage > valid_solutions[0][0]:
                can_enter_heap = True

            # 2. 如果能进入堆，则生成描述字符串并处理入堆逻辑
            if can_enter_heap:
                # 生成方案描述字符串 (延迟到必要时才生成)
                try:
                    solution_string = f'{equipped_warship0.print_out()}(cd={equipped_warship0.cd_calculator():.2f}),   {equipped_warship1.print_out()}(cd={equipped_warship1.cd_calculator():.2f}),   {equipped_warship2.print_out()}(cd={equipped_warship2.cd_calculator():.2f})'
                except (IndexError, AttributeError) as e:
                    # Fallback string if structure is unexpected
                    solution_string = f"Solution at i=12, equip_arr: {[getattr(e, 'name', e) for e in equip_arr]}"

                new_solution = (total_damage, ship1_dmg, ship2_dmg, ship3_dmg, solution_string)

                if len(valid_solutions) < heapN:
                    # 如果堆未满，直接加入
                    heapq.heappush(valid_solutions, new_solution)
                else:
                    # 如果堆已满，且新方案更好，则替换堆顶。(can_enter_heap 已保证 total_damage > valid_solutions[0][0])
                    heapq.heapreplace(valid_solutions, new_solution)
        else:
            for j in available_equipment_set[i]:
                equip_arr[i] = j
                if 1 <= (i % 4) <= 3:
                    if conflict(i,j):
                        continue
                if i == 3:
                    cd0 = ship_single_valid(equip_arr)
                    if not cd0:
                        continue
                    equip_selection(i + 1)
                elif i == 7:
                    cd1 = ship_double_valid(cd0, equip_arr)
                    if not cd1: continue
                    if cd1 == 'break': return
                    equip_selection(i + 1)
                elif i == 11:
                    cd2 = ship_triple_valid(cd0, cd1, equip_arr)
                    if not cd2: continue
                    if cd2 == 'break': return
                    equip_selection(i + 1)
                else:
                    equip_selection(i + 1)

    # 求解函数
    # 此函数可同时适配日航队和美航队
    def getresult():
        global available_equipment_set, valid_solutions, heapN
        heapN = N if N_valid else 1  # 打印前N个最高伤害的方案
        valid_solutions = []
        available_equipment_set = equipment_valid_set(team)
        equip_selection(0)
        # 交换team中后两艘船的顺序，注意可选飞机列表和好感度也需要同步进行中四位和后四位的对调
        if core == Shinano:
            team[1], team[2] = team[2], team[1]
            favorabilities[1], favorabilities[2] = favorabilities[2], favorabilities[1]
            available_equipment_set = equipment_valid_set(team)
            equip_selection(0)
        if valid_solutions:
            # 按总伤害降序排序
            top_n_solutions = sorted(valid_solutions, key=lambda x: x[0], reverse=True)
            output_str = str()
            output_str += (
                f"\n--- 当前配队空袭直伤排名前{heapN}配装方案 ---" if N_valid else f"\n--- 当前配队空袭最佳配装方案 ---")
            for i, (total_dmg, dmg1, dmg2, dmg3, solution_str) in enumerate(top_n_solutions):
                output_str += (f"\n\n伤害顺位第 {i + 1}：" if N_valid else f"\n伤害最高方案")
                output_str += (f"\n装备配置：{solution_str}")
                output_str += (
                    f"\n伤害贡献（按上一行舰船出现顺序）：一号位：{dmg1:.2f}，二号位：{dmg2:.2f}，三号位：{dmg3:.2f}")
                output_str += (f"\n此配置下理论直伤：{total_dmg:.2f}")
        else:
            output_str = ("\n当前设置无法调匹配，请修改条件再试")
        return output_str

    outputstr = getresult()
    return outputstr


def main():
    """主函数，供 GUI 调用"""
    # 可以在这里添加任何需要在计算前执行的准备步骤
    result_str = get_result()
    print(result_str)  # 最终结果通过 print 输出，以便 GUI 捕获


# --- 文件末尾 ---
# 如果直接运行此脚本 (而不是被导入)，则执行 main 函数
# 这保留了脚本独立运行的能力
if __name__ == "__main__":
    main()
