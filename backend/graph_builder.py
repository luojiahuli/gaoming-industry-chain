"""NetworkX 知识图谱构建 - 高明区产业关系网络 (增强版)
包含: 企业/产业链/招商/基建/城市/机会点 六类节点
关系: 上下游/竞争/合作/互补/影响/入驻 七类边
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))

import networkx as nx
from database import *


def build_graph() -> nx.DiGraph:
    """构建完整产业知识图谱 (增强版)"""
    G = nx.DiGraph()
    enterprises = query("SELECT * FROM enterprises")
    chains = query("SELECT * FROM industry_chains")
    chain_map = {c['id']: f"chain_{c['id']}" for c in chains}

    # ── 1. 企业节点 ──────────────────────────────────────
    for e in enterprises:
        G.add_node(
            f"ent_{e['id']}",
            id=e['id'], type="enterprise", name=e['name'],
            industry=e['industry'], sub_industry=e.get('sub_industry',''),
            chain_stage=e.get('chain_stage',''), scale=e.get('scale',''),
            revenue=e.get('revenue_annual',0), employees=e.get('employee_count',0),
            address=e.get('address',''), source=e.get('source',''), description=e.get('description',''),
            label=e['name'], title=f"{e['name']} ({e['industry']})",
            size=min(60, max(20, e.get('revenue_annual',0) * 0.3 + 15)), color="#4A90D9"
        )

    # ── 2. 产业链节点 ────────────────────────────────────
    for c in chains:
        cid = f"chain_{c['id']}"
        G.add_node(
            cid, id=c['id'], type="chain", name=c['chain_name'],
            category=c['category'], description=c.get('description',''),
            surrounding_cities=json.loads(c.get('surrounding_cities','[]')) if isinstance(c.get('surrounding_cities'), str) else c.get('surrounding_cities',[]),
            label=c['chain_name'], title=c['chain_name'], size=50, color="#E8A838"
        )

    # ── 3. 企业→产业链 关联 ──────────────────────────────
    rels = query("""SELECT cr.*, e.name as ent_name, ic.chain_name
                    FROM chain_relations cr
                    JOIN enterprises e ON cr.enterprise_id=e.id
                    JOIN industry_chains ic ON cr.chain_id=ic.id""")
    for r in rels:
        G.add_edge(f"ent_{r['enterprise_id']}", chain_map.get(r['chain_id'], f"chain_{r['chain_id']}"),
                   type="belongs_to", role=r.get('role','配套'), weight=2)

    # ── 4. 企业间关系 (同产业链竞争/上下游协作) ────────
    # 同一产业链同环节=竞争, 不同环节=上下游协作
    from itertools import combinations
    for c in chains:
        cid = c['id']
        stage_ents = {}
        for e in enterprises:
            rel = query_one("SELECT role FROM chain_relations WHERE enterprise_id=:eid AND chain_id=:cid",
                           {"eid": e['id'], "cid": cid})
            if rel:
                stage = e.get('chain_stage','配套')
                stage_ents.setdefault(stage, []).append(e)

        for stage, ents in stage_ents.items():
            # 同环节竞争关系
            for e1, e2 in combinations(ents, 2):
                if e1['id'] != e2['id']:
                    G.add_edge(f"ent_{e1['id']}", f"ent_{e2['id']}",
                               type="competition", label="同业竞争", weight=0.5, color="#E74C3C")
                    break  # 每条链每环节只加一条竞争边,避免图太密

        # 上下游协作: 上游→中游→下游
        chain_stages_order = ["上游","中游","下游","配套"]
        for i in range(len(chain_stages_order)-1):
            up = stage_ents.get(chain_stages_order[i], [])
            down = stage_ents.get(chain_stages_order[i+1], [])
            if up and down:
                G.add_edge(f"ent_{up[0]['id']}", f"ent_{down[0]['id']}",
                           type="supply_chain", label=f"{chain_stages_order[i]}→{chain_stages_order[i+1]}",
                           weight=1.5, color="#2ECC71")

    # ── 5. 招商企业节点 ──────────────────────────────────
    invs = query("SELECT * FROM investments")
    for inv in invs:
        inv_id = f"inv_{inv['id']}"
        G.add_node(inv_id, id=inv['id'], type="investment",
                   name=inv['enterprise_name'], industry=inv.get('industry',''),
                   amount=inv.get('amount',0), stage=inv.get('stage',''),
                   source=inv.get('source',''), date=inv.get('announced_date',''),
                   description=inv.get('description',''),
                   label=inv['enterprise_name'], title=f"[招商] {inv['enterprise_name']}",
                   size=35, color="#E85A5A")
        if inv.get('chain_id') and inv['chain_id'] in chain_map:
            G.add_edge(inv_id, chain_map[inv['chain_id']], type="investment_in", role="招商入驻", weight=1.5)

    # ── 6. 基础设施节点 ──────────────────────────────────
    infras = query("SELECT * FROM infrastructure")
    for inf in infras:
        inf_id = f"infra_{inf['id']}"
        impact = json.loads(inf['impact_areas']) if isinstance(inf.get('impact_areas'), str) else inf.get('impact_areas',[])
        G.add_node(inf_id, id=inf['id'], type="infrastructure", name=inf['name'],
                   infra_type=inf['infra_type'], status=inf['status'],
                   description=inf.get('description',''), completion=inf.get('planned_completion',''),
                   impact_areas=impact, label=inf['name'], title=f"[基建] {inf['name']}",
                   size=40, color="#7BC47F")

    # 基建→产业链影响
    for inf in infras:
        impact = json.loads(inf['impact_areas']) if isinstance(inf.get('impact_areas'), str) else inf.get('impact_areas',[])
        inf_id = f"infra_{inf['id']}"
        for cid in chain_map:
            cn = query_one("SELECT chain_name FROM industry_chains WHERE id=:id", {"id": cid})
            if cn:
                for ia in impact:
                    if ia in cn['chain_name'] or cn['chain_name'].startswith(ia):
                        G.add_edge(inf_id, chain_map[cid], type="impacts", weight=2.5, color="#2ECC71")

    # ── 7. 周边城市节点 + 城市-产业链上下游关系 ────────
    cities_data = query("SELECT DISTINCT city_name FROM city_relations")
    for cd in cities_data:
        cname = cd['city_name']
        G.add_node(f"city_{cname}", type="city", name=cname, label=cname,
                   title=f"城市: {cname}", size=30, color="#9B59B6")

    # 城市关系边 (互补/竞争/合作)
    city_rels = query("SELECT * FROM city_relations")
    color_map_relation = {"互补": "#2ECC71", "竞争": "#E74C3C", "合作": "#3498DB"}
    for city in city_rels:
        cname = city['city_name']
        G.add_edge(f"city_{cname}", f"city_{cname}",
                   type="city_tag", relation_type=city['relation_type'],
                   industry=city['industry'], description=city.get('description',''),
                   color=color_map_relation.get(city['relation_type'], "#95A5A6"))

    # 城市-产业链 上下游流动边 (带方向!)
    flows = query("SELECT * FROM city_chain_flows")
    for f in flows:
        cname = f['city']
        cnode = chain_map.get(f['chain_id'])
        city_node = f"city_{cname}"
        if cnode and city_node in [n for n in G.nodes()]:
            flow_type = f['flow_type']
            if flow_type == "上游":
                # 城市给高明供原料 → 城市→产业链
                G.add_edge(city_node, cnode, type="city_chain_flow", flow_type="上游",
                           label=f"供应", description=f.get('description',''), weight=1.5, color="#3498DB")
            elif flow_type == "下游":
                # 高明产品卖给城市 → 产业链→城市
                G.add_edge(cnode, city_node, type="city_chain_flow", flow_type="下游",
                           label=f"销售", description=f.get('description',''), weight=1.5, color="#2ECC71")
            elif flow_type == "互补":
                G.add_edge(city_node, cnode, type="city_chain_flow", flow_type="互补",
                           label=f"互补", description=f.get('description',''), weight=1, color="#F39C12")
            else:  # 合作/竞争
                G.add_edge(city_node, cnode, type="city_chain_flow", flow_type=flow_type,
                           label=flow_type, description=f.get('description',''), weight=1, color="#95A5A6")

    # ── 8. 招商引资机会点节点 (含缺口分类) ──────────────
    ops = query("SELECT * FROM investment_opportunities")
    gap_type_colors = {
        "general": "#E67E22",      # 橙色 - 常规机会
        "供应链缺口": "#E74C3C",   # 红色 - 供应链风险
        "技术缺口": "#8E44AD",     # 紫色 - 技术缺失
        "上游缺口": "#3498DB",     # 蓝色 - 上游供应缺失
        "下游缺口": "#1ABC9C",     # 青色 - 下游市场缺失
    }
    for op in ops:
        op_id = f"opp_{op['id']}"
        gap_type = op.get('gap_type', 'general') or 'general'
        node_color = gap_type_colors.get(gap_type, "#E67E22")
        G.add_node(op_id, id=op['id'], type="opportunity",
                   name=op['name'], category=op.get('category',''),
                   gap_type=gap_type,
                   estimated_investment=op.get('estimated_investment',''),
                   priority=op.get('priority','中'),
                   target_enterprises=op.get('target_enterprises',''),
                   partner_enterprises=op.get('partner_enterprises',''),
                   partner_cities=op.get('partner_cities',''),
                   description=op.get('description',''),
                   label=op['name'][:15]+'…', title=f"[机会] {op['name']}",
                   size=28, color=node_color)
        # 机会→产业链
        if op['chain_id'] in chain_map:
            G.add_edge(op_id, chain_map[op['chain_id']], type="opportunity_in",
                       label=f"{op.get('estimated_investment','')}",
                       weight=1, color="#F39C12")

        # 机会→建议引入合作企业 (在图谱中查找同名节点)
        partner_ents = op.get('partner_enterprises', '')
        if partner_ents:
            try:
                partner_list = json.loads(partner_ents) if isinstance(partner_ents, str) else partner_ents
                for pname in partner_list:
                    # 尝试匹配企业节点
                    found = False
                    for n in G.nodes():
                        node_data = G.nodes[n]
                        if node_data.get('type') in ('enterprise', 'investment', 'infrastructure'):
                            # 检查节点标签或名称是否包含合作企业关键词
                            node_name = node_data.get('name', '') or node_data.get('label', '')
                            # 提取企业核心名称（去掉括号说明）
                            core = pname.split('（')[0].split('(')[0].strip()
                            if core and len(core) >= 2 and core in node_name:
                                G.add_edge(op_id, n, type="partner_intro",
                                          label="引入合作", weight=0.8, color="#2ECC71")
                                found = True
                                break
                    if not found:
                        # 未匹配到图谱内节点，添加虚拟合作节点
                        virtual_id = f"partner_{op['id']}_{hash(pname) % 10000}"
                        G.add_node(virtual_id, type="virtual_partner",
                                  name=pname, label=pname[:12]+'…' if len(pname) > 12 else pname,
                                  size=15, color="#2ECC71", opacity=0.6)
                        G.add_edge(op_id, virtual_id, type="partner_intro",
                                  label="引入合作", weight=0.5, color="#2ECC71")
            except (json.JSONDecodeError, TypeError):
                pass

        # 机会→合作城市
        partner_cities = op.get('partner_cities', '')
        if partner_cities:
            try:
                city_list = json.loads(partner_cities) if isinstance(partner_cities, str) else partner_cities
                for pcity in city_list:
                    # 提取城市名（去掉括号说明）
                    city_name = pcity.split('（')[0].split('(')[0].strip()
                    city_node_id = f"city_{city_name}"
                    if city_node_id in G:
                        G.add_edge(op_id, city_node_id, type="city_coop",
                                  label="城市合作", weight=0.8, color="#3498DB")
            except (json.JSONDecodeError, TypeError):
                pass

    # ── 9. 产业链间关联 (上下游价值链) ────────────────
    chain_deps = [
        ("chain_5", "chain_3", "新材料→装备制造"),
        ("chain_1", "chain_6", "纺织→物流"),
        ("chain_2", "chain_6", "陶瓷→物流"),
        ("chain_4", "chain_6", "食品→物流"),
        ("chain_5", "chain_2", "新材料→陶瓷"),
        ("chain_1", "chain_3", "纺织→纺织机械"),
        ("chain_7", "chain_3", "工业软件→智能装备"),
        ("chain_5", "chain_9", "新材料→电力装备"),
        ("chain_3", "chain_9", "精密制造→电力装备"),
        ("chain_4", "chain_3", "食品→食品机械"),
    ]
    for src, dst, label in chain_deps:
        if src in chain_map.values() and dst in chain_map.values():
            G.add_edge(src, dst, type="chain_link", label=label, weight=1.2, color="#95A5A6")

    print(f"[图谱] 图构建完成: {G.number_of_nodes()} 节点, {G.number_of_edges()} 条边")
    return G


def get_graph_data() -> dict:
    """导出为前端可用的 JSON"""
    G = build_graph()
    nodes, edges = [], []
    for n, attrs in G.nodes(data=True):
        node = {"id": n, **{k: v for k, v in attrs.items() if k != 'id'}}
        node.setdefault("label", n); node.setdefault("type", "unknown")
        node.setdefault("color", "#666"); node.setdefault("size", 20); node.setdefault("title", n)
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
        JOIN chain_relations cr ON cr.chain_id=ic.id WHERE cr.enterprise_id=:id""", {"id": ent_id})
    return {**e, "chains": chains}


