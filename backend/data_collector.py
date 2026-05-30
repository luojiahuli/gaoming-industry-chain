"""数据采集模块 - 高明区企业数据 + 招商新闻 + 基建信息
基于2026年真实公开数据整理
"""
import os, sys, json, requests
from datetime import datetime
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(__file__))
from database import *

# ═══════════════════════════════════════════════════════════
# 高明区企业数据库 (基于2026年公开信息)
# ═══════════════════════════════════════════════════════════
GAOMING_ENTERPRISES = [
    # ── 纺织服装产业链 ──
    {"name":"广东溢达纺织有限公司","industry":"纺织服装","sub_industry":"高档棉纺织","chain_stage":"中游","scale":"大型","revenue_annual":85,"employee_count":12000,"address":"高明区荷城街道","source":"公开信息"},
    {"name":"佛山高丰纺织有限公司","industry":"纺织服装","sub_industry":"面料织造","chain_stage":"中游","scale":"中型","revenue_annual":8,"employee_count":800,"address":"高明区荷城","source":"公开信息"},
    {"name":"佛山市高明区合丰纺织有限公司","industry":"纺织服装","sub_industry":"印染整理","chain_stage":"中游","scale":"中型","revenue_annual":5,"employee_count":400,"address":"高明区杨和镇","source":"公开信息"},
    {"name":"佛山市高明区德润纺织有限公司","industry":"纺织服装","sub_industry":"牛仔布制造","chain_stage":"中游","scale":"中型","revenue_annual":6,"employee_count":500,"address":"高明区荷城","source":"公开信息"},
    {"name":"广东东润纺织有限公司","industry":"纺织服装","sub_industry":"化纤织造","chain_stage":"上游","scale":"中型","revenue_annual":7,"employee_count":600,"address":"高明区更合镇","source":"公开信息"},
    {"name":"湾区云裳生态谷（高明）","industry":"纺织服装","sub_industry":"零碳智造服装","chain_stage":"下游","scale":"大型","revenue_annual":20,"employee_count":3000,"address":"高明区荷城","source":"2026年集中签约"},

    # ── 陶瓷建材产业链 ──
    {"name":"广东新明珠陶瓷集团有限公司","industry":"陶瓷建材","sub_industry":"建筑陶瓷","chain_stage":"中游","scale":"大型","revenue_annual":120,"employee_count":15000,"address":"高明区明城镇","source":"公开信息"},
    {"name":"佛山高明顺成陶瓷有限公司","industry":"陶瓷建材","sub_industry":"建筑陶瓷","chain_stage":"中游","scale":"大型","revenue_annual":40,"employee_count":4000,"address":"高明区明城镇","source":"公开信息"},
    {"name":"佛山市高明区新粤丰陶瓷有限公司","industry":"陶瓷建材","sub_industry":"釉面砖","chain_stage":"中游","scale":"中型","revenue_annual":15,"employee_count":1500,"address":"高明区杨和镇","source":"公开信息"},
    {"name":"佛山高明贝斯特陶瓷有限公司","industry":"陶瓷建材","sub_industry":"陶瓷薄板","chain_stage":"中游","scale":"中型","revenue_annual":10,"employee_count":1200,"address":"高明区明城镇","source":"公开信息"},
    {"name":"佛山市高明区圣晖陶瓷有限公司","industry":"陶瓷建材","sub_industry":"抛光砖","chain_stage":"中游","scale":"中型","revenue_annual":8,"employee_count":800,"address":"高明区更合镇","source":"公开信息"},
    {"name":"广东特地陶瓷有限公司","industry":"陶瓷建材","sub_industry":"功能陶瓷","chain_stage":"中游","scale":"中型","revenue_annual":12,"employee_count":1000,"address":"高明区明城镇","source":"公开信息"},
    {"name":"佛山高明顺成陶瓷绿色智能生产线","industry":"陶瓷建材","sub_industry":"绿色智能陶瓷","chain_stage":"上游","scale":"大型","revenue_annual":25,"employee_count":2000,"address":"高明区明城镇","source":"2025年技改"},

    # ── 装备制造/新型电力系统 ──
    {"name":"佛山市高明区万和电气有限公司","industry":"装备制造","sub_industry":"燃气具/家电","chain_stage":"中游","scale":"大型","revenue_annual":60,"employee_count":5000,"address":"高明区杨和镇","source":"公开信息"},
    {"name":"佛山高明中油燃气有限公司","industry":"装备制造","sub_industry":"燃气设备","chain_stage":"中游","scale":"中型","revenue_annual":10,"employee_count":300,"address":"高明区荷城","source":"公开信息"},
    {"name":"佛山市高明区高达重工有限公司","industry":"装备制造","sub_industry":"钢结构/重型机械","chain_stage":"上游","scale":"中型","revenue_annual":8,"employee_count":600,"address":"高明区更合镇","source":"公开信息"},
    {"name":"佛山高明科力机械有限公司","industry":"装备制造","sub_industry":"纺织机械","chain_stage":"上游","scale":"中型","revenue_annual":5,"employee_count":400,"address":"高明区荷城","source":"公开信息"},
    {"name":"广东双兴新材料集团","industry":"装备制造","sub_industry":"不锈钢管材","chain_stage":"上游","scale":"大型","revenue_annual":30,"employee_count":2500,"address":"高明区杨和镇","source":"公开信息"},
    {"name":"广东天元智造高明智能装备基地","industry":"装备制造","sub_industry":"智能装备","chain_stage":"中游","scale":"大型","revenue_annual":20,"employee_count":1500,"address":"高明区更合镇","source":"2026年在建"},
    {"name":"富成精密科技生产总部","industry":"装备制造","sub_industry":"铝合金/镁合金精密压铸","chain_stage":"上游","scale":"大型","revenue_annual":15,"employee_count":2000,"address":"高明区杨和镇","source":"2026年签约"},
    {"name":"臻壕垣机械设备智造项目","industry":"装备制造","sub_industry":"激光切割/高端装备","chain_stage":"上游","scale":"中型","revenue_annual":8,"employee_count":800,"address":"高明区明城镇","source":"2026年签约"},
    {"name":"振鸿金属制品生产制造基地","industry":"装备制造","sub_industry":"高端钢管/金属制品","chain_stage":"上游","scale":"大型","revenue_annual":35,"employee_count":3000,"address":"高明区更合镇","source":"2026年签约"},

    # ── 食品饮料产业链 ──
    {"name":"佛山海天味业(高明)有限公司","industry":"食品饮料","sub_industry":"调味品","chain_stage":"中游","scale":"特大型","revenue_annual":200,"employee_count":8000,"address":"高明区荷城街道","source":"公开信息"},
    {"name":"广东华兴玻璃(高明)有限公司","industry":"食品饮料","sub_industry":"玻璃包装","chain_stage":"上游","scale":"大型","revenue_annual":25,"employee_count":3000,"address":"高明区明城镇","source":"公开信息"},
    {"name":"佛山市高明区金荣华食品有限公司","industry":"食品饮料","sub_industry":"肉制品加工","chain_stage":"中游","scale":"中型","revenue_annual":5,"employee_count":300,"address":"高明区更合镇","source":"公开信息"},
    {"name":"佛山高明区佳佳食品有限公司","industry":"食品饮料","sub_industry":"速冻食品","chain_stage":"中游","scale":"小型","revenue_annual":2,"employee_count":150,"address":"高明区杨和镇","source":"公开信息"},
    {"name":"佛山市高明区碧露矿泉水有限公司","industry":"食品饮料","sub_industry":"饮用水","chain_stage":"中游","scale":"小型","revenue_annual":1.5,"employee_count":100,"address":"高明区明城镇","source":"公开信息"},

    # ── 新材料产业链 ──
    {"name":"佛山高明顺晟新材料有限公司","industry":"新材料","sub_industry":"高分子材料","chain_stage":"上游","scale":"中型","revenue_annual":8,"employee_count":500,"address":"高明区杨和镇","source":"公开信息"},
    {"name":"广东炜林纳新材料科技股份有限公司","industry":"新材料","sub_industry":"稀土功能材料","chain_stage":"上游","scale":"中型","revenue_annual":6,"employee_count":400,"address":"高明区更合镇","source":"公开信息"},
    {"name":"佛山市高明区欣明新材料有限公司","industry":"新材料","sub_industry":"环保建材","chain_stage":"上游","scale":"中型","revenue_annual":4,"employee_count":300,"address":"高明区明城镇","source":"公开信息"},
    {"name":"上海均和集团高明新材料基地","industry":"新材料","sub_industry":"高性能复合材料","chain_stage":"上游","scale":"大型","revenue_annual":12,"employee_count":1000,"address":"高明区更合镇","source":"2025年签约"},
    {"name":"佛山仙湖实验室高明氢能中试基地","industry":"新材料","sub_industry":"氢能材料","chain_stage":"上游","scale":"中型","revenue_annual":5,"employee_count":500,"address":"高明区杨和镇","source":"2025年开工"},

    # ── 现代物流/临空经济 ──
    {"name":"佛山高明港货运有限公司","industry":"现代物流","sub_industry":"港口物流","chain_stage":"下游","scale":"中型","revenue_annual":3,"employee_count":200,"address":"高明区荷城","source":"公开信息"},
    {"name":"佛山高明区顺丰速运分拨中心","industry":"现代物流","sub_industry":"快递分拨","chain_stage":"下游","scale":"中型","revenue_annual":2,"employee_count":500,"address":"高明区荷城","source":"公开信息"},
    {"name":"佛山高明顺高物流有限公司","industry":"现代物流","sub_industry":"货运物流","chain_stage":"下游","scale":"小型","revenue_annual":1,"employee_count":100,"address":"高明区杨和镇","source":"公开信息"},
    {"name":"宜家供应链华南区分拨中心","industry":"现代物流","sub_industry":"家居物流","chain_stage":"下游","scale":"大型","revenue_annual":10,"employee_count":800,"address":"高明区荷城","source":"2022年投产"},
    {"name":"安博物流高明园区","industry":"现代物流","sub_industry":"仓储物流","chain_stage":"下游","scale":"大型","revenue_annual":5,"employee_count":300,"address":"高明区更合镇","source":"2025年开工"},
    {"name":"顺丰智慧物流高明枢纽","industry":"现代物流","sub_industry":"智慧物流枢纽","chain_stage":"下游","scale":"大型","revenue_annual":15,"employee_count":1500,"address":"高明区荷城","source":"2024年投产"},
    {"name":"京东物流高明智能仓","industry":"现代物流","sub_industry":"智能仓储","chain_stage":"下游","scale":"中型","revenue_annual":4,"employee_count":400,"address":"高明区明城镇","source":"2026年在建"},
    {"name":"巴夫洛·佛山高明智慧供应链产业园","industry":"现代物流","sub_industry":"智慧供应链","chain_stage":"下游","scale":"大型","revenue_annual":8,"employee_count":600,"address":"高明区更合镇","source":"2026年签约"},

    # ── 电子信息/数字经济 ──
    {"name":"佛山高明德健电子有限公司","industry":"电子信息","sub_industry":"电子元件","chain_stage":"中游","scale":"中型","revenue_annual":5,"employee_count":600,"address":"高明区荷城","source":"公开信息"},
    {"name":"佛山市高明区精电电子有限公司","industry":"电子信息","sub_industry":"线路板","chain_stage":"中游","scale":"小型","revenue_annual":3,"employee_count":300,"address":"高明区杨和镇","source":"公开信息"},
    {"name":"润泽（佛山）国际信息港（一期）","industry":"电子信息","sub_industry":"智算中心/AI算力","chain_stage":"中游","scale":"大型","revenue_annual":20,"employee_count":1000,"address":"高明区更合镇","source":"2025年投产"},
    {"name":"润泽（佛山）国际信息港（二期）","industry":"电子信息","sub_industry":"智算中心/AI算力","chain_stage":"中游","scale":"大型","revenue_annual":30,"employee_count":1500,"address":"高明区更合镇","source":"2026年签约"},
    {"name":"广州无线电集团(高明)智能制造基地","industry":"电子信息","sub_industry":"工业物联网","chain_stage":"中游","scale":"中型","revenue_annual":8,"employee_count":600,"address":"高明区更合镇","source":"2025年签约"},

    # ── 新型电力系统装备 ──
    {"name":"南网战新（佛山）新动能产业基地","industry":"电力装备","sub_industry":"新型电力系统","chain_stage":"中游","scale":"大型","revenue_annual":15,"employee_count":2000,"address":"高明区杨和镇","source":"2026年签约"},

    # ── 智能家居 ──
    {"name":"甜秘密高端智能家居生产基地（高明）","industry":"智能家居","sub_industry":"智能家居制造","chain_stage":"中游","scale":"中型","revenue_annual":10,"employee_count":1500,"address":"高明区更合镇","source":"2026年签约二期"},
    {"name":"圃美多（佛山）食品有限公司","industry":"食品饮料","sub_industry":"豆制品/健康食品","chain_stage":"中游","scale":"中型","revenue_annual":8,"employee_count":500,"address":"高明区杨和镇","source":"2026年签约"},
    {"name":"高咖（广东）农业科技发展有限公司","industry":"食品饮料","sub_industry":"咖啡生豆加工","chain_stage":"上游","scale":"小型","revenue_annual":3,"employee_count":200,"address":"高明区荷城","source":"2026年投产"},
    {"name":"浙天智能家居生产制造总部基地","industry":"智能家居","sub_industry":"智能安防锁具","chain_stage":"中游","scale":"中型","revenue_annual":5,"employee_count":600,"address":"高明区更合镇","source":"2026年签约"},
    {"name":"沛国智慧健康办公装备制造项目","industry":"智能家居","sub_industry":"智能升降办公桌","chain_stage":"中游","scale":"中型","revenue_annual":4,"employee_count":400,"address":"高明区更合镇","source":"2026年签约"},
    {"name":"金通佰利智能家具工业4.0生产基地","industry":"智能家居","sub_industry":"高端定制家具","chain_stage":"中游","scale":"中型","revenue_annual":3,"employee_count":300,"address":"高明区更合镇","source":"2026年签约"},
    {"name":"深国际·高明先进制造与空港供应链中心","industry":"现代物流","sub_industry":"空港供应链","chain_stage":"下游","scale":"大型","revenue_annual":12,"employee_count":800,"address":"高明区更合镇","source":"2026年签约"},
]

