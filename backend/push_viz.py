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

    lines = [
        f"**🏭 高明区产业链知识图谱日报**",
        f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"",
        f"**📊 数据概览**",
        f"• 现有企业: {sum(1 for n in get_graph_data()['nodes'] if n['type'] == 'enterprise')} 家",
        f"• 产业链: 9 条（含纺织、陶瓷、装备、食品、新材料、物流、电子信息、智能家居、电力装备）",
        f"• 招商项目: 19 个",
        f"• 基础设施: 7 项（机场·2026.3动工、广湛高铁·已通车等）",
        f"",
        f"**📈 经济影响**",
    ]
    for eco in analysis.get("economic_impact", []):
        lines.append(f"• {eco['year']}年: 总产值 {eco['total_output']}亿元 | GDP {eco['total_gdp']}亿元 | 就业 {eco['total_emp']}人")

    lines.extend([
        f"",
        f"**🔗 产业链缺口建议**",
    ])
    for s in analysis.get("suggestions", []):
        lines.append(f"• **{s['chain']}**: {s['suggestion']}")

    lines.extend([
        f"",
        f"**🏙️ 城市关系**",
    ])
    for cr in analysis.get("city_relations", []):
        lines.append(f"• {cr['city_name']} ({cr['relation_type']}): {cr['description'][:50]}...")

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
