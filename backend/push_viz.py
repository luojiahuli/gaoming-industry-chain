"""生成产业链图谱截图/HTML并推送到飞书"""
import os, sys, json, io, base64, webbrowser
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from graph_builder import get_graph_data, build_graph, get_analysis
from pyvis.network import Network
import networkx as nx


OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_pyvis_html(output_path=None) -> str:
    """生成 PyVis 交互式 HTML 图谱文件"""
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, "gaoming_graph.html")

    G = build_graph()
    net = Network(height="800px", width="100%", directed=True, bgcolor="#1a1a2e", font_color="white")

    # 节点颜色映射
    color_map = {"enterprise": "#4A90D9", "chain": "#E8A838", "investment": "#E85A5A",
                 "infrastructure": "#7BC47F", "city": "#9B59B6"}
    size_map = {"enterprise": 25, "chain": 40, "investment": 20, "infrastructure": 30, "city": 15}

    for node, attrs in G.nodes(data=True):
        ntype = attrs.get("type", "unknown")
        label = attrs.get("label", node)
        title_parts = [f"<b>{label}</b>", f"类型: {ntype}"]
        if attrs.get("industry"): title_parts.append(f"行业: {attrs['industry']}")
        if attrs.get("revenue"): title_parts.append(f"年营收: {attrs['revenue']}亿元")
        if attrs.get("employees"): title_parts.append(f"员工: {attrs['employees']}人")
        if attrs.get("amount"): title_parts.append(f"投资: {attrs['amount']}亿元")
        if attrs.get("stage"): title_parts.append(f"阶段: {attrs['stage']}")
        if attrs.get("status"): title_parts.append(f"状态: {attrs['status']}")
        if attrs.get("description"): title_parts.append(f"<br>{attrs['description'][:100]}")

        net.add_node(
            node, label=label, title="<br>".join(title_parts),
            color=color_map.get(ntype, "#666"),
            size=size_map.get(ntype, 20),
            font={"size": 14, "color": "#eee"}
        )

    for u, v, attrs in G.edges(data=True):
        color = attrs.get("color", "#555")
        width = attrs.get("weight", 1) * 2
        label = attrs.get("label", attrs.get("role", ""))
        net.add_edge(u, v, color=color, width=width, title=label or None)

    net.set_options("""
    var options = {
        "physics": {
            "enabled": true,
            "stabilization": {"iterations": 200},
            "barnesHut": {"gravitationalConstant": -3000, "centralGravity": 0.3, "springLength": 150}
        },
        "edges": {"smooth": {"type": "continuous"}},
        "interaction": {"hover": true, "tooltipDelay": 200}
    }
    """)
    net.save_graph(output_path)
    print(f"[PyVis] 图谱已保存: {output_path}")
    return output_path