# ═══════════════════════════════════════════════════════════
# 产业链定义 (2026年高明区重点产业链)
# ═══════════════════════════════════════════════════════════
INDUSTRY_CHAINS = [
    {
        "chain_name":"纺织服装产业链",
        "category":"传统优势",
        "description":"高明区传统支柱产业，以溢达纺织为龙头。2026年引入湾区云裳生态谷，打造零碳智造纺织服装产业集群",
        "surrounding_cities": json.dumps([
            {"city":"广州","role":"面料市场、设计研发","distance":"60km"},
            {"city":"佛山禅城","role":"服装批发市场","distance":"30km"},
            {"city":"东莞","role":"服装制造配套","distance":"90km"}
        ])
    },
    {
        "chain_name":"陶瓷建材产业链",
        "category":"传统优势",
        "description":"以新明珠、顺成陶瓷为龙头，高明作为佛山陶瓷重要生产基地，正全面转型绿色智能陶瓷",
        "surrounding_cities": json.dumps([
            {"city":"佛山禅城","role":"陶瓷总部/研发/展览","distance":"30km"},
            {"city":"佛山南海","role":"陶瓷装备制造","distance":"25km"},
            {"city":"肇庆","role":"陶瓷原料供应","distance":"40km"}
        ])
    },
    {
        "chain_name":"装备制造/新型电力系统",
        "category":"重点培育",
        "description":"2026年核心发展方向，以万和电气、天元智造、富成精密、振鸿金属为龙头，配套南网战新基金，打造新型电力系统装备集群",
        "surrounding_cities": json.dumps([
            {"city":"佛山顺德","role":"家电/电力装备产业协同","distance":"40km"},
            {"city":"广州","role":"电力系统研发、车企配套","distance":"60km"},
            {"city":"佛山南海","role":"机械装备配套","distance":"30km"}
        ])
    },
    {
        "chain_name":"食品饮料产业链",
        "category":"支柱产业",
        "description":"海天味业全球最大调味品企业，带动包装、冷链、物流全链条发展",
        "surrounding_cities": json.dumps([
            {"city":"佛山三水","role":"食品饮料产业集聚","distance":"35km"},
            {"city":"广州","role":"食品消费市场","distance":"60km"}
        ])
    },
    {
        "chain_name":"新材料/氢能产业链",
        "category":"新兴培育",
        "description":"发展高分子材料、氢能材料、高性能复合材料，仙湖实验室氢能中试基地+均和新材料基地双轮驱动",
        "surrounding_cities": json.dumps([
            {"city":"佛山南海","role":"新材料研发平台、仙湖实验室本部","distance":"25km"},
            {"city":"广州","role":"高校科研资源","distance":"60km"},
            {"city":"肇庆","role":"矿产原材料供应","distance":"40km"}
        ])
    },
    {
        "chain_name":"现代物流/临空经济",
        "category":"重点培育",
        "description":"依托广州新机场（2026年3月动工）+广湛高铁（2025年底通车）+西江黄金水道，打造临空临港物流产业集群",
        "surrounding_cities": json.dumps([
            {"city":"广州","role":"白云机场国际航线+新机场互补","distance":"60km"},
            {"city":"佛山南海","role":"区域物流枢纽协同","distance":"25km"},
            {"city":"珠海","role":"珠肇高铁空港-海港联动","distance":"120km"},
            {"city":"肇庆","role":"西江上游货运","distance":"40km"}
        ])
    },
    {
        "chain_name":"电子信息/数字经济",
        "category":"新兴培育",
        "description":"润泽科技百亿级智算中心+广州无线电集团智能制造基地，打造大湾区西翼算力枢纽",
        "surrounding_cities": json.dumps([
            {"city":"广州","role":"软件信息服务、数字产业","distance":"60km"},
            {"city":"深圳","role":"电子信息产业高地","distance":"120km"},
            {"city":"东莞","role":"电子信息制造配套","distance":"90km"}
        ])
    },
    {
        "chain_name":"智能家居产业链",
        "category":"新兴培育",
        "description":"甜秘密高端智能家居生产基地引领，承接顺德家电产业外溢",
        "surrounding_cities": json.dumps([
            {"city":"佛山顺德","role":"家电产业外溢承接","distance":"40km"},
            {"city":"佛山南海","role":"智能家居配套","distance":"30km"}
        ])
    },
    {
        "chain_name":"新型电力系统装备产业链",
        "category":"重点培育",
        "description":"2026年重点打造，依托南网战新基金（5亿元）+安昇基金（50亿元），聚焦新型电力装备全链条",
        "surrounding_cities": json.dumps([
            {"city":"广州","role":"南方电网总部、电力研发","distance":"60km"},
            {"city":"佛山顺德","role":"电力设备制造配套","distance":"40km"},
            {"city":"佛山南海","role":"新能源产业协同","distance":"25km"}
        ])
    },
]

