"""飞书推送模块 - 推送产业链知识图谱可视化到飞书"""
import sys, os, json, base64

sys.path.insert(0, os.path.dirname(__file__))

FEISHU_WEBHOOK_URL = os.environ.get("FEISHU_WEBHOOK_URL", "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_HERE")

# 如果存在本地的 feishu_push.py 配置，尝试读取 webhook
try:
    local_conf = os.path.join(os.path.dirname(__file__), "..", "..", "feishu_push.py")
    if os.path.exists(local_conf):
        import importlib.util
        spec = importlib.util.spec_from_file_location("feishu_conf", local_conf)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, 'FEISHU_WEBHOOK_URL') and 'YOUR_WEBHOOK' not in mod.FEISHU_WEBHOOK_URL:
            FEISHU_WEBHOOK_URL = mod.FEISHU_WEBHOOK_URL
except Exception:
    pass


def send_feishu(content: str, title: str = "高明区产业链知识图谱"):
    """推送文本消息到飞书"""
    if "YOUR_WEBHOOK_HERE" in FEISHU_WEBHOOK_URL:
        print("[!] 请设置 FEISHU_WEBHOOK_URL 环境变量或配置 feishu_push.py")
        return False
    try:
        import requests as req
        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {"title": {"tag": "plain_text", "content": title}, "template": "blue"},
                "elements": [{"tag": "markdown", "content": content}]
            }
        }
        resp = req.post(FEISHU_WEBHOOK_URL, json=payload, timeout=15)
        if resp.status_code == 200 and resp.json().get("code") == 0:
            print("[+] 飞书推送成功")
            return True
        print(f"[!] 飞书推送失败: {resp.text}")
        return False
    except Exception as e:
        print(f"[!] 推送失败: {e}")
        return False


def send_image_to_feishu(image_path: str, title: str = "高明区产业链图谱可视化"):
    """推送图片到飞书（图谱截图）"""
    if not os.path.exists(image_path):
        print(f"[!] 图片不存在: {image_path}")
        return False
    if "YOUR_WEBHOOK_HERE" in FEISHU_WEBHOOK_URL:
        print("[!] 请先设置 FEISHU_WEBHOOK_URL")
        return False
    try:
        import requests as req
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {"title": {"tag": "plain_text", "content": title}, "template": "blue"},
                "elements": [
                    {"tag": "markdown", "content": "**📊 高明区产业知识图谱**\n包含企业、产业链、招商、基建等节点关系"},
                    {"tag": "img", "img_key": img_b64}
                ]
            }
        }
        resp = req.post(FEISHU_WEBHOOK_URL, json=payload, timeout=30)
        if resp.status_code == 200 and resp.json().get("code") == 0:
            print("[+] 飞书图片推送成功")
            return True
        print(f"[!] 飞书图片推送失败: {resp.text}")
        return False
    except Exception as e:
        print(f"[!] 推送失败: {e}")
        return False


def build_industry_report() -> str:
    """构建产业链日报文本"""
    from graph_builder import get_analysis
    analysis = get_analysis()
    lines = [
        f"**🏭 高明区产业知识图谱日报**",
        f"---",
        f"**📊 经济影响预测**",
    ]
    for eco in analysis.get("economic_impact", []):
        lines.append(f"- {eco['year']}年: 总产值 {eco['total_output']}亿元, 就业 {eco['total_emp']}人, GDP贡献 {eco['total_gdp']}亿元")
    lines.append(f"\n**🔗 产业链缺口与建议**")
    for s in analysis.get("suggestions", [])[:5]:
        lines.append(f"- **{s['chain']}**: {s['gap']} → *{s['suggestion']}*")
    lines.append(f"\n**🏙️ 周边城市关系**")
    for cr in analysis.get("city_relations", []):
        emoji = {"互补": "🔄", "竞争": "⚔️", "合作": "🤝"}.get(cr['relation_type'], "🔗")
        lines.append(f"- {emoji} {cr['city_name']}: {cr['relation_type']}({cr['industry']}) - {cr['description']}")
    lines.append(f"\n---\n🖥️ 完整图谱访问: http://localhost:8000")
    return "\n".join(lines)


def push_report():
    """推送完整报告到飞书"""
    content = build_industry_report()
    return send_feishu(content, "高明区产业链知识图谱日报")


if __name__ == "__main__":
    push_report()