def get_chain_detail(chain_id: int) -> dict:
    """获取产业链详情 (含机会点)"""
    c = query_one("SELECT * FROM industry_chains WHERE id=:id", {"id": chain_id})
    if not c:
        return {}
    ents = query("""SELECT e.* FROM enterprises e
        JOIN chain_relations cr ON cr.enterprise_id=e.id WHERE cr.chain_id=:id""", {"id": chain_id})
    invs = query("SELECT * FROM investments WHERE chain_id=:id", {"id": chain_id})
    impacts = query("SELECT * FROM infrastructure WHERE impact_areas LIKE :q", {"q": f"%{c.get('chain_name','')[:4]}%"})
    eco = query("SELECT * FROM economic_impact WHERE chain_id=:id", {"id": chain_id})
    opps = query("SELECT * FROM investment_opportunities WHERE chain_id=:id", {"id": chain_id})
    flows = query("SELECT * FROM city_chain_flows WHERE chain_id=:id", {"id": chain_id})
    return {**c, "enterprises": ents, "investments": invs, "infrastructure": impacts,
            "economic_impacts": eco, "opportunities": opps, "city_flows": flows}


def search_graph(keyword: str) -> list:
    """搜索企业/产业链/招商/机会点"""
    kw = f"%{keyword}%"
    results = []
    for label, table, id_prefix, name_col in [
        ("enterprise","enterprises","ent","name"),
        ("chain","industry_chains","chain","chain_name"),
        ("investment","investments","inv","enterprise_name"),
        ("infrastructure","infrastructure","infra","name"),
        ("opportunity","investment_opportunities","opp","name"),
    ]:
        rows = query(f"SELECT id, {name_col} as name FROM {table} WHERE {name_col} LIKE :q", {"q": kw})
        for r in rows:
            results.append({"type": label, "id": f"{id_prefix}_{r['id']}", "name": r['name']})
    return results