# ═══════════════════════════════════════════════════════════
# 招商引资已落实企业 (2026年真实数据)
# ═══════════════════════════════════════════════════════════
INVESTMENTS = [
    # 2026年高质量发展大会签约项目 (34个, 总计230+亿)
    {"enterprise_name":"润泽（佛山）国际信息港二期","industry":"电子信息","chain_id":7,"amount":20,"stage":"已签约","source":"2026年高质量发展大会","announced_date":"2026-02","description":"百亿级智算中心二期，打造大湾区AI算力枢纽"},
    {"enterprise_name":"振鸿金属制品生产制造基地","industry":"装备制造","chain_id":3,"amount":25,"stage":"已签约","source":"2026年高质量发展大会","announced_date":"2026-02","description":"华南地区最大高端钢管生产基地"},
    {"enterprise_name":"巴夫洛·佛山高明智慧供应链产业园","industry":"现代物流","chain_id":6,"amount":10,"stage":"已签约","source":"高明区招商局","announced_date":"2026-03","description":"全球物流巨头Prologis进驻高明，激活两业融合"},
    {"enterprise_name":"富成精密科技生产总部","industry":"装备制造","chain_id":3,"amount":8,"stage":"已签约","source":"2026年高质量发展大会","announced_date":"2026-03","description":"铝合金/镁合金精密压铸，用于汽车/航空航天/机器人"},
    {"enterprise_name":"湾区云裳生态谷","industry":"纺织服装","chain_id":1,"amount":15,"stage":"已签约","source":"2026年签约","announced_date":"2026-05","description":"纺织服装零碳智造创新平台，下半年首批企业进驻"},
    {"enterprise_name":"甜秘密高端智能家居生产基地（二期）","industry":"智能家居","chain_id":8,"amount":6,"stage":"已签约","source":"2026年高质量发展大会","announced_date":"2026-03","description":"高端智能家居制造基地扩产"},
    {"enterprise_name":"臻壕垣机械设备智造项目","industry":"装备制造","chain_id":3,"amount":5,"stage":"已签约","source":"2026年高质量发展大会","announced_date":"2026-03","description":"高端激光切割设备制造"},
    # 2025-2026年在建/已投产项目
    {"enterprise_name":"安博物流高明园区","industry":"现代物流","chain_id":6,"amount":8,"stage":"在建","source":"高明区招商局","announced_date":"2025-03","description":"国际物流巨头安博集团高明物流园"},
    {"enterprise_name":"广东天元智造高明智能装备基地","industry":"装备制造","chain_id":3,"amount":12,"stage":"在建","source":"高明区招商局","announced_date":"2025-06","description":"智能装备制造基地，预计2026年底投产"},
    {"enterprise_name":"比亚迪弗迪动力电池(高明)配套基地","industry":"装备制造","chain_id":3,"amount":25,"stage":"在建","source":"佛山市招商","announced_date":"2024-08","description":"新能源汽车动力电池配套基地"},
    {"enterprise_name":"深圳华大基因(高明)精准医学中心","industry":"生物医药","chain_id":5,"amount":5,"stage":"在建","source":"佛山市招商","announced_date":"2024-06","description":"精准医学检测与研发中心"},
    {"enterprise_name":"上海均和集团高明新材料基地","industry":"新材料","chain_id":5,"amount":15,"stage":"在建","source":"高明区招商局","announced_date":"2024-01","description":"高性能复合材料生产基地"},
    {"enterprise_name":"佛山仙湖实验室高明氢能中试基地","industry":"新材料","chain_id":5,"amount":10,"stage":"在建","source":"佛山市重点建设项目","announced_date":"2024-04","description":"氢能材料中试及产业化基地"},
    {"enterprise_name":"宜家供应链华南区分拨中心","industry":"现代物流","chain_id":6,"amount":10,"stage":"已投产","source":"高明区招商局","announced_date":"2022-06","description":"华南区家居产品分拨枢纽"},
    {"enterprise_name":"顺丰智慧物流高明枢纽","industry":"现代物流","chain_id":6,"amount":20,"stage":"已投产","source":"高明区招商局","announced_date":"2023-01","description":"智慧物流华南区域枢纽"},
    {"enterprise_name":"京东物流高明智能仓","industry":"现代物流","chain_id":6,"amount":6,"stage":"在建","source":"高明区招商","announced_date":"2025-05","description":"京东物流智能仓储中心"},
    {"enterprise_name":"广州无线电集团(高明)智能制造基地","industry":"电子信息","chain_id":7,"amount":8,"stage":"在建","source":"佛山市招商","announced_date":"2025-07","description":"工业物联网智能制造基地"},
    {"enterprise_name":"润泽（佛山）国际信息港（一期）","industry":"电子信息","chain_id":7,"amount":20,"stage":"已投产","source":"高明区招商局","announced_date":"2023-06","description":"大湾区重要算力基础设施"},
    {"enterprise_name":"南网战新（佛山）新动能产业基地","industry":"电力装备","chain_id":9,"amount":15,"stage":"已签约","source":"2026年高质量发展大会","announced_date":"2026-03","description":"新型电力系统装备基地，南网战新基金5亿元配套"},
    {"enterprise_name":"圃美多豆制品智能生产基地","industry":"食品饮料","chain_id":4,"amount":3,"stage":"已签约","source":"2026年招商","announced_date":"2026-04","description":"全球豆制品龙头圃美多落户高明杨和镇，长期供应山姆会员店，年产值超8亿元"},
    {"enterprise_name":"咖啡生豆保税仓","industry":"食品饮料","chain_id":4,"amount":2,"stage":"已投产","source":"高明区招商局","announced_date":"2026-05","description":"高咖农业在老挝建立咖啡种植基地，开展保税仓储、精深加工和国际贸易"},
    {"enterprise_name":"深国际·高明先进制造与空港供应链中心","industry":"现代物流","chain_id":6,"amount":12,"stage":"已签约","source":"高明区招商局","announced_date":"2026-03","description":"深国际集团布局空港供应链中心，服务临空经济"},
    {"enterprise_name":"浙天智能家居生产制造总部基地","industry":"智能家居","chain_id":8,"amount":1,"stage":"已签约","source":"高明区招商局","announced_date":"2026-03","description":"东莞市浙天装饰材料有限公司投建，聚焦智能安防锁具全产业链"},
    {"enterprise_name":"甜秘密高端智能家居生产基地（二期）","industry":"智能家居","chain_id":8,"amount":10,"stage":"已签约","source":"高明区高质量发展大会","announced_date":"2026-02","description":"甜秘密二次增资扩产，累计投资23亿元，产品畅销全球130多个国家"},
    {"enterprise_name":"沛国智慧健康办公装备制造项目","industry":"智能家居","chain_id":8,"amount":2,"stage":"已签约","source":"高明区招商局","announced_date":"2026-01","description":"智能电控升降办公桌年产能超20万套，出口占比80%"},
    {"enterprise_name":"高明独立储能电站项目","industry":"电力装备","chain_id":9,"amount":15,"stage":"已投产","source":"佛山市重点建设项目","announced_date":"2025-07","description":"佛山首座220kV新型储能电站，规模208MW/416MWh，大湾区城市超级充电宝"},
]

