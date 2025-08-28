import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import data
import sys
from io import StringIO
from EquipmentData import *
from WarshipData import *
import importlib
import IO_test

class CalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("定身航母队全自动调速器(Pre Release 1)")
        try:
            # 尝试确定图标文件的运行时路径
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                # 如果程序是被 PyInstaller 打包的
                # _MEIPASS 是 PyInstaller 创建的临时文件夹路径
                bundle_dir = sys._MEIPASS
            else:
                # 如果程序是直接运行的 (未打包)
                bundle_dir = os.path.abspath(os.path.dirname(__file__))

            # 构造图标文件的完整路径
            icon_path = os.path.join(bundle_dir, "Implacable.ico")

            # 设置窗口图标
            # 注意：使用 default= 参数有时在打包后可能有问题，直接传路径通常更可靠
            self.root.iconbitmap(icon_path)

        except Exception as e:  # 使用更宽泛的异常捕获
            # 如果图标加载失败（文件未找到、路径错误、格式问题等）
            print(f"警告：无法加载窗口图标 'Implacable.ico'。错误: {e}")
        self.root.geometry("1350x750+100+25")  # 宽x高+x偏移+y偏移 (示例居中)
        self.root.resizable(False, False)  # 固定大小

        # --- 创建主框架 ---
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # --- 创建配置区域 (使用PanedWindow进行横向分割) ---
        config_paned_window = ttk.PanedWindow(main_frame, orient='horizontal')
        config_paned_window.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        main_frame.rowconfigure(0, weight=0) # 配置区不随窗口缩放

        # --- 左侧配置面板 ---
        left_config_frame = ttk.LabelFrame(config_paned_window, text="基础配置", padding="10")
        config_paned_window.add(left_config_frame, weight=1)

        # -- 舰队配置 --
        team_frame = ttk.LabelFrame(left_config_frame, text="舰队配置", padding="5")
        team_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        left_config_frame.columnconfigure(0, weight=1)

        # 核心选择 (ttk.Combobox 作为基准样式)
        ttk.Label(team_frame, text="队伍核心:").grid(row=0, column=0, sticky=tk.W)
        self.core_var = tk.StringVar()
        self.core_combo = ttk.Combobox(team_frame, textvariable=self.core_var, width=12, state="readonly")
        self.core_combo['values'] = ["", "信浓", "约克城II"]
        self.core_combo.set("") # 初始为空
        self.core_combo.grid(row=0, column=1, padx=5)
        self.core_combo.bind('<<ComboboxSelected>>', self.on_core_selected)

        # 定身辅选择 (统一为 ttk.Combobox)
        ttk.Label(team_frame, text="定身辅助:").grid(row=1, column=0, sticky=tk.W, pady=(5,0))
        self.freeze_var = tk.StringVar()
        self.freeze_combo = ttk.Combobox(team_frame, textvariable=self.freeze_var, width=12, state="readonly")
        self.freeze_combo['values'] = ["", "怨仇", "奥古斯特"]
        self.freeze_combo.set("")
        self.freeze_combo.grid(row=1, column=1, padx=5, pady=(5,0))

        # 打手选择 (依赖核心选择, 统一为 ttk.Combobox)
        ttk.Label(team_frame, text="打手:").grid(row=2, column=0, sticky=tk.W, pady=(5,0))
        self.maincarrier_var = tk.StringVar()
        self.maincarrier_combo = ttk.Combobox(team_frame, textvariable=self.maincarrier_var, width=12, state="disabled") # 初始禁用
        self.maincarrier_combo['values'] = [""]
        self.maincarrier_combo.set("")
        self.maincarrier_combo.grid(row=2, column=1, padx=5, pady=(5,0))
        self.maincarrier_combo.bind('<<ComboboxSelected>>', self.on_maincarrier_selected)

        # 好感度选择 (统一为 ttk.Combobox)
        ttk.Label(team_frame, text="好感度:").grid(row=3, column=0, sticky=tk.W, pady=(10,0))
        fav_frame = ttk.Frame(team_frame)
        fav_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=(10,0))
        self.freeze_fav_var = tk.StringVar(value="婚200")
        self.core_fav_var = tk.StringVar(value="婚200")
        self.maincarrier_fav_var = tk.StringVar(value="婚200")
        # 使用 ttk.Combobox 替换 tk.OptionMenu 并应用统一样式
        self.freeze_fav_combo = ttk.Combobox(fav_frame, textvariable=self.freeze_fav_var, values=["婚200", "爱100"], width=6, state="readonly")
        self.core_fav_combo = ttk.Combobox(fav_frame, textvariable=self.core_fav_var, values=["婚200", "爱100"], width=6, state="readonly")
        self.maincarrier_fav_combo = ttk.Combobox(fav_frame, textvariable=self.maincarrier_fav_var, values=["婚200", "爱100"], width=6, state="readonly")
        self.freeze_fav_combo.pack(side=tk.LEFT, padx=(0,2))
        self.core_fav_combo.pack(side=tk.LEFT, padx=2)
        self.maincarrier_fav_combo.pack(side=tk.LEFT, padx=(2,0))

        # -- 科技点加成 --
        tech_frame = ttk.LabelFrame(left_config_frame, text="科技点加成", padding="5")
        tech_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

        ttk.Label(tech_frame, text="航空:").grid(row=0, column=0, sticky=tk.W)
        self.tech_atk_var = tk.StringVar(value=str(data.tech_atk))
        self.tech_atk_entry = ttk.Entry(tech_frame, textvariable=self.tech_atk_var, width=8)
        self.tech_atk_entry.grid(row=0, column=1, padx=(5, 15))

        ttk.Label(tech_frame, text="命中:").grid(row=0, column=2, sticky=tk.W)
        self.tech_acc_var = tk.StringVar(value=str(data.tech_acc))
        self.tech_acc_entry = ttk.Entry(tech_frame, textvariable=self.tech_acc_var, width=8)
        self.tech_acc_entry.grid(row=0, column=3, padx=(5, 15))

        ttk.Label(tech_frame, text="装填:").grid(row=0, column=4, sticky=tk.W)
        self.tech_load_var = tk.StringVar(value=str(data.tech_load))
        self.tech_load_entry = ttk.Entry(tech_frame, textvariable=self.tech_load_var, width=8)
        self.tech_load_entry.grid(row=0, column=5, padx=(5, 0))

        # -- 模式与护甲 -- (统一为 ttk.Combobox)
        mode_def_frame = ttk.Frame(left_config_frame)
        mode_def_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

        ttk.Label(mode_def_frame, text="模式:").grid(row=0, column=0, sticky=tk.W)
        self.mode_var = tk.StringVar(value=data.mode)
        # 使用 ttk.Combobox 替换 tk.OptionMenu 并应用统一样式
        self.mode_combo = ttk.Combobox(mode_def_frame, textvariable=self.mode_var, values=["月度困难", "META"], width=12, state="readonly")
        self.mode_combo.grid(row=0, column=1, padx=(5, 15))
        self.mode_var.trace_add('write', self.on_mode_or_defence_change) # 绑定变化事件

        ttk.Label(mode_def_frame, text="敌方护甲:").grid(row=0, column=2, sticky=tk.W)
        self.defence_type_var = tk.StringVar(value=data.defence_type)
        # 使用 ttk.Combobox 替换 tk.OptionMenu 并应用统一样式
        self.defence_combo = ttk.Combobox(mode_def_frame, textvariable=self.defence_type_var, values=["对轻", "对中", "对重"], width=12, state="readonly")
        self.defence_combo.grid(row=0, column=3, padx=(5, 0))
        self.defence_type_var.trace_add('write', self.on_mode_or_defence_change) # 绑定变化事件

        # -- 空袭CD限制 --
        cd_frame = ttk.LabelFrame(left_config_frame, text="空袭CD限制", padding="5")
        cd_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

        ttk.Label(cd_frame, text="下限 (s):").grid(row=0, column=0, sticky=tk.W)
        self.cd_min_var = tk.StringVar(value=str(data.cd_min_limit))
        self.cd_min_entry = ttk.Entry(cd_frame, textvariable=self.cd_min_var, width=8)
        self.cd_min_entry.grid(row=0, column=1, padx=(5, 15))

        ttk.Label(cd_frame, text="上限 (s):").grid(row=0, column=2, sticky=tk.W)
        self.cd_max_var = tk.StringVar(value=str(data.cd_max_limit))
        self.cd_max_entry = ttk.Entry(cd_frame, textvariable=self.cd_max_var, width=8)
        self.cd_max_entry.grid(row=0, column=3, padx=(5, 0))


        # --- 中间配置面板 ---
        middle_config_frame = ttk.LabelFrame(config_paned_window, text="指挥猫加成", padding="10")
        config_paned_window.add(middle_config_frame, weight=1)

        # -- 指挥猫 Buff --
        buff_frame = ttk.LabelFrame(middle_config_frame, text="Buff选择", padding="5")
        buff_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        middle_config_frame.columnconfigure(0, weight=1)

        self.independence_buff_var = tk.BooleanVar(value=data.independence_buff)
        independence_cb = ttk.Checkbutton(buff_frame, text="空域辅助4%装填航空加成", variable=self.independence_buff_var)
        independence_cb.grid(row=0, column=0, sticky=tk.W, pady=(0, 2))

        self.cat_percentage_buff_var = tk.BooleanVar(value=data.cat_percentage_buff)
        cat_percentage_cb = ttk.Checkbutton(buff_frame, text="指挥喵4.041%航空加成", variable=self.cat_percentage_buff_var)
        cat_percentage_cb.grid(row=1, column=0, sticky=tk.W, pady=2)

        self.cat_extra_percentage_buff_var = tk.BooleanVar(value=data.cat_extra_percentage_buff)
        cat_extra_percentage_cb = ttk.Checkbutton(buff_frame, text="毗沙丸1.288%航空/装填加成", variable=self.cat_extra_percentage_buff_var)
        cat_extra_percentage_cb.grid(row=2, column=0, sticky=tk.W, pady=2)

        # -- IJN指挥官 --
        ijn_frame = ttk.Frame(middle_config_frame)
        ijn_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Label(ijn_frame, text="重樱指挥官等级 (0-3):").pack(side=tk.LEFT)
        self.ijn_commander_var = tk.StringVar(value=str(data.ijn_commander))
        self.ijn_commander_spinbox = ttk.Spinbox(ijn_frame, from_=0, to=3, textvariable=self.ijn_commander_var, width=5)
        self.ijn_commander_spinbox.pack(side=tk.LEFT, padx=(5, 0))

        # -- 指挥猫配置 (Cat1 & Cat2) --
        cat_config_frame = ttk.LabelFrame(middle_config_frame, text="指挥猫配置", padding="5")
        cat_config_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        # Cat1
        ttk.Label(cat_config_frame, text="指挥猫1:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        cat1_inner_frame = ttk.Frame(cat_config_frame)
        cat1_inner_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        # 布尔值部分
        self.cat1_bool_vars = [tk.BooleanVar(value=v) for v in data.cat1[:4]]
        bool_names = ["火", "ACE", "林", "既定"]
        for i, name in enumerate(bool_names):
            cb = ttk.Checkbutton(cat1_inner_frame, text=name, variable=self.cat1_bool_vars[i])
            cb.grid(row=0, column=i, sticky=tk.W, padx=(0, 10))
        # 整数部分
        self.cat1_int_vars = [tk.StringVar(value=str(v)) for v in data.cat1[4:]]
        int_names = ["空中杀手", "格纳库", "苍穹猎手"]
        for i, name in enumerate(int_names):
            inner_f = ttk.Frame(cat1_inner_frame)
            inner_f.grid(row=1, column=i, sticky=tk.W, padx=(0, 10), pady=(5, 0))
            ttk.Label(inner_f, text=name+"(0-3):").pack(side=tk.LEFT)
            sb = ttk.Spinbox(inner_f, from_=0, to=3, textvariable=self.cat1_int_vars[i], width=3)
            sb.pack(side=tk.LEFT, padx=(2, 0))

        # Cat2
        ttk.Label(cat_config_frame, text="指挥猫2:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        cat2_inner_frame = ttk.Frame(cat_config_frame)
        cat2_inner_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        # 布尔值部分
        self.cat2_bool_vars = [tk.BooleanVar(value=v) for v in data.cat2[:4]]
        bool_names = ["火", "ACE", "林", "既定"]
        for i, name in enumerate(bool_names):
            cb = ttk.Checkbutton(cat2_inner_frame, text=name, variable=self.cat2_bool_vars[i])
            cb.grid(row=0, column=i, sticky=tk.W, padx=(0, 10))
        # 整数部分
        self.cat2_int_vars = [tk.StringVar(value=str(v)) for v in data.cat2[4:]]
        int_names = ["空中杀手", "格纳库", "苍穹猎手"]
        for i, name in enumerate(int_names):
            inner_f = ttk.Frame(cat2_inner_frame)
            inner_f.grid(row=1, column=i, sticky=tk.W, padx=(0, 10), pady=(5, 0))
            ttk.Label(inner_f, text=name+"(0-3):").pack(side=tk.LEFT)
            sb = ttk.Spinbox(inner_f, from_=0, to=3, textvariable=self.cat2_int_vars[i], width=3)
            sb.pack(side=tk.LEFT, padx=(2, 0))


        # --- 右侧配置面板 (调整高度) ---
        right_config_frame = ttk.LabelFrame(config_paned_window, text="其他配置", padding="10")
        config_paned_window.add(right_config_frame, weight=1)

        # -- N_valid 和 N --
        n_frame = ttk.Frame(right_config_frame)
        n_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        # 移除 right_config_frame.columnconfigure(0, weight=1) 以避免不必要的扩展

        self.n_valid_var = tk.BooleanVar(value=data.n_valid)
        n_valid_cb = ttk.Checkbutton(n_frame, text="显示前N个方案", variable=self.n_valid_var)
        n_valid_cb.pack(side=tk.LEFT)
        ttk.Label(n_frame, text="N=").pack(side=tk.LEFT, padx=(10, 0))
        self.n_var = tk.StringVar(value=str(data.n))
        self.n_spinbox = ttk.Spinbox(n_frame, from_=1, to=999, textvariable=self.n_var, width=6)
        self.n_spinbox.pack(side=tk.LEFT, padx=(2, 0))

        # -- 敌人数据 --
        enemy_frame = ttk.LabelFrame(right_config_frame, text="敌人数据", padding="5")
        enemy_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.auto_enemy_var = tk.BooleanVar(value=data.auto_enemy_data)
        self.auto_enemy_cb = ttk.Checkbutton(enemy_frame, text="使用预设敌人数据", variable=self.auto_enemy_var, command=self.toggle_enemy_inputs)
        self.auto_enemy_cb.grid(row=0, column=0, columnspan=4, sticky=tk.W)

        ttk.Label(enemy_frame, text="机动:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.enemy_mobility_var = tk.StringVar(value=str(data.enemy_mobility))
        self.enemy_mobility_entry = ttk.Entry(enemy_frame, textvariable=self.enemy_mobility_var, width=8, state='disabled' if data.auto_enemy_data else 'normal')
        self.enemy_mobility_entry.grid(row=1, column=1, padx=(5, 15), pady=(5, 0))

        ttk.Label(enemy_frame, text="幸运:").grid(row=1, column=2, sticky=tk.W, pady=(5, 0))
        self.enemy_fortune_var = tk.StringVar(value=str(data.enemy_fortune))
        self.enemy_fortune_entry = ttk.Entry(enemy_frame, textvariable=self.enemy_fortune_var, width=8, state='disabled' if data.auto_enemy_data else 'normal')
        self.enemy_fortune_entry.grid(row=1, column=3, padx=(5, 0), pady=(5, 0))

        # -- 奥古斯特增伤 & 常用飞机 --
        aug_freq_frame = ttk.Frame(right_config_frame)
        aug_freq_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.august_targeted_var = tk.BooleanVar(value=data.august_targeted_enabled)
        aug_targeted_cb = ttk.Checkbutton(aug_freq_frame, text="奥古斯特对轻/重巡增伤", variable=self.august_targeted_var)
        aug_targeted_cb.pack(side=tk.LEFT)

        self.frequent_only_var = tk.BooleanVar(value=data.frequent_only)
        frequent_only_cb = ttk.Checkbutton(aug_freq_frame, text="仅使用常用飞机", variable=self.frequent_only_var)
        frequent_only_cb.pack(side=tk.LEFT, padx=(10, 0))

        # -- 装备库存限制 (调整高度) --
        # 调整 equip_limit_frame 的 sticky 和内部权重，限制其高度增长
        equip_limit_frame = ttk.LabelFrame(right_config_frame, text="装备库存限制", padding="5")
        # 移除 sticky 中的 tk.S，并移除 rowconfigure weight，使其不随窗口扩展
        equip_limit_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 5))
        # 不再给这一行设置 weight，这样它就不会被拉伸了
        # right_config_frame.rowconfigure(3, weight=1)

        # 添加新限制的控件
        add_limit_frame = ttk.Frame(equip_limit_frame)
        add_limit_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        # 不再给列设置 weight
        # equip_limit_frame.columnconfigure(0, weight=1)
        # equip_limit_frame.columnconfigure(1, weight=1)

        ttk.Label(add_limit_frame, text="选择飞机:").pack(side=tk.LEFT)
        # 从Aircrafts列表获取名称
        aircraft_names = [a.name for a in Aircrafts]
        self.equip_var = tk.StringVar()
        self.equip_combo = ttk.Combobox(add_limit_frame, textvariable=self.equip_var, values=aircraft_names, width=20, state="readonly")
        if aircraft_names:
             self.equip_combo.set(aircraft_names[0]) # 默认选第一个
        self.equip_combo.pack(side=tk.LEFT, padx=(5, 10))

        ttk.Label(add_limit_frame, text="数量:").pack(side=tk.LEFT)
        self.equip_limit_var = tk.StringVar(value="1")
        self.equip_limit_spinbox = ttk.Spinbox(add_limit_frame, from_=1, to=999, textvariable=self.equip_limit_var, width=6)
        self.equip_limit_spinbox.pack(side=tk.LEFT, padx=(5, 10))

        self.add_equip_button = ttk.Button(add_limit_frame, text="添加", command=self.add_equipment_limit)
        self.add_equip_button.pack(side=tk.LEFT)

        # 显示已选限制的列表框和滚动条 (限制高度)
        listbox_frame = ttk.Frame(equip_limit_frame)
        listbox_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N), pady=(0, 5))
        # 不再给行设置 weight
        # equip_limit_frame.rowconfigure(1, weight=1)

        # 通过指定 height 来限制 Listbox 的显示行数
        self.equip_listbox = tk.Listbox(listbox_frame, height=4) # 例如，显示4行
        listbox_scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.equip_listbox.yview)
        self.equip_listbox.configure(yscrollcommand=listbox_scrollbar.set)
        self.equip_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True) # 使用 fill=tk.X
        listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 删除按钮
        delete_button_frame = ttk.Frame(equip_limit_frame)
        delete_button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self.delete_selected_button = ttk.Button(delete_button_frame, text="删除所选项", command=self.delete_selected_equipment)
        self.delete_selected_button.pack(side=tk.LEFT, padx=(0, 10))

        self.delete_all_button = ttk.Button(delete_button_frame, text="删除全部", command=self.delete_all_equipment)
        self.delete_all_button.pack(side=tk.LEFT)


        # --- 开始计算按钮 ---
        self.calculate_button = ttk.Button(main_frame, text="开始计算", command=self.collect_and_update_data)
        self.calculate_button.grid(row=1, column=0, pady=5)


        # --- 显示区域 ---
        display_frame = ttk.LabelFrame(main_frame, text="计算结果", padding="5")
        display_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        main_frame.rowconfigure(2, weight=1) # 显示区随窗口缩放
        main_frame.columnconfigure(0, weight=1)

        self.result_text = scrolledtext.ScrolledText(display_frame, state='disabled', wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # 初始化列表框内容
        self.refresh_equipment_listbox()

    # --- GUI 逻辑函数 ---
    def on_core_selected(self, event):
        """当核心选择改变时，更新定身辅和打手的可选项"""
        selected_core_name = self.core_var.get()
        # 重置定身辅和打手选择
        self.freeze_var.set("")
        self.maincarrier_var.set("")
        self.maincarrier_combo.config(state='disabled')

        if selected_core_name == "信浓":
            self.freeze_combo['values'] = ["", "怨仇", "奥古斯特"]
            self.maincarrier_combo['values'] = ["", "天城", "白龙"]
            self.maincarrier_combo.config(state='readonly')
        elif selected_core_name == "约克城II":
            self.freeze_combo['values'] = ["", "怨仇", "奥古斯特"]
            self.maincarrier_combo['values'] = ["", "企业"]
            self.maincarrier_combo.config(state='readonly')
        else: # 空或无效选择
            self.freeze_combo['values'] = ["", "怨仇", "奥古斯特"]
            self.maincarrier_combo['values'] = [""]
            self.maincarrier_combo.config(state='disabled')

    def on_maincarrier_selected(self, event):
        """当打手选择改变时触发（可选）"""
        # 这里可以添加逻辑，如果需要的话
        pass

    def toggle_enemy_inputs(self):
        """根据'使用预设敌人数据'复选框状态，启用/禁用手动输入框"""
        if self.auto_enemy_var.get():
            self.enemy_mobility_entry.config(state='disabled')
            self.enemy_fortune_entry.config(state='disabled')
            # 自动填充预设值
            self.update_preset_enemy_display()
        else:
            self.enemy_mobility_entry.config(state='normal')
            self.enemy_fortune_entry.config(state='normal')

    def on_mode_or_defence_change(self, *args):
        """当模式或敌方护甲类型改变时，如果启用了自动预设，则更新显示"""
        if self.auto_enemy_var.get():
            self.update_preset_enemy_display()

    def update_preset_enemy_display(self):
        """根据当前mode和defence_type更新敌人数据输入框的显示（仅显示，不修改data.py）"""
        mode_key = self.mode_var.get()
        defence_key = self.defence_type_var.get()
        preset_data = data.PRESET_ENEMY_DATA.get(mode_key, {}).get(defence_key, [0, 0])
        self.enemy_mobility_var.set(str(preset_data[0]))
        self.enemy_fortune_var.set(str(preset_data[1]))

    def add_equipment_limit(self):
        """添加装备库存限制"""
        equip_name = self.equip_var.get()
        try:
            limit = int(self.equip_limit_var.get())
            if equip_name:
                # 找到对应的装备对象
                equip_obj = next((a for a in Aircrafts if a.name == equip_name), None)
                if equip_obj:
                    # 更新本地字典副本
                    data.equipment_stock_limit[equip_obj] = limit
                    self.refresh_equipment_listbox()
                    # 重置输入框
                    self.equip_limit_var.set("1")
                else:
                    messagebox.showerror("错误", f"未找到装备对象: {equip_name}")
            else:
                messagebox.showwarning("警告", "请选择一个装备。")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的整数作为数量。")

    def refresh_equipment_listbox(self):
        """刷新装备限制列表框的显示"""
        self.equip_listbox.delete(0, tk.END)
        for equip_obj, limit in data.equipment_stock_limit.items():
            self.equip_listbox.insert(tk.END, f"{equip_obj.name}: {limit}")

    def delete_selected_equipment(self):
        """删除列表框中选中的装备限制"""
        selection = self.equip_listbox.curselection()
        if selection:
            index = selection[0]
            # 获取列表框中的文本
            item_text = self.equip_listbox.get(index)
            equip_name = item_text.split(":")[0].strip()
            # 找到对应的对象并从字典中删除
            equip_obj_to_remove = next((k for k in data.equipment_stock_limit.keys() if k.name == equip_name), None)
            if equip_obj_to_remove:
                del data.equipment_stock_limit[equip_obj_to_remove]
                self.refresh_equipment_listbox()
        else:
            messagebox.showinfo("提示", "请先选择一个项目来删除。")

    def delete_all_equipment(self):
        """删除所有装备限制"""
        data.equipment_stock_limit.clear()
        self.refresh_equipment_listbox()

    def collect_and_update_data(self):
        """收集GUI中的所有数据，更新到data.py，并触发计算（示例）"""
        try:
            # 1. 收集舰船对象
            core_name_map = {"信浓": Shinano, "约克城II": YorkTown2}
            freeze_name_map = {"怨仇": Implacable, "奥古斯特": August}
            maincarrier_name_map = {"天城": Amagi, "白龙": Hakuryu, "企业": Enterprise}

            selected_core_name = self.core_var.get()
            selected_freeze_name = self.freeze_var.get()
            selected_maincarrier_name = self.maincarrier_var.get()

            core_ship = core_name_map.get(selected_core_name)
            freeze_ship = freeze_name_map.get(selected_freeze_name)
            maincarrier_ship = maincarrier_name_map.get(selected_maincarrier_name)

            # 检查必要选择
            if not core_ship:
                messagebox.showerror("配置错误", "请选择队伍核心。")
                return
            if not freeze_ship:
                 messagebox.showwarning("配置警告", "未选择定身辅助，可能影响计算。")
            if not maincarrier_ship:
                messagebox.showerror("配置错误", "请选择打手。")
                return

            # 更新 data.py 中的舰船对象
            data.update_team(freeze_ship, core_ship, maincarrier_ship)

            # 收集好感度
            fav_map = {"婚200": 200, "爱100": 100}
            freeze_fav = fav_map[self.freeze_fav_var.get()]
            core_fav = fav_map[self.core_fav_var.get()]
            maincarrier_fav = fav_map[self.maincarrier_fav_var.get()]
            data.update_favorabilities(freeze_fav, core_fav, maincarrier_fav)

            # 收集科技点
            data.tech_atk = float(self.tech_atk_var.get())
            data.tech_acc = float(self.tech_acc_var.get())
            data.tech_load = float(self.tech_load_var.get())

            # 收集模式和护甲
            mode_map = {"月度困难": 'monthly', "META": 'META'}
            defence_map = {"对轻": 'light', "对中": 'middle', "对重": 'heavy'}
            data.mode = mode_map[self.mode_var.get()]
            data.defence_type = defence_map[self.defence_type_var.get()]

            # 收集CD限制
            data.cd_min_limit = float(self.cd_min_var.get())
            data.cd_max_limit = float(self.cd_max_var.get())

            # 收集指挥猫 Buff
            data.independence_buff = self.independence_buff_var.get()
            data.cat_percentage_buff = self.cat_percentage_buff_var.get()
            data.cat_extra_percentage_buff = self.cat_extra_percentage_buff_var.get()

            # 收集IJN指挥官等级
            data.ijn_commander = int(self.ijn_commander_var.get())

            # 收集指挥猫配置
            cat1_config = [v.get() for v in self.cat1_bool_vars] + [int(v.get()) for v in self.cat1_int_vars]
            cat2_config = [v.get() for v in self.cat2_bool_vars] + [int(v.get()) for v in self.cat2_int_vars]
            data.update_cat_config(cat1_config, cat2_config)

            # 收集N相关设置
            data.n_valid = self.n_valid_var.get()
            data.n = int(self.n_var.get())

            # 收集敌人数据
            auto_flag = self.auto_enemy_var.get()
            if auto_flag:
                # 如果是自动，使用预设值更新 data.py
                mode_key = data.mode
                defence_key = data.defence_type
                preset_data = data.PRESET_ENEMY_DATA.get(mode_key, {}).get(defence_key, [0, 0])
                data.update_enemy_data(auto_flag, preset_data[0], preset_data[1])
            else:
                # 如果是手动，使用输入值更新 data.py
                mob = float(self.enemy_mobility_var.get())
                fort = float(self.enemy_fortune_var.get())
                data.update_enemy_data(auto_flag, mob, fort)

            # 收集其他开关
            data.august_targeted_enabled = self.august_targeted_var.get()
            data.frequent_only = self.frequent_only_var.get()

            # 装备库存限制已在 add/delete 函数中直接更新 data.py

            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()

            try:
                importlib.reload(IO_test)
                # 调用 A.py 中的主计算函数
                IO_test.main()
                # 获取捕获到的输出
                calculation_result = captured_output.getvalue()
            except Exception as e:
                # 如果计算过程出错，也捕获错误信息
                calculation_result = f"计算过程中发生错误:\n{e}"
            finally:
                # 无论是否出错，都必须恢复标准输出
                sys.stdout = old_stdout

            # 将计算结果（或错误信息）显示在 GUI 中
            self.display_result(calculation_result)

        except ValueError as e:
            messagebox.showerror("输入错误", f"请输入有效的数字。\n错误详情: {e}")
        except Exception as e:
            messagebox.showerror("未知错误", f"更新数据或计算时发生错误: {e}")

    def display_result(self, result_string):
        """在结果区域显示文本"""
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result_string)
        self.result_text.config(state='disabled')


# --- 如果需要直接运行此GUI进行测试 ---
if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorGUI(root)
    root.mainloop()



