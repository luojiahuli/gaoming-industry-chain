"""热门行业抓取与匹配模块
提供国内国际热门行业关键词列表，支持筛选匹配图谱中的企业/产业链/招商/机会点
"""
import requests
import json
from typing import Optional

# ── 热门行业分类 ─────────────────────────────────────────────
DOMESTIC_HOT = [
    {"name":"低空经济","keywords":["低空经济","无人机","eVTOL","飞行汽车","空域管理"]},
    {"name":"商业航天","keywords":["商业航天","卫星","火箭","太空","航天"]},
    {"name":"具身智能","keywords":["具身智能","人形机器人","足式机器人","灵巧手"]},
    {"name":"固态电池","keywords":["固态电池","半固态","锂金属","下一代电池"]},
    {"name":"AI大模型","keywords":["大模型","AI","人工智能","智算","算力","深度学习"]},
    {"name":"量子计算","keywords":["量子计算","量子","量子比特"]},
    {"name":"生物制造","keywords":["生物制造","合成生物","基因编辑","生物医药"]},
    {"name":"自动驾驶","keywords":["自动驾驶","无人驾驶","智能网联","车路协同"]},
    {"name":"氢能","keywords":["氢能","燃料电池","电解水","储氢","绿氢"]},
    {"name":"新型储能","keywords":["储能","锂电池","钠离子","液流电池","电力系统"]},
]

INTERNATIONAL_HOT = [
    {"name":"AI Chip","keywords":["AI芯片","GPU","HBM","Chiplet","半导体","芯片"]},
    {"name":"Nuclear Fusion","keywords":["核聚变","聚变","核能"]},
    {"name":"Brain-Computer","keywords":["脑机接口","BCI","脑科学","神经接口"]},
    {"name":"Robotics","keywords":["机器人","协作机器人","工业机器人","服务机器人"]},
    {"name":"SaaS/AI应用","keywords":["SaaS","AI应用","企业软件","云计算","企业服务"]},
    {"name":"Climate Tech","keywords":["气候科技","碳捕集","碳交易","碳达峰","碳中和"]},
    {"name":"Advanced Materials","keywords":["新材料","复合材料","超材料","纳米材料","碳纤维"]},
    {"name":"Smart Manufacturing","keywords":["智能制造","工业4.0","数字孪生","工业互联网","柔性制造"]},
]

HOT_INDUSTRIES = DOMESTIC_HOT + INTERNATIONAL_HOT


# ── 热门行业实时抓取 ─────────────────────────────────────────

def scrape_36kr_hot() -> list:
    """尝试从36氪抓取热门行业话题（不阻塞，失败返回空）"""
    try:
        resp = requests.get(
            "https://36kr.com/api/newsflash",
            params={"per_page": 20},
            timeout=5,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("data", {}).get("items", [])
            topics = set()
            for item in items:
                title = item.get("title", "")
                if title:
                    topics.add(title[:30])
            return list(topics)[:10]
    except Exception:
        pass
    return []


def scrape_huxiu_hot() -> list:
    """尝试从虎嗅抓取热门话题"""
    try:
        resp = requests.get(
            "https://m.huxiu.com/article",
            timeout=5,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        if resp.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "lxml")
            titles = []
            for a in soup.select("h3 a, .article-title a, .transition")[:10]:
                t = a.get_text(strip=True)
                if t and len(t) > 5:
                    titles.append(t[:40])
            return titles
    except Exception:
        pass
    return []


def scrape_and_update():
    """尝试抓取实时热门话题并更新到HOT_INDUSTRIES"""
    results = scrape_36kr_hot() + scrape_huxiu_hot()
    if results:
        print(f"[热门行业] 抓取到 {len(results)} 条实时话题")
    return results


# ── 匹配逻辑 ─────────────────────────────────────────────────

def match_industry_keywords(industry: str) -> list:
    """返回给定行业的搜索关键词列表"""
    for item in HOT_INDUSTRIES:
        if item["name"] == industry:
            return item["keywords"]
    # 模糊匹配
    for item in HOT_INDUSTRIES:
        if industry.lower() in item["name"].lower():
            return item["keywords"]
    return [industry]


if __name__ == "__main__":
    print(f"国内热门行业: {len(DOMESTIC_HOT)} 个")
    print(f"国际热门行业: {len(INTERNATIONAL_HOT)} 个")
    print(f"总计: {len(HOT_INDUSTRIES)} 个")
    print("\n抓取36氪热门...")
    titles = scrape_36kr_hot()
    for t in titles:
        print(f"  - {t}")
    print("\n抓取虎嗅热门...")
    titles = scrape_huxiu_hot()
    for t in titles:
        print(f"  - {t}")