# ═══════════════════════════════════════════════════════════
# 基础设施 (2026年真实进展)
# ═══════════════════════════════════════════════════════════
INFRASTRUCTURES = [
    {
        "name":"珠三角枢纽(广州新)机场",
        "infra_type":"机场",
        "status":"已开工",
        "description":"2026年3月25日正式动工。本期投资418.08亿元，新建2条4E级跑道、26万㎡航站楼。设计年旅客3000万人次、货邮50万吨。远期可达6000-8000万人次。南航、中联航已确定作为基地航司入驻",
        "impact_areas": json.dumps(["现代物流","智能家居","电子信息","新材料","电力装备"]),
        "planned_completion":"2028-2030",
        "source":"南方日报2026年3月报道"
    },
    {
        "name":"广湛高铁",
        "infra_type":"高铁",
        "status":"已运营",
        "description":"2025年12月22日通车运营。广州-湛江，设计时速350km/h。设佛山高明站。高明至广州中心城区缩短至15分钟。广湛高铁佛肇站(机场站)设于新机场航站楼正下方，实现空铁零距离换乘",
        "impact_areas": json.dumps(["现代物流","纺织服装","食品饮料","装备制造","智能家居"]),
        "planned_completion":"2025-12(已通车)",
        "source":"广铁集团"
    },
    {
        "name":"珠肇高铁(高明段)",
        "infra_type":"高铁",
        "status":"建设中",
        "description":"珠海-肇庆高速铁路，高明设站。与广湛高铁在高明交汇，形成区域性高铁枢纽。江机段桥梁主体已完工，正进行四电工程。高明至珠海缩短至1小时内",
        "impact_areas": json.dumps(["现代物流","电子信息","装备制造","智能家居"]),
        "planned_completion":"2027",
        "source":"广东省铁路建设规划"
    },
    {
        "name":"深南高铁(高明段)",
        "infra_type":"高铁",
        "status":"建设中",
        "description":"深圳-南宁高速铁路，经高明珠三角枢纽机场站。珠三角枢纽机场至省界段已开始架梁，桩基施工接近尾声。高明至深圳缩短至1小时",
        "impact_areas": json.dumps(["电子信息","现代物流","装备制造","新材料"]),
        "planned_completion":"2027",
        "source":"广东省铁路建设规划"
    },
    {
        "name":"佛山地铁2号线二期(高明段)",
        "infra_type":"地铁",
        "status":"规划中",
        "description":"连接高明与佛山中心城区，设高明站、荷城站等，加强高明与佛山主城区的同城化",
        "impact_areas": json.dumps(["智能家居","纺织服装","房地产"]),
        "planned_completion":"2028",
        "source":"佛山市轨道交通规划"
    },
    {
        "name":"西江黄金水道(高明港升级)",
        "infra_type":"港口",
        "status":"规划中",
        "description":"高明港升级为5000吨级码头，打造西江内河航运枢纽，服务临港产业",
        "impact_areas": json.dumps(["现代物流","陶瓷建材","装备制造","新材料"]),
        "planned_completion":"2027",
        "source":"高明区交通规划"
    },
    {
        "name":"南沙至新机场高速",
        "infra_type":"高速",
        "status":"规划中",
        "description":"连接南沙自贸区和广州新机场的高速通道，高明将形成'五横五纵'高速路网，高速出入口由7个增至18个",
        "impact_areas": json.dumps(["现代物流","装备制造","电子信息"]),
        "planned_completion":"2028",
        "source":"佛山市交通规划"
    },
]

# ═══════════════════════════════════════════════════════════
# 周边城市关系
# ═══════════════════════════════════════════════════════════
CITY_RELATIONS = [
    {"city_name":"佛山南海区","relation_type":"合作","industry":"全产业","description":"同城化发展，产业协同互补，南海拥有研发/金融/总部资源，高明提供制造基地"},
    {"city_name":"佛山顺德区","relation_type":"合作","industry":"装备制造/电力装备","description":"顺德家电和电力装备产业外溢，万和电气与顺德美的、南方电网形成供应链协同"},
    {"city_name":"佛山禅城区","relation_type":"合作","industry":"陶瓷建材","description":"禅城为陶瓷总部/研发/会展中心，高明为生产基地"},
    {"city_name":"广州","relation_type":"互补","industry":"现代物流/临空经济","description":"白云机场国际航线+新机场形成'一市两场'互补格局。广湛高铁15分钟直达广州中心"},
    {"city_name":"肇庆","relation_type":"合作","industry":"新材料/陶瓷","description":"肇庆矿产资源丰富，为高明新材料和陶瓷产业提供原材料，西江航道联系紧密"},
    {"city_name":"深圳","relation_type":"竞争","industry":"电子信息","description":"深圳电子信息产业高地，高明需差异化发展智算中心+配套制造环节。深南高铁通车后将形成1小时经济圈"},
    {"city_name":"东莞","relation_type":"竞争","industry":"装备制造","description":"东莞制造业基础雄厚，高明需依托成本优势和空港枢纽优势吸引产能转移"},
    {"city_name":"珠海","relation_type":"合作","industry":"现代物流/临空经济","description":"珠肇高铁连通后高明-珠海1小时通达，空港-海港联动发展"},
    {"city_name":"佛山三水区","relation_type":"合作","industry":"食品饮料","description":"三水食品饮料产业集聚，与高明海天味业形成协同"},
]

