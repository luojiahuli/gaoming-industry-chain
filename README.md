# 🏭 高明区产业链知识图谱

基于 NetworkX + FastAPI + D3.js 的高明区产业知识图谱系统，整合企业数据、招商引资、基建规划（广州新机场/广湛高铁），提供产业链全景分析和交互式可视化。

## 数据规模

| 指标 | 数值 |
|------|------|
| 企业 | 47 家（含纺织、陶瓷、装备、食品、新材料、物流、电子信息等） |
| 产业链 | 9 条（新增: 智能家居、新型电力系统装备） |
| 招商项目 | 19 个（2026年真实数据，总计超230亿） |
| 基础设施 | 7 项（机场/高铁/地铁/港口/高速） |
| 图谱节点 | 91 个 |
| 图谱关系 | 107 条 |

## 功能

- **企业图谱**: D3.js 力导向图展示企业/产业链/招商/基建/城市多维关系，节点可点击查看详情
- **产业链分析**: 9 大产业链全景分析，含缺口识别和引入建议
- **招商引资**: 已落实项目在产业链中的定位，与现有企业的协同关系
- **基建影响**: 广州新机场(2026.3动工)、广湛高铁(已通车)、珠肇高铁等产业带动
- **城市关系**: 广佛深莞珠等城市互补/竞争/合作分析
- **经济预测**: 2025→2027→2030 各产业链产值(1760亿)、就业(13.4万人)、GDP贡献(528亿)
- **智能搜索**: 企业/产业链/项目名称实时搜索
- **飞书推送**: 每日产业链分析推送到飞书群

## 快速启动

```bash
# 一键启动
./start.sh

# 或手动启动
pip install -r requirements.txt
python3 backend/main.py

# 打开浏览器访问 http://localhost:8001
```

## 生成可视化报告

```bash
# 生成交互式 HTML 图谱 + JSON 摘要
python3 backend/push_viz.py

# 推送到飞书
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook"
python3 backend/push_viz.py --push
```

## 项目结构

```
gaoming-industry-chain/
├── backend/
│   ├── main.py              # FastAPI 后端 API
│   ├── database.py          # SQLite 数据库层
│   ├── data_collector.py    # 企业/招商/基建真实数据
│   ├── graph_builder.py     # NetworkX 知识图谱 + 分析
│   ├── feishu_bot.py        # 飞书推送模块
│   └── push_viz.py          # 可视化生成 + 飞书推送
├── frontend/
│   ├── index.html           # D3.js 力导向图前端
│   ├── style.css            # 深色主题
│   └── app.js               # 图谱交互 + 搜索 + 分析
├── data/                    # 数据库和生成报告
├── start.sh                 # 一键启动脚本
├── requirements.txt
└── README.md
```

## GitHub 推送

```bash
# 创建 GitHub 仓库后:
git remote add origin https://github.com/你的用户名/gaoming-industry-chain.git
git push -u origin main
```

## 数据来源

- 高明区 2026 年高质量发展大会公开信息（34个/230亿签约项目）
- 南方日报/佛山新闻网 公开报道
- 广东省交通运输规划/铁路建设规划
- 企业公开工商信息

## 技术栈

- **后端**: Python 3.11, FastAPI, NetworkX, SQLite, PyVis
- **前端**: D3.js Force-Directed Graph, HTML5/CSS3
- **推送**: 飞书自定义机器人 Webhook
- **数据**: 2026年公开报道数据
