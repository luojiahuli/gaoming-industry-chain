# 🏭 高明区产业链知识图谱

基于 NetworkX + FastAPI + D3.js 的高明区产业知识图谱系统，整合企业数据、招商引资、基建规划（高铁/机场），提供产业链全景分析和可视化。

## 功能

| 模块 | 功能 |
|------|------|
| **企业图谱** | 展示高明区现有企业分布及所属产业链，节点可点击查看详情 |
| **产业链分析** | 7 大产业链（纺织、陶瓷、装备制造、食品饮料、新材料、物流、电子） |
| **招商引资** | 已落实招商项目及其在产业链中的位置 |
| **基建影响** | 珠三角枢纽机场、广湛高铁、珠肇高铁等基建项目的产业带动分析 |
| **城市关系** | 与广州、佛山、深圳、东莞等城市的互补/竞争/合作分析 |
| **经济预测** | 2025/2030 年各产业链产值、就业、GDP 贡献预测 |
| **智能搜索** | 支持企业、产业链、项目名称搜索 |
| **飞书推送** | 自动推送产业链图谱日报到飞书群 |

## 快速启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动后端（自动初始化数据）
python3 backend/main.py

# 3. 打开浏览器
open http://localhost:8000
```

## 项目结构

```
gaoming-industry-chain/
├── backend/
│   ├── main.py              # FastAPI 后端入口
│   ├── database.py          # SQLite 数据库模型
│   ├── data_collector.py    # 数据采集（企业/招商/基建）
│   ├── graph_builder.py     # NetworkX 知识图谱构建
│   └── feishu_bot.py        # 飞书推送机器人
├── frontend/
│   ├── index.html           # 前端页面
│   ├── style.css            # 深色主题样式
│   └── app.js               # D3.js 力导向图 + 交互
├── data/                    # SQLite 数据库存放目录
├── requirements.txt
└── README.md
```

## 飞书推送

```bash
# 设置飞书 Webhook（或修改 feishu_push.py）
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook"

# 推送产业链日报
python3 backend/feishu_bot.py
```

## 数据来源

- 高明区人民政府公开信息
- 佛山市招商局公开项目
- 广东省铁路/交通建设规划
- 天眼查/企查查公开企业信息

## 技术栈

- 后端: Python, FastAPI, NetworkX, SQLite
- 前端: D3.js Force-Directed Graph
- 推送: 飞书自定义机器人 Webhook
