"""SQLite 数据库层 - 存储企业、产业链、招商等信息"""
import sqlite3, json, os
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "gaoming.db")


def get_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """初始化所有表"""
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS enterprises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            industry TEXT NOT NULL,          -- 所属行业
            sub_industry TEXT,               -- 细分领域
            chain_stage TEXT,                -- 产业链环节: 上游/中游/下游/配套
            scale TEXT DEFAULT '中小微',      -- 规模
            revenue_annual REAL,             -- 年营收(亿元)
            employee_count INTEGER,          -- 员工数
            address TEXT,
            source TEXT DEFAULT '已知企业',    -- 数据来源
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS industry_chains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chain_name TEXT UNIQUE NOT NULL,  -- 产业链名称
            category TEXT NOT NULL,           -- 类别: 传统/新兴/配套
            description TEXT,
            surrounding_cities TEXT           -- 周边城市 JSON
        );

        CREATE TABLE IF NOT EXISTS chain_relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enterprise_id INTEGER NOT NULL,
            chain_id INTEGER NOT NULL,
            role TEXT,                       -- 角色: 核心/配套/上下游
            FOREIGN KEY (enterprise_id) REFERENCES enterprises(id),
            FOREIGN KEY (chain_id) REFERENCES industry_chains(id)
        );

        CREATE TABLE IF NOT EXISTS investments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enterprise_name TEXT NOT NULL,
            industry TEXT,
            chain_id INTEGER,
            amount REAL,                     -- 投资额(亿元)
            stage TEXT DEFAULT '已签约',       -- 阶段: 已签约/在建/已投产
            source TEXT,                     -- 信息来源
            announced_date TEXT,
            description TEXT,
            FOREIGN KEY (chain_id) REFERENCES industry_chains(id)
        );

        CREATE TABLE IF NOT EXISTS infrastructure (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            infra_type TEXT NOT NULL,         -- 高铁/机场/高速/港口
            status TEXT DEFAULT '规划中',      -- 规划中/建设中/已运营
            description TEXT,
            impact_areas TEXT,               -- 影响产业领域(JSON)
            planned_completion TEXT,
            source TEXT
        );

        CREATE TABLE IF NOT EXISTS city_relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_name TEXT NOT NULL,
            relation_type TEXT NOT NULL,       -- 互补/竞争/合作
            industry TEXT,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS economic_impact (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chain_id INTEGER,
            year INTEGER,
            output_value REAL,               -- 产值(亿元)
            employment INTEGER,              -- 带动就业(人)
            gdp_contribution REAL,           -- GDP贡献(亿元)
            description TEXT,
            FOREIGN KEY (chain_id) REFERENCES industry_chains(id)
        );

        CREATE TABLE IF NOT EXISTS city_chain_flows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chain_id INTEGER NOT NULL,
            city TEXT NOT NULL,
            flow_type TEXT NOT NULL,          -- 上游/下游/合作/互补/竞争
            description TEXT,
            FOREIGN KEY (chain_id) REFERENCES industry_chains(id)
        );

        CREATE TABLE IF NOT EXISTS investment_opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chain_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            category TEXT,
            gap_type TEXT DEFAULT 'general',  -- general/供应链缺口/技术缺口/上游缺口/下游缺口
            estimated_investment TEXT,
            priority TEXT DEFAULT '中',
            description TEXT,
            target_enterprises TEXT,
            FOREIGN KEY (chain_id) REFERENCES industry_chains(id)
        );
        """)
    print("[DB] 数据库初始化完成")


# ── CRUD 操作 ──────────────────────────────────────────────

def add_enterprise(**kw) -> int:
    kw.setdefault("description", "")
    kw.setdefault("sub_industry", "")
    kw.setdefault("chain_stage", "")
    kw.setdefault("scale", "中小微")
    kw.setdefault("revenue_annual", 0)
    kw.setdefault("employee_count", 0)
    kw.setdefault("address", "")
    kw.setdefault("source", "公开信息")
    sql = """INSERT OR IGNORE INTO enterprises
        (name,industry,sub_industry,chain_stage,scale,revenue_annual,employee_count,address,source,description)
        VALUES (:name,:industry,:sub_industry,:chain_stage,:scale,:revenue_annual,:employee_count,:address,:source,:description)"""
    with get_conn() as conn:
        cur = conn.execute(sql, kw)
        return cur.lastrowid or 0


def add_chain(**kw) -> int:
    sql = """INSERT OR IGNORE INTO industry_chains (chain_name,category,description,surrounding_cities)
        VALUES (:chain_name,:category,:description,:surrounding_cities)"""
    with get_conn() as conn:
        cur = conn.execute(sql, kw)
        return cur.lastrowid or 0


def add_investment(**kw) -> int:
    kw.setdefault("industry",""); kw.setdefault("chain_id",0); kw.setdefault("amount",0)
    kw.setdefault("stage","已签约"); kw.setdefault("source",""); kw.setdefault("announced_date","")
    kw.setdefault("description","")
    sql = """INSERT INTO investments (enterprise_name,industry,chain_id,amount,stage,source,announced_date,description)
        VALUES (:enterprise_name,:industry,:chain_id,:amount,:stage,:source,:announced_date,:description)"""
    with get_conn() as conn:
        cur = conn.execute(sql, kw)
        return cur.lastrowid or 0


def add_infrastructure(**kw) -> int:
    kw.setdefault("status","规划中"); kw.setdefault("description",""); kw.setdefault("impact_areas","[]")
    kw.setdefault("planned_completion",""); kw.setdefault("source","")
    sql = """INSERT INTO infrastructure (name,infra_type,status,description,impact_areas,planned_completion,source)
        VALUES (:name,:infra_type,:status,:description,:impact_areas,:planned_completion,:source)"""
    with get_conn() as conn:
        cur = conn.execute(sql, kw)
        return cur.lastrowid or 0


def query(sql: str, params: Optional[dict] = None) -> list:
    with get_conn() as conn:
        cur = conn.execute(sql, params or {})
        return [dict(r) for r in cur.fetchall()]


def query_one(sql: str, params: Optional[dict] = None) -> Optional[dict]:
    rows = query(sql, params)
    return rows[0] if rows else None
