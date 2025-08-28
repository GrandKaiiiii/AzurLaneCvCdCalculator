from CdDamageCalculator import *


def ship_cd_calculator(ship: Warship, equip1, equip2, equip3, equip4, equip5):
    if ship == Shinano: return shinano_calculator(1, favorabilities[team.index(ship)], equip1, 1, equip2, 1, equip3, 1,
                                                  equip4, 1, equip5, 1)
    if ship == Amagi: return amagi_calculator(1, favorabilities[team.index(ship)], equip1, 1, equip2, 1, equip3, 1,
                                              equip4, 1, equip5, 1)
    if ship == Implacable: return implacable_calculator(1, favorabilities[team.index(ship)], equip1, 1, equip2, 1,
                                                        equip3, 1, equip4, 1, equip5, 1)
    if ship == Hakuryu: return hakuryu_calculator(1, favorabilities[team.index(ship)], equip1, 1, equip2, 1, equip3, 1,
                                                  equip4, 1, equip5, 1)
    if ship == August: return august_calculator(1, favorabilities[team.index(ship)], equip1, 1, equip2, 1, equip3, 1,
                                                equip4, 1, equip5, 1)


def ship_dmg_calculator(ship: Warship, equip1, equip2, equip3, equip4, equip5):
    if ship == Shinano: return \
    shinano_calculator(0, favorabilities[team.index(ship)], equip1, 1, equip2, 1, equip3, 1, equip4, 1, equip5, 1)[1]
    if ship == Amagi: return \
    amagi_calculator(0, favorabilities[team.index(ship)], equip1, 1, equip2, 1, equip3, 1, equip4, 1, equip5, 1)[1]
    if ship == Implacable: return \
    implacable_calculator(0, favorabilities[team.index(ship)], equip1, 1, equip2, 1, equip3, 1, equip4, 1, equip5, 1)[1]
    if ship == Hakuryu: return \
    hakuryu_calculator(0, favorabilities[team.index(ship)], equip1, 1, equip2, 1, equip3, 1, equip4, 1, equip5, 1)[1]
    if ship == August: return \
    august_calculator(0, favorabilities[team.index(ship)], equip1, 1, equip2, 1, equip3, 1, equip4, 1, equip5, 1)[1]


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
            if key == 'Torpedo': available_list.extend(Torpedoes) if freeze != August else available_list.append(C6N1)
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
            print([a.name for a in available_equipment_set[i]])
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
if defence_type == 'middle':# 对中时ban掉地狱火和FW190，每种鱼雷机保留两架用作调速
    Equipment_Stock[F6F_HellCat_HVAR] = 1
    Equipment_Stock[FW190A6] = 1
    for torpedo in Torpedoes:
        Equipment_Stock[torpedo] = 2
if Equipment_Stock_Limit: Equipment_Stock.update({k: v for k, v in Equipment_Stock_Limit.items()})  # 根据设置更新限制名单


equip_arr = [None] * 12
valid_solutions = []


#  剪枝条件1
def conflict(equip):
    global equip_arr
    if equip in Equipment_Stock:
        if equip_arr.count(equip) > Equipment_Stock.get(equip):  # 超出库存限制的判装备冲突
            return True


# 剪枝条件2：单船cd判定
def ship_single_valid(arr):
    a, b, c, d, e = arr[1], arr[2], arr[3], arr[0][0], arr[0][1]
    cd0 = ship_cd_calculator(team[0], a, b, c, d, e)
    if not cd_min_limit + 0.03 <= cd0 <= cd_max_limit - 0.03:
        return False
    else:
        return cd0


# 剪枝条件3：双船cd判定；附带隐式剪枝：cd从小到大遍历，一旦超出最大cd限制直接跳过后续尝试
def ship_double_valid(cd0, arr):
    a, b, c, d, e = arr[5], arr[6], arr[7], arr[4][0], arr[4][1]
    cd1 = ship_cd_calculator(team[1], a, b, c, d, e)
    if cd1 < max(cd0 - 0.28, cd_min_limit + 0.03):
        return False
    elif max(cd0 - (
    (0.28 if mode == 'monthly' else 0.37) if team[0] == Implacable else (0.15 if mode == 'monthly' else 0.2)),
             cd_min_limit) <= cd1 <= cd0 - 0.03:
        return cd1
    else:
        return 'break'