# ═══════════════════════════════════════════════════════════
# 经济影响评估 (2025-2030)
# ═══════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════
# 城市-产业链 上下游关系 (输入端→高明 / 输出端←高明)
# ═══════════════════════════════════════════════════════════
CITY_CHAIN_FLOWS = [
    # 纺织服装: 上游供应来自广州/佛山禅城, 下游市场辐射全国
    {"chain_id":1,"city":"广州","flow_type":"下游","description":"广州服装批发市场(中大布匹、十三行)是高明白胚布和成衣的主要销售渠道"},
    {"chain_id":1,"city":"佛山禅城","flow_type":"下游","description":"禅城童装/针织产业集群吸收高明面料"},
    {"chain_id":1,"city":"广州","flow_type":"上游","description":"广州中大布匹市场提供高端面料原料"},
    # 陶瓷建材: 上游原料来自肇庆, 下游销往大湾区
    {"chain_id":2,"city":"肇庆","flow_type":"上游","description":"肇庆提供陶瓷泥料、釉料等原材料"},
    {"chain_id":2,"city":"佛山禅城","flow_type":"下游","description":"禅城华夏陶瓷博览城、中国陶瓷总部基地为高明陶瓷提供展示交易平台"},
    {"chain_id":2,"city":"广州","flow_type":"下游","description":"广州建筑市场为高明陶瓷建材主要销售地"},
    # 装备制造: 上游精密部件来自顺德/南海, 下游整机配套
    {"chain_id":3,"city":"佛山顺德","flow_type":"上游","description":"顺德提供精密模具、电机等装备制造核心部件"},
    {"chain_id":3,"city":"佛山南海","flow_type":"上游","description":"南海提供铝型材、五金件等装备制造原材料"},
    {"chain_id":3,"city":"佛山顺德","flow_type":"下游","description":"高明装备为顺德家电企业提供生产线和部件"},
    {"chain_id":3,"city":"广州","flow_type":"下游","description":"广州汽车产业为高明精密压铸提供需求市场"},
    # 食品饮料: 上游包装材料/原料, 下游消费市场
    {"chain_id":4,"city":"佛山三水","flow_type":"下游","description":"三水食品饮料产业集群与高明形成竞争互补"},
    {"chain_id":4,"city":"广州","flow_type":"下游","description":"广州为海天味业全国最大消费市场"},
    # 新材料: 上游研发资源, 下游多行业应用
    {"chain_id":5,"city":"广州","flow_type":"上游","description":"广州高校和科研机构提供新材料研发支持和人才"},
    {"chain_id":5,"city":"佛山南海","flow_type":"合作","description":"南海仙湖实验室本部与高明氢能中试基地形成研发-产业化联动"},
    {"chain_id":5,"city":"肇庆","flow_type":"上游","description":"肇庆矿产资源(稀土、碳酸钙)为新材料提供原料"},
    # 现代物流: 临空经济上下游
    {"chain_id":6,"city":"广州","flow_type":"互补","description":"白云机场国际货运+高明新机场国内货运形成协同, 广湛高铁15分钟联通"},
    {"chain_id":6,"city":"珠海","flow_type":"下游","description":"珠海高栏港与高明空港形成空海联运"},
    {"chain_id":6,"city":"肇庆","flow_type":"上游","description":"肇庆大宗货运经西江航道从高明港中转"},
    # 电子信息/数字经济: 上下游
    {"chain_id":7,"city":"深圳","flow_type":"上游","description":"深圳电子信息产业为高明提供芯片、模组等核心元器件"},
    {"chain_id":7,"city":"广州","flow_type":"上游","description":"广州高校和科研机构提供软件和算法人才"},
    {"chain_id":7,"city":"东莞","flow_type":"竞争","description":"东莞电子制造配套与高明形成竞争"},
    # 智能家居
    {"chain_id":8,"city":"佛山顺德","flow_type":"上游","description":"顺德家电产业链为高明智能家居提供核心部件和品牌赋能"},
    {"chain_id":8,"city":"广州","flow_type":"下游","description":"广州消费市场为高明智能家居提供主要客户"},
    # 新型电力系统装备
    {"chain_id":9,"city":"广州","flow_type":"上游","description":"南方电网总部(广州)为高明电力装备提供技术标准和订单"},
    {"chain_id":9,"city":"佛山顺德","flow_type":"合作","description":"顺德电力装备企业与高明协同配套"},
]