def match_hot_industry(industry: str) -> dict:
    """匹配热门行业关键词到图谱节点（搜索所有相关关键词）"""
    # 从 hot_industries 获取该行业的所有关键词
    try:
        from hot_industries import HOT_INDUSTRIES
        keywords = [industry]  # 默认用行业名称
        for item in HOT_INDUSTRIES:
            if item["name"] == industry:
                keywords = item["keywords"]
                break
    except ImportError:
        keywords = [industry]

    matches = {"enterprises": [], "chains": [], "investments": [], "opportunities": [], "node_ids": [], "matched_keywords": keywords}

    for kw in keywords:
        q = f"%{kw}%"
        rows = query("SELECT id, name FROM enterprises WHERE industry LIKE :q OR sub_industry LIKE :q OR description LIKE :q", {"q": q})
        for r in rows:
            nid = f"ent_{r['id']}"
            if nid not in matches["node_ids"]:
                matches["enterprises"].append(r)
                matches["node_ids"].append(nid)

        rows = query("SELECT id, chain_name as name FROM industry_chains WHERE chain_name LIKE :q OR description LIKE :q OR category LIKE :q", {"q": q})
        for r in rows:
            nid = f"chain_{r['id']}"
            if nid not in matches["node_ids"]:
                matches["chains"].append(r)
                matches["node_ids"].append(nid)

        rows = query("SELECT id, enterprise_name as name FROM investments WHERE industry LIKE :q OR description LIKE :q", {"q": q})
        for r in rows:
            nid = f"inv_{r['id']}"
            if nid not in matches["node_ids"]:
                matches["investments"].append(r)
                matches["node_ids"].append(nid)

        rows = query("SELECT id, name FROM investment_opportunities WHERE name LIKE :q OR description LIKE :q OR category LIKE :q OR target_enterprises LIKE :q", {"q": q})
        for r in rows:
            nid = f"opp_{r['id']}"
            if nid not in matches["node_ids"]:
                matches["opportunities"].append(r)
                matches["node_ids"].append(nid)

    matches["count"] = sum(len(v) for k, v in matches.items() if k not in ("node_ids", "matched_keywords"))
    return matches


