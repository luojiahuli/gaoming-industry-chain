"""
高明区产业链知识图谱 - 企业数据补充脚本
基于 WebSearch 搜到的公开信息，补充更多存量企业和新建项目
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from database import get_conn, add_enterprise, add_investment, add_chain, add_infrastructure, query, query_one

# ── 新增企业数据 ──────────────────────────────────────────────
# 格式: (name, industry, sub_industry, chain_stage, scale, revenue_annual, employee_count, source, description, chain_ids)

NEW_ENTERPRISES = [
    # ── 装备制造 ──
    {"name": "索斯科锁定技术（佛山）有限公司", "industry": "装备制造", "sub_industry": "精密锁定系统",
     "chain_stage": "中游", "scale": "大型", "revenue_annual": 5, "employee_count": 300,
     "source": "2025年投产（佛山市高明区招商局）", "description": "全球锁具领军企业美资索斯科佛山新厂，2025年9月开业，总投资1亿美元，位于专精特新湾·平谦智造产业园",
     "chain_ids": [3]},
    {"name": "广东德太工业自动化科技有限公司", "industry": "装备制造", "sub_industry": "智能装备集成",
     "chain_stage": "中游", "scale": "中小微", "revenue_annual": 2, "employee_count": 150,
     "source": "2025年签约", "description": "星宇电子智能装备集成系统项目，生产气缸、电磁阀等，投资2亿元",
     "chain_ids": [3]},
    {"name": "佛山市恒奥佳化工机械有限公司", "industry": "装备制造", "sub_industry": "新能源装备",
     "chain_stage": "中游", "scale": "中小微", "revenue_annual": 1.2, "employee_count": 100,
     "source": "2025年签约", "description": "恒奥佳高端智能装备生产制造基地项目，投资1.2亿元，新能源高端装备",
     "chain_ids": [3]},
    {"name": "佛山市泓众机械设备有限公司", "industry": "装备制造", "sub_industry": "金属加工设备",
     "chain_stage": "中游", "scale": "中小微", "revenue_annual": 2.1, "employee_count": 120,
     "source": "2025年签约", "description": "泓众机械装备智造基地项目，投资2.1亿元，金属加工设备制造",
     "chain_ids": [3]},
    {"name": "广东豪斯特汽车零部件有限公司", "industry": "装备制造", "sub_industry": "汽车零部件",
     "chain_stage": "中游", "scale": "大型", "revenue_annual": 10, "employee_count": 500,
     "source": "2024年投产（政府公开信息）", "description": "豪斯特高端汽车零部件及电池包壳体项目，总投资20亿元，C/D栋已投产，B栋预计2025年投产",
     "chain_ids": [3]},
    {"name": "佛山市中盈重工有限公司", "industry": "装备制造", "sub_industry": "船舶装备",
     "chain_stage": "中游", "scale": "中型", "revenue_annual": 5, "employee_count": 300,
     "source": "2025年签约", "description": "中盈船舶装备制造基地项目，投资5亿元，船用舱口盖制造",
     "chain_ids": [3]},
    {"name": "程旭精密机械", "industry": "装备制造", "sub_industry": "精密机械",
     "chain_stage": "中游", "scale": "中小微", "revenue_annual": 1.5, "employee_count": 80,
     "source": "2025年签约", "description": "程旭精密机械智能制造总部基地项目，位于荷城街道",
     "chain_ids": [3]},
    {"name": "本田金属（佛山）有限公司", "industry": "装备制造", "sub_industry": "汽车零部件",
     "chain_stage": "中游", "scale": "大型", "revenue_annual": 15, "employee_count": 800,
     "source": "高明区重点骨干企业", "description": "本田金属佛山公司，高明区装备制造龙头企业，汽车零部件制造",
     "chain_ids": [3]},

    # ── 电子信息 ──
    {"name": "新启航半导体有限公司", "industry": "电子信息", "sub_industry": "半导体",
     "chain_stage": "上游", "scale": "中型", "revenue_annual": 3, "employee_count": 200,
     "source": "2024-2025中国IC独角兽榜单", "description": "佛山唯一入选中国IC独角兽企业，超快激光微纳加工、微纳图形3D光学测量，国家高新技术企业、广东省专精特新企业",
     "chain_ids": [7]},

    # ── 新材料 ──
    {"name": "佛山市高明亿阳塑胶有限公司", "industry": "新材料", "sub_industry": "高分子材料",
     "chain_stage": "中游", "scale": "中型", "revenue_annual": 8, "employee_count": 400,
     "source": "2025年签约", "description": "亿阳塑胶高分子新材料研发生产基地，投资10亿元，PVC高分子新材料",
     "chain_ids": [5]},
    {"name": "广东远华新材料股份有限公司", "industry": "新材料", "sub_industry": "高性能复合材料",
     "chain_stage": "中游", "scale": "大型", "revenue_annual": 12, "employee_count": 600,
     "source": "2025年增资扩产", "description": "广东远华新材料产业园项目，投资25亿元（增资扩产），打造国内一流材料产业园",
     "chain_ids": [5]},
    {"name": "聚圣科技有限公司", "industry": "新材料", "sub_industry": "聚合物复合材料",
     "chain_stage": "中游", "scale": "中型", "revenue_annual": 5, "employee_count": 250,
     "source": "高明区重点骨干企业", "description": "聚合物复合材料领域龙头企业，高明区聚合物复合材料产业集群入选2025年广东省中小企业特色产业集群",
     "chain_ids": [5]},
    {"name": "广东晟阳节能玻璃有限公司", "industry": "新材料", "sub_industry": "节能玻璃",
     "chain_stage": "中游", "scale": "中型", "revenue_annual": 5, "employee_count": 300,
     "source": "2024年动工", "description": "广东晟阳节能新材料制造（总部）项目，投资8亿元，位于专精特新湾",
     "chain_ids": [5]},
    {"name": "广东三和兴模具材料科技有限公司", "industry": "新材料", "sub_industry": "模具材料",
     "chain_stage": "上游", "scale": "中小微", "revenue_annual": 1.5, "employee_count": 100,
     "source": "2025年签约", "description": "广东三和兴高端模具主件项目，投资1.5亿元，高精密模具材料",
     "chain_ids": [3, 5]},
    {"name": "佛山市高明区振野海绵制品有限公司", "industry": "新材料", "sub_industry": "聚氨酯海绵",
     "chain_stage": "中游", "scale": "中小微", "revenue_annual": 1, "employee_count": 80,
     "source": "2025年签约", "description": "振野海绵智造中心基地项目，投资1亿元，聚氨酯海绵制品",
     "chain_ids": [5]},

    # ── 新型电力系统装备 ──
    {"name": "安恒智能科技有限公司", "industry": "电力装备", "sub_industry": "智能输配电",
     "chain_stage": "中游", "scale": "大型", "revenue_annual": 20, "employee_count": 1000,
     "source": "高明区重点骨干企业", "description": "智能输配电控制设备领军企业，高明区智能输配电控制设备产业集群入选2025年广东省中小企业特色产业集群（涵盖125家企业，总产值129亿元）",
     "chain_ids": [9]},
    {"name": "广东浩城电气有限公司", "industry": "电力装备", "sub_industry": "智能电气设备",
     "chain_stage": "中游", "scale": "大型", "revenue_annual": 8, "employee_count": 400,
     "source": "2025年投产", "description": "浩城科技园（智能电气设备总部基地），投资9亿元，2025年7月落成",
     "chain_ids": [9]},
    {"name": "广东尚高电气有限公司", "industry": "电力装备", "sub_industry": "变压器",
     "chain_stage": "中游", "scale": "中型", "revenue_annual": 5, "employee_count": 300,
     "source": "2025年投产", "description": "尚高电气新能效变压器智造基地，预计年产值5亿元，2025年内投产",
     "chain_ids": [9]},
    {"name": "佛山万马响光电科技有限公司", "industry": "电力装备", "sub_industry": "电力设备制造",
     "chain_stage": "中游", "scale": "大型", "revenue_annual": 10, "employee_count": 500,
     "source": "2025年签约", "description": "万马（佛山）高端智能电力装备智造基地项目，投资10亿元，电力设备制造集群",
     "chain_ids": [9]},
    {"name": "广东德光变压器有限公司", "industry": "电力装备", "sub_industry": "新能源变压器",
     "chain_stage": "中游", "scale": "中型", "revenue_annual": 3, "employee_count": 200,
     "source": "2025年签约", "description": "德光电力新能源设备智能制造中心项目，投资2.1亿元，新能源变压器",
     "chain_ids": [9]},
    {"name": "天亿电气有限公司", "industry": "电力装备", "sub_industry": "电力设备",
     "chain_stage": "中游", "scale": "中型", "revenue_annual": 4, "employee_count": 250,
     "source": "高明区重点骨干企业", "description": "高明区电力设备制造重点企业",
     "chain_ids": [9]},
    {"name": "广东佛锐电气有限公司", "industry": "电力装备", "sub_industry": "电气机械",
     "chain_stage": "中游", "scale": "中小微", "revenue_annual": 1.5, "employee_count": 100,
     "source": "2025年签约", "description": "佛锐电气智能科技生产基地总部，投资1.5亿元，电气机械制造",
     "chain_ids": [3, 9]},

    # ── 智能家居 ──
    {"name": "广东度高家具有限公司", "industry": "智能家居", "sub_industry": "高端酒店家具",
     "chain_stage": "中游", "scale": "中型", "revenue_annual": 3, "employee_count": 200,
     "source": "2025年动工", "description": "广东度泽智能科技有限公司项目，投资4亿元，高端酒店家具智能制造，位于专精特新湾，预计2025年底投产",
     "chain_ids": [8]},
    {"name": "芬伦家具", "industry": "智能家居", "sub_industry": "办公家具",
     "chain_stage": "中游", "scale": "中型", "revenue_annual": 3, "employee_count": 200,
     "source": "2025年增资扩产", "description": "芬伦智能办公产业总部基地项目，投资5亿元（增资扩产）",
     "chain_ids": [8]},
    {"name": "欧丽家具", "industry": "智能家居", "sub_industry": "办公家具",
     "chain_stage": "中游", "scale": "中小微", "revenue_annual": 1, "employee_count": 80,
     "source": "2025年签约", "description": "欧丽智能商务空间研发总部基地项目，投资1亿元，办公休闲椅、沙发制造",
     "chain_ids": [8]},
    {"name": "万怡科技（佛山）有限公司", "industry": "智能家居", "sub_industry": "智能小家电",
     "chain_stage": "中游", "scale": "中型", "revenue_annual": 2, "employee_count": 150,
     "source": "2025年签约", "description": "环球互联智能电器制造基地高明项目，投资4亿元，智能小家电制造",
     "chain_ids": [8]},
    {"name": "佛山市崇雅家具有限公司", "industry": "智能家居", "sub_industry": "家具制造",
     "chain_stage": "中游", "scale": "中型", "revenue_annual": 3, "employee_count": 250,
     "source": "佛山高新区2024年度创新积分A类榜单", "description": "入选佛山高新区2024年度创新积分A类榜单，高明区重点家具企业",
     "chain_ids": [8]},
    {"name": "曼柯办公家具", "industry": "智能家居", "sub_industry": "智能办公家具",
     "chain_stage": "中游", "scale": "中型", "revenue_annual": 3, "employee_count": 200,
     "source": "2025年签约", "description": "曼柯办公空间智造总部项目，投资5亿元，智能办公产业总部",
     "chain_ids": [8]},

    # ── 食品饮料 ──
    {"name": "海天醋业（广东）有限公司", "industry": "食品饮料", "sub_industry": "调味品",
     "chain_stage": "中游", "scale": "大型", "revenue_annual": 20, "employee_count": 500,
     "source": "佛山高新区2024年度创新积分A类榜单", "description": "海天味业子公司，入选佛山高新区2024年度创新积分A类榜单",
     "chain_ids": [4]},
    {"name": "鲜之然（广东）生物技术有限公司", "industry": "食品饮料", "sub_industry": "生物技术/食品",
     "chain_stage": "下游", "scale": "中型", "revenue_annual": 2, "employee_count": 150,
     "source": "佛山高新区2024年度创新积分A类榜单", "description": "生物技术/食品企业，入选佛山高新区2024年度创新积分A类榜单",
     "chain_ids": [4]},
    {"name": "佛山高峰淀粉科技有限公司", "industry": "食品饮料", "sub_industry": "淀粉制品",
     "chain_stage": "中游", "scale": "中型", "revenue_annual": 3, "employee_count": 150,
     "source": "2025年投产", "description": "高峰高效淀粉及淀粉制品制备技术项目，变性淀粉领域，2025年7月投产",
     "chain_ids": [4]},
    {"name": "信豚生物", "industry": "食品饮料", "sub_industry": "生物技术/饲料",
     "chain_stage": "下游", "scale": "中小微", "revenue_annual": 1.5, "employee_count": 80,
     "source": "2025年签约", "description": "信豚生物总部项目，已安装生产线",
     "chain_ids": [4]},

    # ── 现代物流 ──
    {"name": "广东嘉溢智慧物流中心", "industry": "现代物流", "sub_industry": "智慧物流",
     "chain_stage": "下游", "scale": "大型", "revenue_annual": 8, "employee_count": 300,
     "source": "2025年签约", "description": "嘉里物流与溢达集团合资，投资3.7亿元，智慧物流体系，2025年6月投产",
     "chain_ids": [6]},
    {"name": "中策空港智链枢纽港", "industry": "现代物流", "sub_industry": "空港供应链",
     "chain_stage": "下游", "scale": "大型", "revenue_annual": 6, "employee_count": 250,
     "source": "2025年增资扩产", "description": "中策空港智链枢纽港项目，投资15亿元（增资扩产），空港供应链枢纽",
     "chain_ids": [6]},

    # ── 陶瓷建材 ──
    {"name": "佛山市高明安华陶瓷洁具有限公司", "industry": "陶瓷建材", "sub_industry": "陶瓷卫浴",
     "chain_stage": "中游", "scale": "大型", "revenue_annual": 10, "employee_count": 800,
     "source": "佛山高新区2024年度知识产权密集型企业", "description": "荣获2024年佛山高新区知识产权密集型企业牌匾，入选2024年度创新积分A类榜单",
     "chain_ids": [2]},

    # ── 新兴/交叉产业 ──
    {"name": "佛山市佰泰汽车用品有限公司", "industry": "装备制造", "sub_industry": "汽车用品",
     "chain_stage": "中游", "scale": "中型", "revenue_annual": 3, "employee_count": 200,
     "source": "2025年动工", "description": "佰泰汽车用品生产基地高明项目，投资2.5亿元，皮卡尾箱盖制造，预计2026年6月投产",
     "chain_ids": [3]},
    {"name": "耀龙集团", "industry": "装备制造", "sub_industry": "金属智造",
     "chain_stage": "中游", "scale": "中型", "revenue_annual": 5, "employee_count": 300,
     "source": "2025年动工", "description": "耀龙高端金属智造及智能设备生产基地，投资5亿元，位于明城镇",
     "chain_ids": [3]},
    {"name": "新绿色药业", "industry": "食品饮料", "sub_industry": "中药制造",
     "chain_stage": "中游", "scale": "中型", "revenue_annual": 5, "employee_count": 300,
     "source": "2025年签约", "description": "新绿色现代中药华南总部基地项目，中药生产基地，预计2025年内投产",
     "chain_ids": [4]},
    {"name": "广东柯维环境科技", "industry": "装备制造", "sub_industry": "环保装备",
     "chain_stage": "下游", "scale": "中小微", "revenue_annual": 2, "employee_count": 100,
     "source": "2025年投产", "description": "柯维环境科技紫外高效消毒项目，年产值约2亿元",
     "chain_ids": [3]},
    {"name": "佛山市智荟蓝天环保科技有限公司", "industry": "装备制造", "sub_industry": "环保装备",
     "chain_stage": "下游", "scale": "中型", "revenue_annual": 2.5, "employee_count": 150,
     "source": "2025年增资扩产", "description": "智荟蓝天增资扩产项目，投资2.5亿元，环保装备制造",
     "chain_ids": [3]},
]

NEW_INVESTMENTS = [
    {"enterprise_name": "索斯科锁定技术（佛山）有限公司", "industry": "装备制造", "chain_id": 3,
     "amount": 7.2, "stage": "已投产", "source": "佛山市高明区招商局",
     "announced_date": "2025-09", "description": "全球锁具领军企业索斯科佛山新厂开业，总投资1亿美元（约7.2亿元）"},
    {"enterprise_name": "广东远华新材料股份有限公司", "industry": "新材料", "chain_id": 5,
     "amount": 25, "stage": "在建", "source": "高明区重点建设项目",
     "announced_date": "2025-01", "description": "广东远华新材料产业园，增资扩产项目，国内一流材料产业园"},
    {"enterprise_name": "广东豪斯特汽车零部件有限公司", "industry": "装备制造", "chain_id": 3,
     "amount": 20, "stage": "在建", "source": "政府公开信息",
     "announced_date": "2024-06", "description": "豪斯特高端汽车零部件及电池包壳体项目"},
    {"enterprise_name": "佛山市高明亿阳塑胶有限公司", "industry": "新材料", "chain_id": 5,
     "amount": 10, "stage": "已签约", "source": "2025年招商项目",
     "announced_date": "2025-06", "description": "亿阳塑胶高分子新材料研发生产基地"},
    {"enterprise_name": "广东浩城电气有限公司", "industry": "电力装备", "chain_id": 9,
     "amount": 9, "stage": "已投产", "source": "政府公开信息",
     "announced_date": "2025-07", "description": "浩城科技园（智能电气设备总部基地）落成"},
    {"enterprise_name": "佛山万马响光电科技有限公司", "industry": "电力装备", "chain_id": 9,
     "amount": 10, "stage": "已签约", "source": "2025年招商项目",
     "announced_date": "2025-06", "description": "万马（佛山）高端智能电力装备智造基地项目"},
    {"enterprise_name": "广东晟阳节能玻璃有限公司", "industry": "新材料", "chain_id": 5,
     "amount": 8, "stage": "在建", "source": "政府公开信息",
     "announced_date": "2024-11", "description": "广东晟阳节能新材料制造（总部）项目"},
    {"enterprise_name": "曼柯办公家具", "industry": "智能家居", "chain_id": 8,
     "amount": 5, "stage": "已签约", "source": "2025年招商项目",
     "announced_date": "2025-07", "description": "曼柯办公空间智造总部项目"},
    {"enterprise_name": "广东度高家具有限公司", "industry": "智能家居", "chain_id": 8,
     "amount": 4, "stage": "在建", "source": "政府公开信息",
     "announced_date": "2025-07", "description": "广东度泽智能科技有限公司项目，高端酒店家具智能制造"},
    {"enterprise_name": "芬伦家具", "industry": "智能家居", "chain_id": 8,
     "amount": 5, "stage": "在建", "source": "2025年增资扩产",
     "announced_date": "2025-06", "description": "芬伦智能办公产业总部基地项目（增资扩产）"},
    {"enterprise_name": "佛山市中盈重工有限公司", "industry": "装备制造", "chain_id": 3,
     "amount": 5, "stage": "已签约", "source": "2025年招商项目",
     "announced_date": "2025-06", "description": "中盈船舶装备制造基地项目"},
    {"enterprise_name": "耀龙集团", "industry": "装备制造", "chain_id": 3,
     "amount": 5, "stage": "在建", "source": "政府公开信息",
     "announced_date": "2025-03", "description": "耀龙高端金属智造及智能设备生产基地"},
    {"enterprise_name": "佛山市佰泰汽车用品有限公司", "industry": "装备制造", "chain_id": 3,
     "amount": 2.5, "stage": "在建", "source": "政府公开信息",
     "announced_date": "2025-07", "description": "佰泰汽车用品生产基地高明项目"},
    {"enterprise_name": "广东嘉溢智慧物流中心", "industry": "现代物流", "chain_id": 6,
     "amount": 3.7, "stage": "已投产", "source": "政府公开信息",
     "announced_date": "2025-06", "description": "嘉里物流与溢达集团合资智慧物流中心"},
    {"enterprise_name": "中策空港智链枢纽港", "industry": "现代物流", "chain_id": 6,
     "amount": 15, "stage": "在建", "source": "2025年增资扩产",
     "announced_date": "2025-06", "description": "中策空港智链枢纽港项目（增资扩产）"},
    {"enterprise_name": "安恒智能科技有限公司", "industry": "电力装备", "chain_id": 9,
     "amount": 30, "stage": "已投产", "source": "高明区重点骨干企业",
     "announced_date": "2024-01", "description": "安恒智能科技，智能输配电控制设备产业集群龙头"},
    {"enterprise_name": "新启航半导体有限公司", "industry": "电子信息", "chain_id": 7,
     "amount": 5, "stage": "已投产", "source": "中国IC独角兽榜单",
     "announced_date": "2024-01", "description": "佛山唯一中国IC独角兽企业，超快激光微纳加工"},
]

NEW_INFRASTRUCTURE = [
    {"name": "专精特新湾产业园", "infra_type": "产业园", "status": "已运营",
     "description": "高明区专精特新湾，已落地企业35家，总投资超147亿元，集聚高端装备、新材料等专精特新企业",
     "impact_areas": '["装备制造","新材料","智能家居"]', "planned_completion": "", "source": "政府公开信息"},
    {"name": "高明（荷城）万洋众创城", "infra_type": "产业园", "status": "在建",
     "description": "万洋集团投资20亿元建设，中国民企500强，荷城街道产业平台",
     "impact_areas": '["装备制造","智能家居","电子信息"]', "planned_completion": "2027", "source": "2025年动工"},
]


def update_database():
    """更新数据库，添加新企业和投资数据"""
    print("=" * 60)
    print("📦 新增企业数据...")
    print("=" * 60)

    added = 0
    skipped = 0
    for ent in NEW_ENTERPRISES:
        chain_ids = ent.pop("chain_ids")
        name = ent["name"]

        # Use single connection for the entire enterprise insert + chain relations
        with get_conn() as conn:
            existing = conn.execute("SELECT id FROM enterprises WHERE name=:name", {"name": name}).fetchone()
            if existing:
                print(f"  ⏭️  已存在: {name}")
                skipped += 1
                ent["chain_ids"] = chain_ids
                continue

            # Direct insert
            sql = """INSERT INTO enterprises
                (name,industry,sub_industry,chain_stage,scale,revenue_annual,employee_count,address,source,description)
                VALUES (:name,:industry,:sub_industry,:chain_stage,:scale,:revenue_annual,:employee_count,:address,:source,:description)"""
            ent.setdefault("address", "")
            cur = conn.execute(sql, ent)
            eid = cur.lastrowid

            if eid:
                for cid in chain_ids:
                    conn.execute("INSERT OR IGNORE INTO chain_relations (enterprise_id, chain_id, role) VALUES (?,?,?)",
                                 (eid, cid, "配套"))
                print(f"  ✅ 新增: {name} (行业: {ent['industry']}, 营收: {ent['revenue_annual']}亿)")
                added += 1
            else:
                print(f"  ❌ 失败: {name}")
        ent["chain_ids"] = chain_ids

    print(f"\n📊 新增企业: {added} 家, 已存在跳过: {skipped} 家")

    # ── 新增投资信息 ──
    print(f"\n{'=' * 60}")
    print("💰 新增投资信息...")
    print("=" * 60)
    inv_added = 0
    for inv in NEW_INVESTMENTS:
        with get_conn() as conn:
            existing = conn.execute("SELECT id FROM investments WHERE enterprise_name=:name AND amount=:amt",
                                     {"name": inv["enterprise_name"], "amt": inv["amount"]}).fetchone()
            if existing:
                print(f"  ⏭️  已存在: {inv['enterprise_name']} ({inv['amount']}亿)")
                continue
            inv.setdefault("industry",""); inv.setdefault("chain_id",0)
            inv.setdefault("stage","已签约"); inv.setdefault("source",""); inv.setdefault("announced_date","")
            inv.setdefault("description","")
            conn.execute("""INSERT INTO investments (enterprise_name,industry,chain_id,amount,stage,source,announced_date,description)
                VALUES (:enterprise_name,:industry,:chain_id,:amount,:stage,:source,:announced_date,:description)""", inv)
            print(f"  ✅ 新增投资: {inv['enterprise_name']} ({inv['amount']}亿, {inv['stage']})")
            inv_added += 1
    print(f"\n📊 新增投资: {inv_added} 条")

    # ── 新增基建信息 ──
    print(f"\n{'=' * 60}")
    print("🏗️  新增基础设施...")
    print("=" * 60)
    infra_added = 0
    for inf in NEW_INFRASTRUCTURE:
        with get_conn() as conn:
            existing = conn.execute("SELECT id FROM infrastructure WHERE name=:name", {"name": inf["name"]}).fetchone()
            if existing:
                print(f"  ⏭️  已存在: {inf['name']}")
                continue
            inf.setdefault("status","规划中"); inf.setdefault("description",""); inf.setdefault("impact_areas","[]")
            inf.setdefault("planned_completion",""); inf.setdefault("source","")
            conn.execute("""INSERT INTO infrastructure (name,infra_type,status,description,impact_areas,planned_completion,source)
                VALUES (:name,:infra_type,:status,:description,:impact_areas,:planned_completion,:source)""", inf)
            print(f"  ✅ 新增基建: {inf['name']}")
            infra_added += 1
    print(f"\n📊 新增基建: {infra_added} 条")

    # ── 最终统计 ──
    print(f"\n{'=' * 60}")
    print("📈 更新后数据统计")
    print("=" * 60)
    with get_conn() as conn:
        ent_count = conn.execute("SELECT COUNT(*) as c FROM enterprises").fetchone()['c']
        inv_count = conn.execute("SELECT COUNT(*) as c FROM investments").fetchone()['c']
        infra_count = conn.execute("SELECT COUNT(*) as c FROM infrastructure").fetchone()['c']
        chain_rel = conn.execute("SELECT COUNT(*) as c FROM chain_relations").fetchone()['c']
        total_rev = conn.execute("SELECT SUM(revenue_annual) as s FROM enterprises").fetchone()['s'] or 0

    print(f"  企业: {ent_count} 家 (总营收 {total_rev:.1f} 亿)")
    print(f"  产业链关系: {chain_rel} 条")
    print(f"  招商项目: {inv_count} 个")
    print(f"  基础设施: {infra_count} 项")


if __name__ == "__main__":
    update_database()