def generate_static_summary(output_path=None) -> str:
    """生成纯文本格式的产业链摘要（用于飞书推送）"""
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, "industry_summary.json")

    analysis = get_analysis()
    graph_data = get_graph_data()

    summary = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "overview": {
            "total_enterprises": sum(1 for n in graph_data["nodes"] if n["type"] == "enterprise"),
            "total_chains": sum(1 for n in graph_data["nodes"] if n["type"] == "chain"),
            "total_investments": sum(1 for n in graph_data["nodes"] if n["type"] == "investment"),
            "total_infrastructures": sum(1 for n in graph_data["nodes"] if n["type"] == "infrastructure"),
        },
        "economic_impact": analysis["economic_impact"],
        "chain_gaps": analysis["chain_gaps"],
        "suggestions": analysis["suggestions"],
        "city_relations": analysis["city_relations"],
    }
    with open(output_path, "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"[摘要] 产业摘要已保存: {output_path}")
    return output_path


def push_to_feishu(webhook_url: str = None):
    """推送产业图谱报告到飞书"""
    if webhook_url is None:
        webhook_url = os.environ.get("FEISHU_WEBHOOK_URL", "")
        if not webhook_url or "YOUR_WEBHOOK" in webhook_url:
            print("[!] 请设置环境变量 FEISHU_WEBHOOK_URL 或在脚本中传入 webhook_url")
            return False

    import requests
    analysis = get_analysis()

    from graph_builder import get_analysis
    analysis = get_analysis()
    gd = get_graph_data()
    stats = {
        "enterprises": sum(1 for n in gd['nodes'] if n['type'] == 'enterprise'),
        "chains": sum(1 for n in gd['nodes'] if n['type'] == 'chain'),
        "investments": sum(1 for n in gd['nodes'] if n['type'] == 'investment'),
        "opportunities": sum(1 for n in gd['nodes'] if n['type'] == 'opportunity'),
        "infrastructures": sum(1 for n in gd['nodes'] if n['type'] == 'infrastructure'),
    }

    # 构建机会点表格行
    opp_rows = []
    for opp in analysis.get("opportunities", []):
        emoji = "🔴" if opp['priority'] == '高' else "🟡"
        opp_rows.append(f"{emoji} **{opp['chain_name']}**: {opp['name']}（{opp['estimated_investment']}）")

    # 构建城市流动行
    flow_rows = []
    arrow_map = {"上游":"←","下游":"→","互补":"↔","合作":"⇄","竞争":"⚡"}
    for f in analysis.get("city_flows", []):
        arr = arrow_map.get(f['flow_type'],'-')
        flow_rows.append(f"{f['city']} {arr} {f['chain_name']}（{f['flow_type']}）")

    # 企业分析行
    ent_analysis_rows = []
    for ea in analysis.get("enterprise_analysis", []):
        stages_str = " | ".join(f"{s['stage']}{s['count']}家" for s in ea.get('stage_distribution',[]))
        ent_analysis_rows.append(f"• **{ea['chain_name']}**: {ea['total_enterprises']}家企业, {ea['total_revenue']}亿产值, {ea['total_employees']}人\n  {stages_str}")

    lines = [
        f"**🏭 高明区产业链知识图谱增强版**",
        f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"",
        f"**📊 数据概览**",
        f"• 现有企业: {stats['enterprises']} 家 | 产业链: {stats['chains']} 条",
        f"• 招商项目: {stats['investments']} 个 | 招商机会: {stats['opportunities']} 个",
        f"• 基础设施: {stats['infrastructures']} 项",
        f"• 知识图谱: {len(gd['nodes'])} 节点 | {len(gd['edges'])} 条关系",
        f"",
        f"**📈 经济影响**",
    ]
    for eco in analysis.get("economic_impact", []):
        lines.append(f"• {eco['year']}年: 总产值 {eco['total_output']}亿元 | GDP {eco['total_gdp']}亿元 | 就业 {eco['total_emp']}人")

    lines.extend([
        f"",
        f"**🔗 产业链招商机会 ({len(opp_rows)}个)**",
    ])
    lines.extend(opp_rows[:12])  # 最多12条

    lines.extend([
        f"",
        f"**🏙️ 城市产业链上下游流动 ({len(flow_rows)}条)**",
    ])
    lines.extend(flow_rows[:10])

    lines.extend([
        f"",
        f"**🏭 企业产业链分析**",
    ])
    lines.extend(ent_analysis_rows[:5])

    lines.extend([
        f"",
        f"**🏙️ 城市关系**",
    ])
    for cr in analysis.get("city_relations", []):
        lines.append(f"• {cr['city_name']} ({cr['relation_type']}): {cr['description'][:40]}...")

    lines.extend([
        f"",
        f"**🚄 基础设施**",
        f"• 广州新机场(珠三角枢纽): 2026.3动工，年旅客3000万人次",
        f"• 广湛高铁: 已通车，高明→广州15分钟",
        f"• 珠肇高铁+深南高铁: 建设中，预计2027年通车",
        f"",
        f"---",
        f"🖥️ 完整交互图谱: http://localhost:8001",
    ])

    content = "\n".join(lines)
    payload = {
        "msg_type": "interactive",
        "card": {
            "header": {"title": {"tag": "plain_text", "content": "🏭 高明区产业知识图谱日报"}, "template": "blue"},
            "elements": [{"tag": "markdown", "content": content}]
        }
    }
    try:
        resp = requests.post(webhook_url, json=payload, timeout=15)
        if resp.status_code == 200 and resp.json().get("code") == 0:
            print("[✅] 飞书推送成功")
            return True
        print(f"[!] 推送失败: {resp.text}")
        return False
    except Exception as e:
        print(f"[!] 推送异常: {e}")
        return False


def build_full_report():
    """生成完整的本地报告"""
    generate_pyvis_html()
    generate_static_summary()
    print("\n✅ 所有报告已生成!")
    print(f"  📄 交互图谱: file://{os.path.join(OUTPUT_DIR, 'gaoming_graph.html')}")
    print(f"  📊 数据摘要: file://{os.path.join(OUTPUT_DIR, 'industry_summary.json')}")


if __name__ == "__main__":
    import sys
    if "--push" in sys.argv:
        push_to_feishu()
    elif "--feishu" in sys.argv:
        push_to_feishu()
    else:
        build_full_report()
        # 自动打开浏览器
        webbrowser.open(f"file://{os.path.join(OUTPUT_DIR, 'gaoming_graph.html')}")