def get_analysis() -> dict:
    """产业分析 - 缺口/机会/互补/经济影响"""
    chains = query("SELECT * FROM industry_chains")
    analysis = {"chain_gaps": [], "city_relations": [], "city_flows": [],
                "economic_impact": [], "suggestions": [], "opportunities": [],
                "enterprise_analysis": []}

    # 产业链综合分析
    for c in chains:
        e_count = query_one("SELECT COUNT(*) as cnt FROM chain_relations WHERE chain_id=:id", {"id": c['id']})['cnt']
        inv_count = query_one("SELECT COUNT(*) as cnt FROM investments WHERE chain_id=:id", {"id": c['id']})['cnt']
        opp_count = query_one("SELECT COUNT(*) as cnt FROM investment_opportunities WHERE chain_id=:id", {"id": c['id']})['cnt']
        eco = query("SELECT * FROM economic_impact WHERE chain_id=:id ORDER BY year", {"id": c['id']})
        flows = query("SELECT * FROM city_chain_flows WHERE chain_id=:id", {"id": c['id']})
        analysis["chain_gaps"].append({
            "chain_name": c['chain_name'], "category": c['category'],
            "existing_enterprises": e_count, "new_investments": inv_count,
            "opportunities": opp_count, "economic_impacts": eco, "city_flows": flows
        })

    # 缺口建议 (合并机会点)
    all_opps = query("""SELECT o.*, ic.chain_name FROM investment_opportunities o
        JOIN industry_chains ic ON o.chain_id=ic.id ORDER BY o.priority""")
    analysis["opportunities"] = all_opps
    analysis["suggestions"] = [
        {"chain": opp['chain_name'], "gap": opp['name'], "suggestion": f"引入{opp['target_enterprises']}, 预计投资{opp['estimated_investment']}",
         "priority": opp['priority']}
        for opp in all_opps
    ]

    # 城市产业链上下游
    analysis["city_flows"] = query("""SELECT ccf.*, ic.chain_name FROM city_chain_flows ccf
        JOIN industry_chains ic ON ccf.chain_id=ic.id ORDER BY ccf.city, ccf.flow_type""")

    # 城市关系
    analysis["city_relations"] = query("SELECT * FROM city_relations")

    # 企业分析: 按产业链和环节统计
    for c in chains:
        ents = query("""SELECT e.chain_stage, e.scale, e.revenue_annual, e.employee_count
            FROM enterprises e JOIN chain_relations cr ON cr.enterprise_id=e.id WHERE cr.chain_id=:id""", {"id": c['id']})
        total_rev = sum(e.get('revenue_annual',0) or 0 for e in ents)
        total_emp = sum(e.get('employee_count',0) or 0 for e in ents)
        stages = {}
        for e in ents:
            st = e.get('chain_stage','其他')
            stages.setdefault(st, {"count":0, "revenue":0, "employees":0})
            stages[st]["count"] += 1
            stages[st]["revenue"] += e.get('revenue_annual',0) or 0
            stages[st]["employees"] += e.get('employee_count',0) or 0
        analysis["enterprise_analysis"].append({
            "chain_name": c['chain_name'], "total_enterprises": len(ents),
            "total_revenue": round(total_rev, 1), "total_employees": total_emp,
            "stage_distribution": [{"stage": k, **v} for k, v in stages.items()]
        })

    # 经济影响汇总
    for year in [2025, 2027, 2030]:
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
