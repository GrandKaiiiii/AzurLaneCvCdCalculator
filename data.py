# data.py
# 用于存储计算器GUI和计算逻辑之间共享的变量

# --- 初始默认值 ---
# 舰船对象 (将由GUI根据选择进行设置)
freeze = None  # 定身辅选择 (Implacable / August)
core = None    # 舰队核心选择 (Shinano / YorkTown2)
maincarrier = None  # 打手选择 (Amagi / Hakuryu / Enterprise)

# 好感度 (将由GUI根据选择进行设置)
# 200 表示婚, 100 表示爱
favorabilities = [200, 200, 200]  # [freeze, core, maincarrier]
favorabilities_freeze = favorabilities[0]
favorabilities_core = favorabilities[1]
favorabilities_maincarrier = favorabilities[2]

# 舰队列表 (按 [freeze, core, maincarrier] 顺序)
team = [freeze, core, maincarrier]

# 科技点加成
tech_atk = 69
tech_acc = 23
tech_load = 42

# 模式和敌方护甲
mode = None  # 'monthly' or 'META'
defence_type = None  # 'light', 'middle', or 'heavy'

# 空袭CD限制
cd_min_limit = 20.0  # 单位: 秒
cd_max_limit = 21.0  # 单位: 秒

# 指挥猫加成 (Independence_buff, Cat_percentage_buff, Cat_extra_percentage_buff)
independence_buff = True
cat_percentage_buff = True
cat_extra_percentage_buff = True

# IJN指挥官等级 (0-3)
ijn_commander = 0

# 指挥猫配置 (cat1, cat2)
# 前4位布尔值: [火, ACE, 林, 既定]
# 后3位整数 (0-3): [空中杀手, 格纳库之主, 苍穹猎手]
cat1 = [True, True, False, True, 3, 0, 3]
cat2 = [True, True, False, False, 3, 0, 3]

# 结果显示选项
n_valid = True
n = 10

# 敌人数据
auto_enemy_data = True
# 预设或手动输入的敌人数据 [机动, 幸运]
enemy = [75, 50]
enemy_mobility = enemy[0]
enemy_fortune = enemy[1]

# 奥古斯特目标增伤开关
august_targeted_enabled = False

# 仅使用常用飞机开关
frequent_only = True

# 装备库存限制 (装备对象 -> 数量)
equipment_stock_limit = {}

# --- 更新函数 ---
def update_team(freeze_ship, core_ship, maincarrier_ship):
    """更新舰船对象和队伍列表"""
    global freeze, core, maincarrier, team
    freeze = freeze_ship
    core = core_ship
    maincarrier = maincarrier_ship
    team = [freeze, core, maincarrier]

def update_favorabilities(freeze_fav, core_fav, maincarrier_fav):
    """更新好感度"""
    global favorabilities, favorabilities_freeze, favorabilities_core, favorabilities_maincarrier
    favorabilities = [freeze_fav, core_fav, maincarrier_fav]
    favorabilities_freeze = favorabilities[0]
    favorabilities_core = favorabilities[1]
    favorabilities_maincarrier = favorabilities[2]

def update_enemy_data(auto_flag, mobility, fortune):
    """更新敌人数据"""
    global auto_enemy_data, enemy, enemy_mobility, enemy_fortune
    auto_enemy_data = auto_flag
    enemy = [mobility, fortune]
    enemy_mobility = enemy[0]
    enemy_fortune = enemy[1]

def update_cat_config(cat1_config, cat2_config):
    """更新指挥猫配置"""
    global cat1, cat2
    # 确保列表内容被修改而不是引用被替换
    cat1[:] = cat1_config
    cat2[:] = cat2_config

def update_equipment_stock_limit(new_dict):
    """更新装备库存限制字典"""
    global equipment_stock_limit
    # 清空并更新字典内容
    equipment_stock_limit.clear()
    equipment_stock_limit.update(new_dict)

# --- 预设敌人数据映射 (供GUI内部逻辑使用) ---
PRESET_ENEMY_DATA = {
    'monthly': {
        'light': [95, 45],
        'middle': [90, 45],
        'heavy': [74, 45]
    },
    'META': {
        'light': [75, 50],
        'middle': [75, 50],
        'heavy': [75, 50]
    }
}