# 剪枝条件4：三船cd判定；附带隐式剪枝：cd从小到大遍历，一旦超出最大cd限制直接跳过后续尝试
def ship_triple_valid(cd0, cd1, arr):
    a, b, c, d, e = arr[9], arr[10], arr[11], arr[8][0], arr[8][1]
    cd2 = ship_cd_calculator(team[2], a, b, c, d, e)
    if team[0] == Implacable:
        if cd2 < cd0 + 0.03:
            return False
        elif cd0 + 0.03 <= cd2 <= min(cd_max_limit, (
        ((0.43 if mode == 'monthly' else 0.5) + cd1) if (cd0 - cd1 < (0.125 if mode == 'monthly' else 0.166)) else (
                cd0 + (0.28 if mode == 'monthly' else 0.34)))):
            return cd2
        else:
            return 'break'
    if team[0] == August:
        if cd2 < cd0 + 0.03:
            return False
        elif cd0 + 0.03 <= cd2 <= min(cd_max_limit, (
        ((0.3 if mode == 'monthly' else 0.41) + cd1) if (cd0 - cd1 < (0.125 if mode == 'monthly' else 0.166)) else (
                cd0 + (0.18 if mode == 'monthly' else 0.25)))):
            return cd2
        else:
            return 'break'


#  回溯（主函数）
#  本函数将严格按照cd1 < cd0 < cd2的顺序筛选配装，但显然首飞和尾飞舰船的顺序颠倒也应当算是调速成功，故该主函数需要运行两次，直接运行一次，调换后两艘顺序后再运行一次
def equip_selection(i):
    global equip_arr, cd0, cd1, cd2
    if i > 11:
        # 计算各船伤害
        ship1_dmg = ship_dmg_calculator(team[0], equip_arr[1], equip_arr[2], equip_arr[3], equip_arr[0][0],
                                        equip_arr[0][1])
        ship2_dmg = ship_dmg_calculator(team[1], equip_arr[5], equip_arr[6], equip_arr[7], equip_arr[4][0],
                                        equip_arr[4][1])
        ship3_dmg = ship_dmg_calculator(team[2], equip_arr[9], equip_arr[10], equip_arr[11], equip_arr[8][0],
                                        equip_arr[8][1])

        # 计算总伤害
        total_damage = ship1_dmg + ship2_dmg + ship3_dmg

        # 生成方案描述字符串
        try:
            equip_name = list(k.name for k in
                              [equip_arr[1], equip_arr[2], equip_arr[3], equip_arr[0][0], equip_arr[0][1], equip_arr[5],
                               equip_arr[6], equip_arr[7], equip_arr[4][0], equip_arr[4][1], equip_arr[9],
                               equip_arr[10], equip_arr[11], equip_arr[8][0], equip_arr[8][1]])
            solution_string = f'{team[0].name}：{" ".join(equip_name[0:5])}；  {team[1].name}：{" ".join(equip_name[5:10])}；  {team[2].name}：{" ".join(equip_name[10:15])}, 遍历到此解时，已存储{len(valid_solutions)}个解'
        except (IndexError, AttributeError) as e:
            # Fallback string if structure is unexpected
            solution_string = f"Solution at i=12, equip_arr: {[getattr(e, 'name', e) for e in equip_arr]}"

        # 存储结果
        valid_solutions.append((total_damage, ship1_dmg, ship2_dmg, ship3_dmg, solution_string))
    else:
        for j in available_equipment_set[i]:
            equip_arr[i] = j
            if 1 <= (i % 4) <= 3:
                if conflict(j): continue
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
def get_result():
    global available_equipment_set
    available_equipment_set = equipment_valid_set(team)
    equip_selection(0)
    # 交换team中后两艘船的顺序，注意可选飞机列表和好感度也需要同步进行中四位和后四位的对调
    if core == Shinano:
        team[1], team[2] = team[2], team[1]
        favorabilities[1], favorabilities[2] = favorabilities[2], favorabilities[1]
        available_equipment_set = equipment_valid_set(team)
        equip_selection(0)


    heapN = N if N_valid else 1  # 打印前N个最高伤害的方案
    if valid_solutions:
        # 按总伤害降序排序
        # 由于经常能跑出来几万个匹配结果因此选择使用维护大顶堆heapq.nlargest的方式减少复杂度
        import heapq

        top_n_solutions = heapq.nlargest(heapN, valid_solutions, key=lambda x: x[0])

        print(f"\n--- 当前配队空袭直伤排名前{heapN}配装方案 ---" if N_valid else f"\n--- 当前配队空袭最佳配装方案 ---")
        for i, (total_dmg, dmg1, dmg2, dmg3, solution_str) in enumerate(top_n_solutions):
            print(f"\n伤害顺位第 {i + 1}：" if N_valid else f"\n伤害最高方案")
            print(f"  装备配置：{solution_str}")
            print(f"  伤害贡献（按上一行舰船出现顺序）：一号位：{dmg1:.2f}，二号位：{dmg2:.2f}，三号位：{dmg3:.2f}")
            print(f"  此配置下理论直伤：{total_dmg:.2f}")
    else:
        print("\n当前设置无法调匹配，请修改条件再试")

get_result()
