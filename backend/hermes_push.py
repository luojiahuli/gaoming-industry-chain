"""使用 Hermes 飞书接口推送产业链知识图谱报告"""
import os, sys, json, ssl, urllib.request
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from graph_builder import get_graph_data, get_analysis

# 从 Hermes .env 读取飞书配置
ENV_PATH = os.path.expanduser("~/.hermes/.env")
FEISHU_APP_ID = FEISHU_APP_SECRET = FEISHU_CHAT_ID = ""
if os.path.exists(ENV_PATH):
    for line in open(ENV_PATH):
        if "=" in line:
            k, v = line.strip().split("=", 1)
            if k == "FEISHU_APP_ID": FEISHU_APP_ID = v
            if k == "FEISHU_APP_SECRET": FEISHU_APP_SECRET = v
            if k == "FEISHU_CHAT_ID": FEISHU_CHAT_ID = v

if not FEISHU_APP_ID or not FEISHU_APP_SECRET or not FEISHU_CHAT_ID:
    print("[!] 未找到 Hermes 飞书配置 (~/.hermes/.env)")
    print("    需要: FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_CHAT_ID")
    sys.exit(1)


def get_feishu_token():
    payload = json.dumps({"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}).encode()
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=payload, headers={"Content-Type": "application/json"}
    )
    resp = json.loads(urllib.request.urlopen(req, timeout=30, context=ctx).read())
    return resp.get("tenant_access_token", "")


def send_feishu_card(token, header_title, elements):
    payload = json.dumps({
        "receive_id": FEISHU_CHAT_ID,
        "msg_type": "interactive",
        "content": json.dumps({
            "header": {"title": {"tag": "plain_text", "content": header_title}, "template": "blue"},
            "elements": elements
        })
    }).encode()
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    )
    resp = json.loads(urllib.request.urlopen(req, timeout=30, context=ctx).read())
    if resp.get("code") == 0:
        print(f"[✅] 飞书推送成功!")
    else:
        print(f"[!] 推送失败: {resp.get('msg','')}")
        if resp.get('code') == 99991663:
            print("    → 消息内容过长，请适当缩减")
    return resp


def build_report():
    gd = get_graph_data()
    analysis = get_analysis()
    stats = {
        "enterprises": sum(1 for n in gd['nodes'] if n['type'] == 'enterprise'),
        "chains": sum(1 for n in gd['nodes'] if n['type'] == 'chain'),
        "investments": sum(1 for n in gd['nodes'] if n['type'] == 'investment'),
        "opportunities": sum(1 for n in gd['nodes'] if n['type'] == 'opportunity'),
        "infras": sum(1 for n in gd['nodes'] if n['type'] == 'infrastructure'),
        "nodes": len(gd['nodes']), "edges": len(gd['edges']),
    }
    elements = []

    # 1. 概览
    elements.append({"tag": "markdown", "content": (
        f"**📊 数据概览**\n"
        f"🏢 企业 {stats['enterprises']}家 · ⛓️ 产业链 {stats['chains']}条\n"
        f"📋 招商 {stats['investments']}项 · 🎯 机会 {stats['opportunities']}个\n"
        f"🏗️ 基建 {stats['infras']}项 · 🔗 图谱 {stats['nodes']}节点/{stats['edges']}边\n"
        f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )})

    # 2. 经济影响
    eco_lines = ["**📈 经济影响预测**"]
    for e in analysis.get("economic_impact", []):
        eco_lines.append(f"• {e['year']}: 产值 {e['total_output']}亿 · GDP {e['total_gdp']}亿 · 就业 {e['total_emp']}人")
    elements.append({"tag": "markdown", "content": "\n".join(eco_lines)})

    # 3. 企业分析 (top 5 chains)
    ent_lines = ["**🏭 重点产业链企业分布**"]
    for ea in analysis.get("enterprise_analysis", [])[:5]:
        stages = " | ".join(f"{s['stage']}{s['count']}家" for s in ea.get('stage_distribution',[]))
        ent_lines.append(f"• **{ea['chain_name']}**: {ea['total_enterprises']}家/{ea['total_revenue']}亿\n  {stages}")
    elements.append({"tag": "markdown", "content": "\n".join(ent_lines)})

    # 4. 高优先级机会
    high_opps = [o for o in analysis.get("opportunities", []) if o['priority'] == '高']
    if high_opps:
        opp_lines = ["**🔴 高优先级招商机会**"]
        for o in high_opps:
            opp_lines.append(f"• **{o['chain_name']}**: {o['name']}\n  💰 {o['estimated_investment']} · 🎯 {o['target_enterprises'][:30]}")
        elements.append({"tag": "markdown", "content": "\n".join(opp_lines)})

    # 5. 城市上下游 (top 8)
    flow_lines = ["**🏙️ 城市产业链上下游**"]
    arrow = {"上游":"←供应","下游":"→销售","互补":"↔","合作":"⇄","竞争":"⚡"}
    for f in analysis.get("city_flows", [])[:8]:
        arr = arrow.get(f['flow_type'], f['flow_type'])
        flow_lines.append(f"• {f['city']} {arr} {f['chain_name']}")
    elements.append({"tag": "markdown", "content": "\n".join(flow_lines)})

    # 6. 基建
    elements.append({"tag": "markdown", "content": (
        "**🚄 基建动态**\n"
        "• 广州新机场: 2026.3动工 · 年旅客3000万\n"
        "• 广湛高铁: 已通车 · 高明→广州15min\n"
        "• 珠肇/深南高铁: 在建 · 2027通车\n"
        "• 西江黄金水道: 高明港升级5000吨级"
    )})

    return elements


def push():
    print("[Hermes] 获取飞书 Token...")
    token = get_feishu_token()
    if not token:
        print("[!] Token获取失败")
        return False
    print(f"[Hermes] 构建产业报告 (图谱 {sum(1 for n in get_graph_data()['nodes'] if n['type']=='enterprise')}家企业)...")
    elements = build_report()
    print(f"[Hermes] 推送中 ({len(elements)} 个模块)...")
    send_feishu_card(token, "🏭 高明区产业链知识图谱增强版", elements)
    return True


if __name__ == "__main__":
    push()
