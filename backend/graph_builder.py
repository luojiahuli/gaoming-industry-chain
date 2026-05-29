"""NetworkX 知识图谱构建 - 高明区产业关系网络"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))

import networkx as nx
from database import *


def build_graph() -> nx.DiGraph:
    """构建完整产业知识图谱"""
    G = nx.DiGraph()

    # ── 1. 企业节点 ──────────────────────────────────────
    enterprises = query("SELECT * FROM enterprises")
    for e in enterprises:
        G.add_node(
            f"ent_{e['id']}",
            id=e['id'],
            type="enterprise",
            name=e['name'],
            industry=e['industry'],
            sub_industry=e.get('sub_industry',''),
            chain_stage=e.get('chain_stage',''),
            scale=e.get('scale',''),
            revenue=e.get('revenue_annual',0),
            employees=e.get('employee_count',0),
            address=e.get('address',''),
            source=e.get('source',''),
            description=e.get('description',''),
            # 前端展示用
            label=e['name'],
            title=f"{e['name']} ({e['industry']})",
            size=min(60, max(20, e.get('revenue_annual',0) * 0.3 + 15)),
            color="#4A90D9"  # 蓝色-企业
        )

    # ── 2. 产业链节点 ────────────────────────────────────
    chains = query("SELECT * FROM industry_chains")
    chain_map = {}
    for c in chains:
        cid = f"chain_{c['id']}"
        chain_map[c['id']] = cid
        G.add_node(
            cid,
            id=c['id'],
            type="chain",
            name=c['chain_name'],
            category=c['category'],
            description=c.get('description',''),
            surrounding_cities=json.loads(c.get('surrounding_cities','[]')) if isinstance(c.get('surrounding_cities'), str) else c.get('surrounding_cities',[]),
            label=c['chain_name'],
            title=c['chain_name'],
            size=50,
            color="#E8A838"  # 金色-产业链
        )

    # ── 3. 企业→产业链 关联 ──────────────────────────────
    rels = query("""SELECT cr.*, e.name as ent_name, ic.chain_name
                    FROM chain_relations cr
                    JOIN enterprises e ON cr.enterprise_id=e.id
                    JOIN industry_chains ic ON cr.chain_id=ic.id""")
    for r in rels:
        G.add_edge(
            f"ent_{r['enterprise_id']}",
            chain_map.get(r['chain_id'], f"chain_{r['chain_id']}"),
            type="belongs_to",
            role=r.get('role','配套'),
            weight=2
        )

    # ── 4. 招商企业节点 ──────────────────────────────────
    invs = query("SELECT * FROM investments")
    for inv in invs:
        inv_id = f"inv_{inv['id']}"
        G.add_node(
            inv_id,
            id=inv['id'],
            type="investment",
            name=inv['enterprise_name'],
            industry=inv.get('industry',''),
            amount=inv.get('amount',0),
            stage=inv.get('stage',''),
            source=inv.get('source',''),
            date=inv.get('announced_date',''),
            description=inv.get('description',''),
            label=inv['enterprise_name'],
            title=f"[招商] {inv['enterprise_name']}",
            size=35,
            color="#E85A5A"  # 红色-招商
        )
        # 招商企业→产业链
        if inv.get('chain_id') and inv['chain_id'] in chain_map:
            G.add_edge(
                inv_id, chain_map[inv['chain_id']],
                type="investment_in",
                role="招商入驻",
                weight=1.5
            )

    # ── 5. 基础设施节点 ──────────────────────────────────
    infras = query("SELECT * FROM infrastructure")
    for inf in infras:
        inf_id = f"infra_{inf['id']}"
        impact = json.loads(inf['impact_areas']) if isinstance(inf.get('impact_areas'), str) else inf.get('impact_areas',[])
        G.add_node(
            inf_id,
            id=inf['id'],
            type="infrastructure",
            name=inf['name'],
            infra_type=inf['infra_type'],
            status=inf['status'],
            description=inf.get('description',''),
            completion=inf.get('planned_completion',''),
            impact_areas=impact,
            label=inf['name'],
            title=f"[基建] {inf['name']}",
            size=40,
            color="#7BC47F"  # 绿色-基建
        )

    # ── 6. 周边城市节点 ──────────────────────────────────
    cities = query("SELECT * FROM city_relations")
    seen_cities = {}
    for city in cities:
        ckey = city['city_name']
        if ckey not in seen_cities:
            seen_cities[ckey] = True
            G.add_node(
                f"city_{ckey}",
                type="city",
                name=ckey,
                label=ckey,
                title=f"城市: {ckey}",
                size=30,
                color="#9B59B6"  # 紫色-城市
            )

    # 城市关系边
    for city in cities:
        cname = city['city_name']
        industries = city['industry']
        rel_type = city['relation_type']
        color_map = {"互补": "#2ECC71", "竞争": "#E74C3C", "合作": "#3498DB"}
        G.add_edge(
            f"city_{cname}", f"chain_{chain_map.get(city.get('chain_id'), 0)}" if city.get('chain_id') else f"city_{cname}",
            type="city_relation",
            relation_type=rel_type,
            industry=industries,
            description=city.get('description',''),
            weight=1,
            color=color_map.get(rel_type, "#95A5A6")
        )

    # 基建→产业链 影响线
    for inf in infras:
        impact = json.loads(inf['impact_areas']) if isinstance(inf.get('impact_areas'), str) else inf.get('impact_areas',[])
        inf_id = f"infra_{inf['id']}"
        for cid, cnode in chain_map.items():
            chain_name = query_one("SELECT chain_name FROM industry_chains WHERE id=:id", {"id": cid})
            if chain_name:
                for ia in impact:
                    if ia in chain_name['chain_name'] or chain_name['chain_name'].startswith(ia):
                        G.add_edge(inf_id, cnode, type="impacts", weight=2.5, color="#2ECC71")

    # ── 7. 产业链间关联 (上下游) ────────────────────────
    # 根据产业经济学建立价值链关联
    chain_deps = [
        ("chain_5", "chain_3", "新材料→装备制造"),   # 新材料支撑装备制造
        ("chain_1", "chain_6", "纺织→物流"),          # 纺织需要物流
        ("chain_2", "chain_6", "陶瓷→物流"),          # 陶瓷需要物流
        ("chain_4", "chain_6", "食品→物流"),          # 食品需要物流
        ("chain_5", "chain_2", "新材料→陶瓷"),        # 新材料用于陶瓷
        ("chain_1", "chain_3", "纺织→纺织机械"),      # 纺织需要纺织机械(装备制造)
    ]
    for src, dst, label in chain_deps:
        if src in [f"chain_{c['id']}" for c in chains] and dst in [f"chain_{c['id']}" for c in chains]:
            G.add_edge(src, dst, type="chain_link", label=label, weight=1, color="#95A5A6")

    print(f"[图谱] 图构建完成: {G.number_of_nodes()} 节点, {G.number_of_edges()} 条边")
    return G


def get_graph_data() -> dict:
    """导出为前端可用的 JSON (Force-directed graph format)"""
    G = build_graph()
    nodes = []
    edges = []

    for n, attrs in G.nodes(data=True):
        node = {"id": n, **{k: v for k, v in attrs.items() if k != 'id'}}
        # 确保必须字段
        node.setdefault("label", n)
        node.setdefault("type", "unknown")
        node.setdefault("color", "#666")
        node.setdefault("size", 20)
        node.setdefault("title", n)
        nodes.append(node)

    for u, v, attrs in G.edges(data=True):
        edge = {"source": u, "target": v, **attrs}
        edges.append(edge)

    return {"nodes": nodes, "edges": edges}


def get_enterprise_detail(ent_id: int) -> dict:
    """获取企业详情"""
    e = query_one("SELECT * FROM enterprises WHERE id=:id", {"id": ent_id})
    if not e:
        return {}
    chains = query("""SELECT ic.* FROM industry_chains ic
        JOIN chain_relations cr ON cr.chain_id=ic.id
        WHERE cr.enterprise_id=?""", {"id": ent_id})
    return {**e, "chains": chains}


def get_chain_detail(chain_id: int) -> dict:
    """获取产业链详情"""
    c = query_one("SELECT * FROM industry_chains WHERE id=:id", {"id": chain_id})
    if not c:
        return {}
    ents = query("""SELECT e.* FROM enterprises e
        JOIN chain_relations cr ON cr.enterprise_id=e.id
        WHERE cr.chain_id=?""", {"id": chain_id})
    invs = query("SELECT * FROM investments WHERE chain_id=:id", {"id": chain_id})
    impacts = query("SELECT * FROM infrastructure WHERE impact_areas LIKE :id", {"id": f"%{c.get('chain_name','')[:4]}%"})
    eco = query("SELECT * FROM economic_impact WHERE chain_id=:id", {"id": chain_id})
    return {
        **c,
        "enterprises": ents,
        "investments": invs,
        "infrastructure": impacts,
        "economic_impacts": eco,
    }


def search_graph(keyword: str) -> list:
    """搜索企业/产业链/招商"""
    results = []
    kw = f"%{keyword}%"
    # 企业
    ents = query("SELECT * FROM enterprises WHERE name LIKE :q OR industry LIKE :q OR description LIKE :q",
                 {"q": kw})
    for e in ents:
        results.append({"type": "enterprise", "id": f"ent_{e['id']}", "name": e['name'], "industry": e['industry']})
    # 产业链
    chains = query("SELECT * FROM industry_chains WHERE chain_name LIKE :q OR description LIKE :q",
                   {"q": kw})
    for c in chains:
        results.append({"type": "chain", "id": f"chain_{c['id']}", "name": c['chain_name']})
    # 招商
    invs = query("SELECT * FROM investments WHERE enterprise_name LIKE :q OR industry LIKE :q",
                 {"q": kw})
    for inv in invs:
        results.append({"type": "investment", "id": f"inv_{inv['id']}", "name": inv['enterprise_name'], "industry": inv.get('industry','')})
    # 基建
    infras = query("SELECT * FROM infrastructure WHERE name LIKE :q OR description LIKE :q",
                   {"q": kw})
    for inf in infras:
        results.append({"type": "infrastructure", "id": f"infra_{inf['id']}", "name": inf['name']})
    return results


def get_analysis() -> dict:
    """产业分析 - 缺口/互补/经济影响"""
    chains = query("SELECT * FROM industry_chains")
    analysis = {"chain_gaps": [], "city_relations": [], "economic_impact": [], "suggestions": []}

    # 产业链分析
    for c in chains:
        e_count = query_one("SELECT COUNT(*) as cnt FROM chain_relations WHERE chain_id=:id", {"id": c['id']})['cnt']
        inv_count = query_one("SELECT COUNT(*) as cnt FROM investments WHERE chain_id=:id", {"id": c['id']})['cnt']
        eco = query("SELECT * FROM economic_impact WHERE chain_id=:id ORDER BY year", {"id": c['id']})
        analysis["chain_gaps"].append({
            "chain_name": c['chain_name'],
            "category": c['category'],
            "existing_enterprises": e_count,
            "new_investments": inv_count,
            "economic_impacts": eco
        })

    # 缺口建议
    analysis["suggestions"] = [
        {"chain": "纺织服装产业链", "gap": "高端面料研发环节薄弱", "suggestion": "引入功能性面料、智能纺织企业"},
        {"chain": "纺织服装产业链", "gap": "品牌设计环节缺失", "suggestion": "引进服装设计工作室、时尚品牌总部"},
        {"chain": "陶瓷建材产业链", "gap": "绿色低碳技术不足", "suggestion": "引入碳捕集、固废利用技术企业"},
        {"chain": "装备制造产业链", "gap": "核心零部件依赖外购", "suggestion": "引入精密零部件、伺服电机等上游企业"},
        {"chain": "食品饮料产业链", "gap": "冷链物流配套不足", "suggestion": "引入专业化冷链物流企业"},
        {"chain": "新材料产业链", "gap": "研发成果转化平台缺失", "suggestion": "建中试基地、引入高校科研分支机构"},
        {"chain": "现代物流产业链", "gap": "临空高附加值加工缺失", "suggestion": "引入航空食品、保税加工等临空产业"},
        {"chain": "电子信息产业链", "gap": "规模较小、集聚度低", "suggestion": "引入PCB、半导体封装等配套环节"},
    ]

    # 城市关系
    analysis["city_relations"] = query("SELECT * FROM city_relations")

    # 经济影响汇总
    for year in [2025, 2030]:
        rows = query("SELECT SUM(output_value) as total_output, SUM(employment) as total_emp, SUM(gdp_contribution) as total_gdp FROM economic_impact WHERE year=:id", {"id": year})
        if rows:
            analysis["economic_impact"].append({"year": year, **rows[0]})

    return analysis


if __name__ == "__main__":
    from data_collector import seed_database
    seed_database()
    data = get_graph_data()
    print(f"节点数: {len(data['nodes'])}, 边数: {len(data['edges'])}")
    with open(os.path.join(os.path.dirname(__file__), "..", "data", "graph_data.json"), "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("图谱数据已保存到 data/graph_data.json")