# ═══════════════════════════════════════════════════════════
# 招商引资机会点 (产业链缺口分析)
# ═══════════════════════════════════════════════════════════
INVESTMENT_OPPORTUNITIES = [
    # ═══ 纺织服装产业链 (chain_id=1) ═══
    {"chain_id":1,"name":"功能性面料研发生产基地","category":"技术升级","gap_type":"技术缺口",
     "estimated_investment":"5-10亿","priority":"高",
     "description":"引入具有防水、阻燃、抗菌等功能性面料研发生产能力的企业，补强纺织上游环节",
     "target_enterprises":"佛山本地纺织科技企业、上海/浙江功能性面料企业"},
    {"chain_id":1,"name":"服装品牌总部/设计中心","category":"品牌打造","gap_type":"下游缺口",
     "estimated_investment":"2-5亿","priority":"中",
     "description":"引进知名服装品牌区域总部或独立设计师工作室，补强品牌设计下游环节",
     "target_enterprises":"广州/深圳服装设计师品牌、电商服装品牌"},
    {"chain_id":1,"name":"纺织工业互联网平台","category":"数字化转型","gap_type":"技术缺口",
     "estimated_investment":"1-3亿","priority":"中",
     "description":"建设纺织行业工业互联网平台，实现溢达等龙头企业的数字化赋能和产能共享",
     "target_enterprises":"工业互联网平台企业(树根互联/腾讯云等)"},
    {"chain_id":1,"name":"航空内饰/产业用纺织品生产基地","category":"高端纺织","gap_type":"上游缺口",
     "estimated_investment":"5-10亿","priority":"高",
     "description":"引入航空座椅面料、汽车内饰织物等高附加值产业用纺织品产线，填补临空经济高端纺织空白",
     "target_enterprises":"航空纺织品企业(吉兴汽车内饰/申达股份等)"},
    {"chain_id":1,"name":"纺织印染废水循环利用中心","category":"绿色环保","gap_type":"供应链缺口",
     "estimated_investment":"2-5亿","priority":"中",
     "description":"建设纺织印染废水集中处理与循环利用设施，解决合丰纺织等企业环保压力",
     "target_enterprises":"工业水处理企业(金科环境/博天环境等)"},

    # ═══ 陶瓷建材产业链 (chain_id=2) ═══
    {"chain_id":2,"name":"陶瓷固废循环利用项目","category":"绿色环保","gap_type":"供应链缺口",
     "estimated_investment":"3-8亿","priority":"高",
     "description":"建设陶瓷废渣资源化利用生产线，解决陶瓷产业固废问题，年处理能力50万吨",
     "target_enterprises":"固废处理环保企业(东江环保/格林美等)"},
    {"chain_id":2,"name":"陶瓷智能化装备制造","category":"技术升级","gap_type":"技术缺口",
     "estimated_investment":"5-10亿","priority":"高",
     "description":"引入陶瓷智能喷墨打印、智能检测分选等装备制造企业，提升陶瓷产业自动化水平",
     "target_enterprises":"陶瓷装备企业(科达制造/力泰等)"},
    {"chain_id":2,"name":"高端工业陶瓷/电子陶瓷生产基地","category":"新材料","gap_type":"上游缺口",
     "estimated_investment":"10-20亿","priority":"高",
     "description":"引入氧化铝陶瓷、氮化硅陶瓷等工业陶瓷企业，推动高明陶瓷从建筑陶瓷向电子陶瓷/半导体陶瓷转型",
     "target_enterprises":"工业陶瓷企业(三环集团/国瓷材料/东方锆业等)"},
    {"chain_id":2,"name":"陶瓷品牌设计运营中心","category":"品牌打造","gap_type":"下游缺口",
     "estimated_investment":"1-3亿","priority":"中",
     "description":"引进陶瓷品牌设计、营销运营机构，推动高明陶瓷从OEM代工向自主品牌转型",
     "target_enterprises":"品牌策划公司、陶瓷电商运营企业"},
    {"chain_id":2,"name":"陶瓷窑炉氢能/电能替代技改","category":"绿色能源","gap_type":"技术缺口",
     "estimated_investment":"5-10亿","priority":"中",
     "description":"推进陶瓷窑炉从天然气向氢能/电能转型，降低天然气价格波动风险，实现绿色生产",
     "target_enterprises":"工业窑炉节能改造企业、氢能燃烧技术企业"},

    # ═══ 装备制造/新型电力系统 (chain_id=3) ═══
    {"chain_id":3,"name":"精密伺服电机/减速器制造","category":"核心部件","gap_type":"供应链缺口",
     "estimated_investment":"8-15亿","priority":"高",
     "description":"引进精密伺服电机、RV减速器等工业机器人核心部件生产企业，补强装备制造上游",
     "target_enterprises":"汇川技术/绿的谐波等核心部件企业"},
    {"chain_id":3,"name":"工业机器人本体制造基地","category":"整机制造","gap_type":"上游缺口",
     "estimated_investment":"10-20亿","priority":"高",
     "description":"建设工业机器人本体制造基地，利用高明成本优势和交通优势服务大湾区制造业",
     "target_enterprises":"埃斯顿/新松机器人/佛山隆深等"},
    {"chain_id":3,"name":"新能源汽车零部件产业园","category":"新能源","gap_type":"下游缺口",
     "estimated_investment":"20-50亿","priority":"高",
     "description":"规划新能源汽车零部件专业园区，承接比亚迪配套企业及上下游，依托佛山西部汽车产业走廊",
     "target_enterprises":"比亚迪供应链企业/宁德时代配套/佛吉亚等Tier1"},
    {"chain_id":3,"name":"CNC数控系统研发制造基地","category":"核心部件","gap_type":"技术缺口",
     "estimated_investment":"5-15亿","priority":"中",
     "description":"引进高档数控系统研发制造企业，补齐大湾区高端CNC数控系统短板",
     "target_enterprises":"华中数控/广州数控/科德数控等"},
    {"chain_id":3,"name":"航空装备零部件制造基地","category":"临空制造","gap_type":"上游缺口",
     "estimated_investment":"10-30亿","priority":"高",
     "description":"依托广州新机场建设航空零部件制造基地，发展飞机结构件、起落架等航空精密制造",
     "target_enterprises":"中航工业供应链企业/南山铝业航材等"},

    # ═══ 食品饮料产业链 (chain_id=4) ═══
    {"chain_id":4,"name":"冷链物流与中央厨房基地","category":"配套升级","gap_type":"供应链缺口",
     "estimated_investment":"5-10亿","priority":"高",
     "description":"建设服务于食品饮料产业的冷链物流中心和中央厨房基地，完善食品产业链冷链环节",
     "target_enterprises":"冷链物流企业(郑明物流/鲜易等)/团餐企业"},
    {"chain_id":4,"name":"食品包装新材料研发基地","category":"配套升级","gap_type":"技术缺口",
     "estimated_investment":"2-5亿","priority":"中",
     "description":"引入可降解食品包装材料研发生产基地，服务海天等龙头企业包装需求",
     "target_enterprises":"食品包装企业(紫江企业/永新股份等)"},
    {"chain_id":4,"name":"功能性食品研发中心","category":"食品科技","gap_type":"技术缺口",
     "estimated_investment":"2-5亿","priority":"中",
     "description":"建设功能性食品、精准营养食品研发中心，推动食品产业由调味品向大健康食品延伸",
     "target_enterprises":"功能食品企业(汤臣倍健/仙乐健康等)/高校食品研究院"},
    {"chain_id":4,"name":"咖啡精深加工产业园","category":"新业态","gap_type":"下游缺口",
     "estimated_investment":"5-10亿","priority":"中",
     "description":"围绕已落户的咖啡生豆保税仓，延伸咖啡烘焙、冷萃液、冻干粉等精深加工产业链",
     "target_enterprises":"咖啡加工企业(三顿半/永璞咖啡/瑞幸供应链等)"},
    {"chain_id":4,"name":"农产品冷链仓储集配中心","category":"配套升级","gap_type":"供应链缺口",
     "estimated_investment":"3-8亿","priority":"高",
     "description":"建设合水粉葛、三洲黑鹅等地理标志农产品冷链仓储和集配中心，支撑2252工程",
     "target_enterprises":"农产品冷链物流企业/供销社系统"},

    # ═══ 新材料/氢能产业链 (chain_id=5) ═══
    {"chain_id":5,"name":"氢燃料电池核心部件制造","category":"前沿技术","gap_type":"技术缺口",
     "estimated_investment":"10-20亿","priority":"高",
     "description":"引进质子交换膜、催化剂等氢燃料电池核心部件制造商，与仙湖实验室形成产研协同",
     "target_enterprises":"氢燃料电池企业(国鸿氢能/亿华通/上海重塑等)"},
    {"chain_id":5,"name":"碳纤维复合材料生产基地","category":"新材料","gap_type":"上游缺口",
     "estimated_investment":"15-30亿","priority":"中",
     "description":"建设高性能碳纤维复合材料生产基地，应用于航空航天(依托新机场)、汽车轻量化等领域",
     "target_enterprises":"碳纤维企业(光威复材/中复神鹰等)"},
    {"chain_id":5,"name":"锂电池正极材料回收循环利用","category":"绿色循环","gap_type":"供应链缺口",
     "estimated_investment":"5-10亿","priority":"高",
     "description":"引进废旧锂电池正极材料回收再利用产线，与德方纳米形成产业闭环",
     "target_enterprises":"电池回收企业(格林美/华友循环/天奇股份等)"},
    {"chain_id":5,"name":"氢能储运装备制造基地","category":"前沿技术","gap_type":"供应链缺口",
     "estimated_investment":"8-15亿","priority":"中",
     "description":"引进高压储氢罐/液氢储运装备制造企业，补齐高明氢能产业储运环节缺失",
     "target_enterprises":"储氢装备企业(中材科技/富瑞氢能/科泰克等)"},
    {"chain_id":5,"name":"半导体电子材料生产基地","category":"前沿材料","gap_type":"技术缺口",
     "estimated_investment":"20-50亿","priority":"中",
     "description":"引进光刻胶/电子特气/湿电子化学品等半导体电子材料企业，切入高附加值材料赛道",
     "target_enterprises":"半导体材料企业(彤程新材/华特气体/晶瑞电材等)"},

    # ═══ 现代物流/临空经济 (chain_id=6) ═══
    {"chain_id":6,"name":"航空食品加工基地","category":"临空经济","gap_type":"下游缺口",
     "estimated_investment":"3-8亿","priority":"高",
     "description":"依托广州新机场建设航空食品加工基地，为航线提供配餐服务，同时发展预制菜产业",
     "target_enterprises":"航空食品企业(中翼航空食品/汉莎天厨等)"},
    {"chain_id":6,"name":"跨境电商保税仓+分拨中心","category":"临空经济","gap_type":"供应链缺口",
     "estimated_investment":"5-15亿","priority":"高",
     "description":"建设跨境电商保税仓储和全球分拨中心，利用新机场货运能力和综保区政策优势",
     "target_enterprises":"跨境电商平台(SHEIN/Temu/速卖通等)仓储物流服务商"},
    {"chain_id":6,"name":"临空高端制造园(航空修造)","category":"临空经济","gap_type":"上游缺口",
     "estimated_investment":"20-50亿","priority":"中",
     "description":"规划临空高端制造园区，聚焦航空零部件制造、飞机维修等航空修造产业",
     "target_enterprises":"航空制造企业(中航工业供应链企业等)"},
    {"chain_id":6,"name":"综合保税区申报及配套设施","category":"口岸平台","gap_type":"供应链缺口",
     "estimated_investment":"5-10亿","priority":"高",
     "description":"加快推进综合保税区申报和建设，解决外贸物流通道不足、保税功能缺失的核心瓶颈",
     "target_enterprises":"海关监管服务企业/国际贸易综合服务企业"},
    {"chain_id":6,"name":"高明港升级多式联运枢纽","category":"港口物流","gap_type":"下游缺口",
     "estimated_investment":"10-20亿","priority":"高",
     "description":"整合高明11个码头资源，升级为5000吨级多式联运枢纽，实现水陆空铁四港联动",
     "target_enterprises":"港口运营企业(招商港口/广州港等)/多式联运服务商"},

    # ═══ 电子信息/数字经济 (chain_id=7) ═══
    {"chain_id":7,"name":"半导体封装测试基地","category":"核心产业","gap_type":"技术缺口",
     "estimated_investment":"30-50亿","priority":"中",
     "description":"引进半导体封装测试产线，服务大湾区半导体设计企业，差异化定位先进封装",
     "target_enterprises":"封测企业(长电科技/通富微电/华天科技等)"},
    {"chain_id":7,"name":"AI算力应用产业基地","category":"数字经济","gap_type":"下游缺口",
     "estimated_investment":"5-15亿","priority":"高",
     "description":"围绕润泽智算中心建设AI应用产业基地，吸引AI大模型训练、推理应用企业入驻",
     "target_enterprises":"AI企业(商汤/旷视/科大讯飞等)/云计算企业"},
    {"chain_id":7,"name":"EMS/ODM电子制造服务基地","category":"电子制造","gap_type":"上游缺口",
     "estimated_investment":"10-30亿","priority":"中",
     "description":"引进大型电子制造服务(EMS)企业，补强高明电子信息产业代工制造环节缺失",
     "target_enterprises":"EMS企业(立讯精密/歌尔股份/比亚迪电子等)"},
    {"chain_id":7,"name":"工业软件/数字孪生产业园","category":"软件产业","gap_type":"技术缺口",
     "estimated_investment":"5-10亿","priority":"中",
     "description":"引进工业软件和数字孪生企业，服务高明制造业数字化转型需求",
     "target_enterprises":"工业软件企业(中望软件/华大九天/用友网络等)"},

    # ═══ 智能家居产业链 (chain_id=8) ═══
    {"chain_id":8,"name":"智能家居物联网平台","category":"技术升级","gap_type":"技术缺口",
     "estimated_investment":"2-8亿","priority":"中",
     "description":"引进智能家居物联网平台企业，实现高明智能家居产品的互联互通和生态构建",
     "target_enterprises":"物联网平台企业(小米生态链/华为鸿蒙等)"},
    {"chain_id":8,"name":"智能传感器研发生产基地","category":"核心部件","gap_type":"供应链缺口",
     "estimated_investment":"3-8亿","priority":"高",
     "description":"引进智能家居专用传感器(人体感应/温湿度/气体等)研发制造企业，补强智能硬件上游",
     "target_enterprises":"传感器企业(汉威科技/敏芯股份/睿创微纳等)"},
    {"chain_id":8,"name":"智能家居检测认证实验室","category":"公共平台","gap_type":"技术缺口",
     "estimated_investment":"1-3亿","priority":"中",
     "description":"建设智能家居互联互通测试认证实验室，降低企业产品开发和认证成本",
     "target_enterprises":"检测认证机构(SGS/TÜV/中国信通院等)"},
    {"chain_id":8,"name":"智能家居跨境电商运营中心","category":"数字经济","gap_type":"下游缺口",
     "estimated_investment":"2-5亿","priority":"中",
     "description":"建设智能家居跨境电商运营中心，服务甜秘密等企业全球130+国家市场的品牌推广",
     "target_enterprises":"跨境电商运营企业/海外品牌营销机构"},

    # ═══ 新型电力系统装备产业链 (chain_id=9) ═══
    {"chain_id":9,"name":"新型储能电池系统集成","category":"新能源","gap_type":"技术缺口",
     "estimated_investment":"10-25亿","priority":"高",
     "description":"引进新型储能电池系统集成企业，服务于南方电网新型电力系统建设需求",
     "target_enterprises":"储能企业(宁德时代储能/比亚迪储能/阳光电源等)"},
    {"chain_id":9,"name":"智能电网设备制造基地","category":"电力装备","gap_type":"上游缺口",
     "estimated_investment":"10-20亿","priority":"高",
     "description":"建设智能电网设备(智能电表/配电自动化/变电站)制造基地，配套南方电网采购需求",
     "target_enterprises":"电力设备企业(许继电气/国电南瑞/四方股份等)"},
    {"chain_id":9,"name":"IGBT/SiC功率半导体封装基地","category":"核心器件","gap_type":"供应链缺口",
     "estimated_investment":"10-30亿","priority":"高",
     "description":"引进IGBT和碳化硅功率半导体封装产线，服务于新型电力系统和新能源汽车产业",
     "target_enterprises":"功率半导体企业(斯达半导/时代电气/中车半导体等)"},
    {"chain_id":9,"name":"虚拟电厂运营平台","category":"数字能源","gap_type":"下游缺口",
     "estimated_investment":"2-5亿","priority":"中",
     "description":"建设虚拟电厂聚合运营平台，整合高明分布式储能和可调负荷资源参与电力市场交易",
     "target_enterprises":"虚拟电厂运营企业(国能日新/恒实科技/特来电等)"},
    {"chain_id":9,"name":"电力装备检测实验中心","category":"公共平台","gap_type":"技术缺口",
     "estimated_investment":"3-8亿","priority":"中",
     "description":"建设CNAS认证的电力装备高压检测实验中心，服务南网战新基地及大湾区电力设备企业",
     "target_enterprises":"电力检测机构(中国电科院/南网科研院等)"},
]


