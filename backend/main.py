"""FastAPI 后端 - 高明区产业链知识图谱 API"""
import sys, os, json

sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from database import *
from graph_builder import (
    get_graph_data, get_enterprise_detail, get_chain_detail,
    search_graph, get_analysis, match_hot_industry
)
from data_collector import seed_database, scrape_gaoming_news

app = FastAPI(title="高明区产业链知识图谱", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# 初始化数据（首次运行）
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "gaoming.db")
if not os.path.exists(DB_PATH):
    print("[启动] 首次运行，初始化数据库...")
    seed_database()


# ── API 路由 ──────────────────────────────────────────────

@app.get("/api/graph")
def api_graph():
    """获取完整图谱数据 (Force-Directed JSON)"""
    return get_graph_data()


@app.get("/api/enterprise/{ent_id}")
def api_enterprise(ent_id: int):
    """企业详情"""
    detail = get_enterprise_detail(ent_id)
    if not detail:
        return JSONResponse({"error": "not found"}, 404)
    return detail


@app.get("/api/chain/{chain_id}")
def api_chain(chain_id: int):
    """产业链详情"""
    detail = get_chain_detail(chain_id)
    if not detail:
        return JSONResponse({"error": "not found"}, 404)
    return detail


@app.get("/api/search")
def api_search(q: str = Query("", min_length=1)):
    """搜索"""
    return search_graph(q)


@app.get("/api/analysis")
def api_analysis():
    """产业分析数据"""
    return get_analysis()


@app.get("/api/news")
def api_news():
    """抓取最新招商新闻"""
    return scrape_gaoming_news()


@app.get("/api/hot-industries")
def api_hot_industries():
    """获取热门行业列表"""
    from hot_industries import HOT_INDUSTRIES
    return {"industries": HOT_INDUSTRIES}


@app.get("/api/hot-industries/match")
def api_hot_match(industry: str = Query("", min_length=1)):
    """匹配热门行业到图谱节点"""
    result = match_hot_industry(industry)
    return result


@app.get("/api/stats")
def api_stats():
    """数据统计概览"""
    ent_count = query_one("SELECT COUNT(*) as c FROM enterprises")['c']
    chain_count = query_one("SELECT COUNT(*) as c FROM industry_chains")['c']
    inv_count = query_one("SELECT COUNT(*) as c FROM investments")['c']
    infra_count = query_one("SELECT COUNT(*) as c FROM infrastructure")['c']
    total_revenue = query_one("SELECT SUM(revenue_annual) as s FROM enterprises")['s'] or 0
    total_employees = query_one("SELECT SUM(employee_count) as s FROM enterprises")['s'] or 0
    return {
        "enterprises": ent_count,
        "chains": chain_count,
        "investments": inv_count,
        "infrastructures": infra_count,
        "total_revenue": round(total_revenue, 1),
        "total_employees": total_employees
    }


# ── 静态前端 ──────────────────────────────────────────────
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    print("🚀 启动高明区产业链知识图谱服务: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