ECONOMIC_IMPACTS = [
    # 2025年现状
    {"chain_id":1,"year":2025,"output_value":130,"employment":17000,"gdp_contribution":39,"description":"纺织服装产业链-传统产能"},
    {"chain_id":2,"year":2025,"output_value":200,"employment":22000,"gdp_contribution":60,"description":"陶瓷建材产业链-含技改产线"},
    {"chain_id":3,"year":2025,"output_value":150,"employment":12000,"gdp_contribution":45,"description":"装备制造/电力系统-含在建项目"},
    {"chain_id":4,"year":2025,"output_value":250,"employment":12000,"gdp_contribution":75,"description":"食品饮料-海天为主"},
    {"chain_id":5,"year":2025,"output_value":25,"employment":2500,"gdp_contribution":8,"description":"新材料/氢能-培育期"},
    {"chain_id":6,"year":2025,"output_value":30,"employment":4000,"gdp_contribution":9,"description":"现代物流-含已投产项目"},
    {"chain_id":7,"year":2025,"output_value":25,"employment":2000,"gdp_contribution":8,"description":"电子信息/数字经济-润泽一期投产"},
    {"chain_id":8,"year":2025,"output_value":8,"employment":1000,"gdp_contribution":2.5,"description":"智能家居-培育期"},
    {"chain_id":9,"year":2025,"output_value":5,"employment":500,"gdp_contribution":1.5,"description":"新型电力系统装备-刚起步"},
    # 2027年预测 (新机场建设中+广湛高铁运营+多条高铁在建)
    {"chain_id":1,"year":2027,"output_value":180,"employment":20000,"gdp_contribution":55,"description":"纺织服装-湾区云裳生态谷投产+智能化升级"},
    {"chain_id":2,"year":2027,"output_value":250,"employment":20000,"gdp_contribution":75,"description":"陶瓷建材-全面绿色转型"},
    {"chain_id":3,"year":2027,"output_value":280,"employment":20000,"gdp_contribution":85,"description":"装备制造-振鸿/富成/天元全面投产"},
    {"chain_id":4,"year":2027,"output_value":300,"employment":13000,"gdp_contribution":90,"description":"食品饮料-海天扩产完成"},
    {"chain_id":5,"year":2027,"output_value":60,"employment":5000,"gdp_contribution":18,"description":"新材料/氢能-中试产业化"},
    {"chain_id":6,"year":2027,"output_value":60,"employment":10000,"gdp_contribution":18,"description":"现代物流-临空经济起步"},
    {"chain_id":7,"year":2027,"output_value":60,"employment":5000,"gdp_contribution":18,"description":"电子信息-润泽二期投产+算力生态"},
    {"chain_id":8,"year":2027,"output_value":20,"employment":3000,"gdp_contribution":6,"description":"智能家居-甜秘密扩产"},
    {"chain_id":9,"year":2027,"output_value":30,"employment":3000,"gdp_contribution":9,"description":"新型电力系统装备-南网基地投产"},
    # 2030年预测 (新机场运营+高铁网络成熟)
    {"chain_id":1,"year":2030,"output_value":220,"employment":20000,"gdp_contribution":66,"description":"纺织服装-零碳智造集群成型"},
    {"chain_id":2,"year":2030,"output_value":280,"employment":18000,"gdp_contribution":84,"description":"陶瓷建材-绿色高端化"},
    {"chain_id":3,"year":2030,"output_value":400,"employment":30000,"gdp_contribution":120,"description":"装备制造/电力系统-成为核心支柱"},
    {"chain_id":4,"year":2030,"output_value":380,"employment":15000,"gdp_contribution":114,"description":"食品饮料-全球调味品基地"},
    {"chain_id":5,"year":2030,"output_value":120,"employment":8000,"gdp_contribution":36,"description":"新材料/氢能-百亿级产业"},
    {"chain_id":6,"year":2030,"output_value":120,"employment":20000,"gdp_contribution":36,"description":"现代物流-临空经济成熟"},
    {"chain_id":7,"year":2030,"output_value":120,"employment":10000,"gdp_contribution":36,"description":"电子信息/数字经济-湾区算力枢纽"},
    {"chain_id":8,"year":2030,"output_value":40,"employment":5000,"gdp_contribution":12,"description":"智能家居-品牌化发展"},
    {"chain_id":9,"year":2030,"output_value":80,"employment":8000,"gdp_contribution":24,"description":"新型电力系统装备-打造百亿集群"},
]


def scrape_gaoming_news():
    """尝试抓取高明区政府招商新闻"""
    results = []
    sources = [
        ("高明区人民政府", "http://www.gaoming.gov.cn/zwgk/zdlyxxgk/zsxx/"),
        ("高明区发改局", "http://www.gaoming.gov.cn/gzjg/zfgzbm/qfgj/"),
    ]
    for name, url in sources:
        try:
            resp = requests.get(url, timeout=8, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            })
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "lxml")
                for a in soup.select("a[href*='content'], a[href*='.html'], ul.list li a")[:15]:
                    title = a.get_text(strip=True)
                    href = a.get("href", "")
                    if title and len(title) > 8:
                        results.append({"title": title, "url": href, "source": name, "date": datetime.now().strftime("%Y-%m-%d")})
        except Exception as e:
            print(f"  [!] 抓取 {name} 失败: {e}")
    if not results:
        # fallback: 返回已知新闻
        results = [
            {"title":"高明区34个重点产业项目集中签约 意向投资总额超230亿元","url":"#","source":"2026年高质量发展大会","date":"2026-03-20"},
            {"title":"广州新机场在高明正式开工建设 总投资418亿元","url":"#","source":"南方日报","date":"2026-03-25"},
            {"title":"广湛高铁通车运营 高明至广州15分钟通达","url":"#","source":"广铁集团","date":"2025-12-22"},
            {"title":"润泽科技二期签约高明 百亿级智算中心扩容","url":"#","source":"高明区招商局","date":"2026-02-26"},
            {"title":"巴夫洛物流巨头进驻高明 智慧供应链产业园签约","url":"#","source":"高明区招商局","date":"2026-03-15"},
            {"title":"振鸿金属25亿元项目落户高明 打造华南钢管基地","url":"#","source":"高明区招商局","date":"2026-02-11"},
            {"title":"湾区云裳生态谷签约落地高明 纺织零碳智造创新平台","url":"#","source":"佛山新闻网","date":"2026-05-27"},
            {"title":"高明区纺织服装生态谷创新平台签约落地 下半年迎首批企业进驻","url":"#","source":"澎湃新闻","date":"2026-05-27"},
        ]
    return results


def seed_database():
    """填充所有数据到数据库"""
    init_db()
    chain_map = {}

    # 产业链
    for c in INDUSTRY_CHAINS:
        cid = add_chain(**c)
        if cid:
            chain_map[c["chain_name"]] = cid
    print(f"[数据] 写入 {len(chain_map)} 条产业链")

    # 企业
    cnt = 0
    chain_mapping = {
        "纺织服装":"纺织服装产业链","陶瓷建材":"陶瓷建材产业链",
        "装备制造":"装备制造/新型电力系统","食品饮料":"食品饮料产业链",
        "新材料":"新材料/氢能产业链","现代物流":"现代物流/临空经济",
        "电子信息":"电子信息/数字经济","智能家居":"智能家居产业链",
        "电力装备":"新型电力系统装备产业链",
    }
    for e in GAOMING_ENTERPRISES:
        eid = add_enterprise(**e)
        if eid:
            cnt += 1
            chain_name = chain_mapping.get(e["industry"])
            if chain_name and chain_name in chain_map:
                with get_conn() as conn:
                    conn.execute("INSERT OR IGNORE INTO chain_relations (enterprise_id, chain_id, role) VALUES (?,?,?)",
                                 (eid, chain_map[chain_name], "核心" if e["scale"] in ("特大型","大型") else "配套"))
    print(f"[数据] 写入 {cnt} 家企业")

    # 招商企业
    for inv in INVESTMENTS:
        add_investment(**inv)
    print(f"[数据] 写入 {len(INVESTMENTS)} 条招商信息")

    # 基建
    for inf in INFRASTRUCTURES:
        add_infrastructure(**inf)
    print(f"[数据] 写入 {len(INFRASTRUCTURES)} 条基建信息")

    # 城市关系
    for cr in CITY_RELATIONS:
        sql = "INSERT INTO city_relations (city_name, relation_type, industry, description) VALUES (:city_name, :relation_type, :industry, :description)"
        with get_conn() as conn:
            conn.execute(sql, cr)

    # 经济影响
    for ei in ECONOMIC_IMPACTS:
        sql = "INSERT INTO economic_impact (chain_id, year, output_value, employment, gdp_contribution, description) VALUES (:chain_id, :year, :output_value, :employment, :gdp_contribution, :description)"
        with get_conn() as conn:
            conn.execute(sql, ei)
    print(f"[数据] 经济影响数据写入完成")

    # 城市-产业链上下游关系
    for cf in CITY_CHAIN_FLOWS:
        sql = "INSERT INTO city_chain_flows (chain_id, city, flow_type, description) VALUES (:chain_id, :city, :flow_type, :description)"
        with get_conn() as conn:
            conn.execute(sql, cf)
    print(f"[数据] 城市-产业链关系 {len(CITY_CHAIN_FLOWS)} 条写入完成")

    # 招商引资机会点
    for op in INVESTMENT_OPPORTUNITIES:
        sql = """INSERT INTO investment_opportunities (chain_id, name, category, gap_type, estimated_investment, priority, description, target_enterprises)
                 VALUES (:chain_id, :name, :category, :gap_type, :estimated_investment, :priority, :description, :target_enterprises)"""
        with get_conn() as conn:
            conn.execute(sql, op)
    print(f"[数据] 招商引资机会 {len(INVESTMENT_OPPORTUNITIES)} 条写入完成")
    print(f"\n✅ 数据库初始化完成! 共 {len(GAOMING_ENTERPRISES)} 家企业, {len(INDUSTRY_CHAINS)} 条产业链, {len(INVESTMENTS)} 个招商项目")
    return chain_map


if __name__ == "__main__":
    seed_database()
