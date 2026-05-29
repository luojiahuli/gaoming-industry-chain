/* 高明区产业链知识图谱 - 前端可视化 */
const API_BASE = "/api";
let graphData = null;
let simulation = null;
let svg, g, zoom;

// ── 颜色映射 ──────────────────────────────────────────────
const COLORS = {
  enterprise: "#4A90D9",
  chain: "#E8A838",
  investment: "#E85A5A",
  infrastructure: "#7BC47F",
  city: "#9B59B6",
};

const TYPE_LABELS = {
  enterprise: "现有企业",
  chain: "产业链",
  investment: "招商项目",
  infrastructure: "基础设施",
  city: "周边城市",
};

// ── 初始化 ────────────────────────────────────────────────
async function init() {
  svg = d3.select("#graph-svg");
  g = svg.append("g");
  zoom = d3.zoom().scaleExtent([0.2, 4]).on("zoom", (e) => g.attr("transform", e.transform));
  svg.call(zoom);

  await loadData();
  loadStats();
}

async function loadData() {
  try {
    const resp = await fetch(`${API_BASE}/graph`);
    graphData = await resp.json();
    renderGraph();
  } catch (e) {
    console.error("加载数据失败:", e);
    // fallback: 后端可能未启动，尝试加载本地文件
    try {
      const resp = await fetch("/data/graph_data.json");
      graphData = await resp.json();
      renderGraph();
    } catch (e2) {
      document.querySelector("#graph-container").innerHTML = `
        <div style="text-align:center;padding:80px;color:#667;">
          <h2>⚠️ 无法加载图谱数据</h2>
          <p>请确保后端服务已启动: <code>python3 backend/main.py</code></p>
        </div>`;
    }
  }
}

async function loadStats() {
  try {
    const resp = await fetch(`${API_BASE}/stats`);
    const s = await resp.json();
    document.getElementById("stat-ent").textContent = s.enterprises || 0;
    document.getElementById("stat-chain").textContent = s.chains || 0;
    document.getElementById("stat-inv").textContent = s.investments || 0;
    document.getElementById("stat-infra").textContent = s.infrastructures || 0;
  } catch (e) { /* ignore */ }
}

// ── 力导向图渲染 ──────────────────────────────────────────
function renderGraph() {
  const { nodes, edges } = graphData;
  const container = document.getElementById("graph-container");
  const width = container.clientWidth;
  const height = container.clientHeight;

  svg.attr("width", width).attr("height", height);

  // 初始化位置
  const centerX = width / 2, centerY = height / 2;
  nodes.forEach((n, i) => {
    n.x = centerX + (Math.random() - 0.5) * width * 0.6;
    n.y = centerY + (Math.random() - 0.5) * height * 0.6;
  });

  // 边
  const link = g.selectAll("line").data(edges).join("line")
    .attr("stroke", (d) => d.color || "#2a3a4a")
    .attr("stroke-width", (d) => (d.weight || 1) * 1.5)
    .attr("stroke-opacity", 0.4)
    .attr("stroke-dasharray", (d) => d.type === "city_relation" ? "4,3" : "none");

  // 边标签
  const linkLabel = g.selectAll(".edge-label").data(edges.filter(d => d.label)).join("text")
    .attr("class", "edge-label")
    .text(d => d.label)
    .attr("font-size", 9)
    .attr("fill", "#556")
    .attr("text-anchor", "middle");

  // 节点组
  const node = g.selectAll(".node-group").data(nodes).join("g")
    .attr("class", "node-group")
    .call(d3.drag()
      .on("start", dragStart)
      .on("drag", dragMove)
      .on("end", dragEnd)
    )
    .on("click", (e, d) => nodeClick(e, d))
    .on("mouseenter", (e, d) => showTooltip(e, d))
    .on("mousemove", (e) => moveTooltip(e))
    .on("mouseleave", hideTooltip);

  // 圆
  node.append("circle")
    .attr("r", (d) => d.size || 20)
    .attr("fill", (d) => d.color || COLORS[d.type] || "#666")
    .attr("stroke", "#1a2a3a")
    .attr("stroke-width", 2)
    .attr("opacity", 0.9);

  // 标签
  node.append("text")
    .text((d) => truncate(d.label || d.name || d.id, 12))
    .attr("text-anchor", "middle")
    .attr("dy", (d) => (d.size || 20) + 14)
    .attr("font-size", 11)
    .attr("fill", "#aabbcc")
    .attr("font-weight", 500);

  // 高亮圈 (hover)
  node.append("circle")
    .attr("class", "halo")
    .attr("r", (d) => (d.size || 20) + 4)
    .attr("fill", "none")
    .attr("stroke", (d) => d.color || COLORS[d.type] || "#666")
    .attr("stroke-width", 0)
    .attr("opacity", 0);

  // 力模拟
  simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(edges).id((d) => d.id).distance(120).strength(0.3))
    .force("charge", d3.forceManyBody().strength(-400))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide().radius((d) => (d.size || 20) + 10))
    .on("tick", () => {
      link
        .attr("x1", (d) => d.source.x || d.source.x || 0)
        .attr("y1", (d) => d.source.y || d.source.y || 0)
        .attr("x2", (d) => d.target.x || d.target.x || 0)
        .attr("y2", (d) => d.target.y || d.target.y || 0);
      linkLabel
        .attr("x", (d) => ((d.source.x || d.source.x || 0) + (d.target.x || d.target.x || 0)) / 2)
        .attr("y", (d) => ((d.source.y || d.source.y || 0) + (d.target.y || d.target.y || 0)) / 2);
      node.attr("transform", (d) => `translate(${d.x},${d.y})`);
    });
}

function truncate(str, len) {
  return str && str.length > len ? str.slice(0, len) + ".." : str;
}

// ── 拖拽 ──────────────────────────────────────────────────
function dragStart(e, d) {
  if (!e.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x; d.fy = d.y;
}

function dragMove(e, d) {
  d.fx = e.x; d.fy = e.y;
}

function dragEnd(e, d) {
  if (!e.active) simulation.alphaTarget(0);
  d.fx = null; d.fy = null;
}

// ── Tooltip ────────────────────────────────────────────────
const tooltip = document.getElementById("tooltip");

function showTooltip(e, d) {
  const lines = [
    `<b>${d.label || d.name || d.id}</b>`,
    `类型: ${TYPE_LABELS[d.type] || d.type}`,
  ];
  if (d.industry) lines.push(`行业: ${d.industry}`);
  if (d.sub_industry) lines.push(`细分: ${d.sub_industry}`);
  if (d.chain_stage) lines.push(`环节: ${d.chain_stage}`);
  if (d.scale) lines.push(`规模: ${d.scale}`);
  if (d.revenue) lines.push(`年营收: ${d.revenue}亿元`);
  if (d.employees) lines.push(`员工: ${d.employees}人`);
  if (d.amount) lines.push(`投资额: ${d.amount}亿元`);
  if (d.stage) lines.push(`阶段: ${d.stage}`);
  if (d.infra_type) lines.push(`类型: ${d.infra_type}`);
  if (d.status) lines.push(`状态: ${d.status}`);
  tooltip.innerHTML = lines.join("<br>");
  tooltip.style.display = "block";
}

function moveTooltip(e) {
  const rect = document.getElementById("graph-container").getBoundingClientRect();
  tooltip.style.left = (e.clientX - rect.left + 12) + "px";
  tooltip.style.top = (e.clientY - rect.top - 10) + "px";
}

function hideTooltip() {
  tooltip.style.display = "none";
}

// ── 节点点击 → 详情面板 ──────────────────────────────────
async function nodeClick(e, d) {
  e.stopPropagation();
  const panel = document.getElementById("detail-panel");
  const content = document.getElementById("panel-content");
  panel.classList.remove("hidden");

  // 高亮
  g.selectAll(".node-group circle").attr("opacity", 0.3);
  g.selectAll(`.node-group`).filter((n) => n.id === d.id).select("circle").attr("opacity", 1);

  if (d.type === "enterprise") {
    try {
      const resp = await fetch(`${API_BASE}/enterprise/${d.id}`);
      const data = await resp.json();
      renderEnterpriseDetail(data);
    } catch(e) {
      content.innerHTML = `<p style="color:#E85A5A">加载失败: ${e.message}</p>`;
    }
  } else if (d.type === "chain") {
    try {
      const resp = await fetch(`${API_BASE}/chain/${d.id}`);
      const data = await resp.json();
      renderChainDetail(data);
    } catch(e) {
      content.innerHTML = `<p style="color:#E85A5A">加载失败: ${e.message}</p>`;
    }
  } else if (d.type === "investment") {
    renderInvestmentDetail(d);
  } else if (d.type === "infrastructure") {
    renderInfrastructureDetail(d);
  } else if (d.type === "city") {
    renderCityDetail(d);
  }
}

function renderEnterpriseDetail(data) {
  const el = document.getElementById("panel-content");
  el.innerHTML = `
    <div class="dp-header">
      <span class="dp-type enterprise">企业</span>
      <div class="dp-title">${data.name}</div>
      <div class="dp-sub">${data.industry} · ${data.sub_industry || ""} · ${data.chain_stage || ""}</div>
    </div>
    <div class="dp-section">
      <h3>基本信息</h3>
      <div class="dp-field"><span class="label">规模</span><span class="value">${data.scale || '-'}</span></div>
      <div class="dp-field"><span class="label">年营收</span><span class="value">${data.revenue_annual || 0} 亿元</span></div>
      <div class="dp-field"><span class="label">员工数</span><span class="value">${data.employee_count || 0} 人</span></div>
      <div class="dp-field"><span class="label">地址</span><span class="value">${data.address || '-'}</span></div>
      <div class="dp-field"><span class="label">数据来源</span><span class="value">${data.source || '-'}</span></div>
    </div>
    ${data.chains && data.chains.length ? `
    <div class="dp-section">
      <h3>所属产业链</h3>
      <ul class="dp-list">
        ${data.chains.map(c => `<li><span class="name">${c.chain_name}</span><span class="meta">[${c.category || ''}]</span></li>`).join('')}
      </ul>
    </div>` : ''}
    <div class="dp-section">
      <h3>相关新闻</h3>
      <p style="color:#667;font-size:13px;">🔍 搜索 "${data.name}" 查看更多资讯</p>
    </div>`;
}

function renderChainDetail(data) {
  let surrCities = data.surrounding_cities;
  try { surrCities = typeof surrCities === 'string' ? JSON.parse(surrCities) : surrCities; } catch(e) {}
  const el = document.getElementById("panel-content");
  el.innerHTML = `
    <div class="dp-header">
      <span class="dp-type chain">产业链</span>
      <div class="dp-title">${data.chain_name}</div>
      <div class="dp-sub">${data.category || ''}</div>
    </div>
    <div class="dp-section">
      <h3>描述</h3>
      <p style="font-size:13px;color:#bbb;line-height:1.6;">${data.description || ''}</p>
    </div>
    ${data.enterprises && data.enterprises.length ? `
    <div class="dp-section">
      <h3>现有企业 (${data.enterprises.length})</h3>
      <ul class="dp-list">
        ${data.enterprises.map(e => `<li><span class="name">${e.name}</span><span class="meta">[${e.scale}] ${e.revenue_annual || 0}亿元</span></li>`).join('')}
      </ul>
    </div>` : ''}
    ${data.investments && data.investments.length ? `
    <div class="dp-section">
      <h3>招商项目 (${data.investments.length})</h3>
      <ul class="dp-list">
        ${data.investments.map(inv => `<li><span class="name">${inv.enterprise_name}</span><span class="meta">${inv.stage} · ${inv.amount || 0}亿元</span></li>`).join('')}
      </ul>
    </div>` : ''}
    ${data.economic_impacts && data.economic_impacts.length ? `
    <div class="dp-section">
      <h3>经济影响</h3>
      <ul class="dp-list">
        ${data.economic_impacts.map(eco => `<li>${eco.year}年: 产值 ${eco.output_value}亿元 / 就业 ${eco.employment}人 / GDP ${eco.gdp_contribution}亿元</li>`).join('')}
      </ul>
    </div>` : ''}
    ${surrCities && surrCities.length ? `
    <div class="dp-section">
      <h3>周边城市协同</h3>
      <ul class="dp-list">
        ${surrCities.map(sc => `<li><span class="name">${sc.city}</span><span class="meta">${sc.role}</span></li>`).join('')}
      </ul>
    </div>` : ''}`;
}

function renderInvestmentDetail(d) {
  const el = document.getElementById("panel-content");
  el.innerHTML = `
    <div class="dp-header">
      <span class="dp-type investment">招商项目</span>
      <div class="dp-title">${d.name}</div>
      <div class="dp-sub">${d.industry || ''}</div>
    </div>
    <div class="dp-section">
      <h3>项目信息</h3>
      <div class="dp-field"><span class="label">投资额</span><span class="value">${d.amount || 0} 亿元</span></div>
      <div class="dp-field"><span class="label">阶段</span><span class="value">${d.stage || '-'}</span></div>
      <div class="dp-field"><span class="label">信息来源</span><span class="value">${d.source || '-'}</span></div>
      <div class="dp-field"><span class="label">公布时间</span><span class="value">${d.date || '-'}</span></div>
    </div>
    <div class="dp-section">
      <h3>意义</h3>
      <p style="font-size:13px;color:#bbb;line-height:1.6;">${d.description || '该招商项目将完善高明区相关产业链布局，带动就业和经济增长。'}</p>
    </div>`;
}

function renderInfrastructureDetail(d) {
  const el = document.getElementById("panel-content");
  let impactAreas = d.impact_areas;
  if (typeof impactAreas === 'string') try { impactAreas = JSON.parse(impactAreas); } catch(e) {}
  el.innerHTML = `
    <div class="dp-header">
      <span class="dp-type infrastructure">基础设施</span>
      <div class="dp-title">${d.name}</div>
      <div class="dp-sub">${d.infra_type || ''} · ${d.status || ''}</div>
    </div>
    <div class="dp-section">
      <h3>项目信息</h3>
      <div class="dp-field"><span class="label">类型</span><span class="value">${d.infra_type || '-'}</span></div>
      <div class="dp-field"><span class="label">状态</span><span class="value">${d.status || '-'}</span></div>
      <div class="dp-field"><span class="label">预计完成</span><span class="value">${d.completion || '-'}</span></div>
    </div>
    <div class="dp-section">
      <h3>项目描述</h3>
      <p style="font-size:13px;color:#bbb;line-height:1.6;">${d.description || ''}</p>
    </div>
    ${impactAreas && impactAreas.length ? `
    <div class="dp-section">
      <h3>带动产业</h3>
      <ul class="dp-list">
        ${impactAreas.map(ia => `<li>${ia}</li>`).join('')}
      </ul>
    </div>` : ''}`;
}

function renderCityDetail(d) {
  const el = document.getElementById("panel-content");
  el.innerHTML = `
    <div class="dp-header">
      <span class="dp-type city">周边城市</span>
      <div class="dp-title">${d.name}</div>
    </div>
    <div class="dp-section">
      <p style="font-size:13px;color:#bbb;">高明区与 ${d.name} 的产业协同详情请在产业分析中查看。</p>
    </div>`;
}

function closePanel() {
  document.getElementById("detail-panel").classList.add("hidden");
  g.selectAll(".node-group circle").attr("opacity", 0.9);
}

// ── 搜索 ──────────────────────────────────────────────────
const searchInput = document.getElementById("search-input");
const searchResults = document.getElementById("search-results");
let searchTimer = null;

searchInput.addEventListener("input", () => {
  clearTimeout(searchTimer);
  const q = searchInput.value.trim();
  if (q.length < 1) { searchResults.classList.remove("show"); return; }
  searchTimer = setTimeout(() => doSearch(q), 300);
});

document.addEventListener("click", (e) => {
  if (!e.target.closest("#search-box")) searchResults.classList.remove("show");
});

async function doSearch(q) {
  try {
    const resp = await fetch(`${API_BASE}/search?q=${encodeURIComponent(q)}`);
    const data = await resp.json();
    searchResults.innerHTML = "";
    if (data.length === 0) {
      searchResults.innerHTML = '<div class="sr-item" style="color:#667">未找到结果</div>';
    } else {
      data.slice(0, 20).forEach((item) => {
        const div = document.createElement("div");
        div.className = "sr-item";
        div.innerHTML = `<span class="sr-tag ${item.type === 'enterprise' ? 'ent' : item.type === 'chain' ? 'chain' : item.type === 'investment' ? 'inv' : 'infra'}">${TYPE_LABELS[item.type] || item.type}</span> ${item.name}`;
        div.addEventListener("click", () => {
          searchResults.classList.remove("show");
          searchInput.value = item.name;
          focusNode(item.id);
        });
        searchResults.appendChild(div);
      });
    }
    searchResults.classList.add("show");
  } catch (e) { /* ignore */ }
}

function focusNode(id) {
  const node = graphData.nodes.find(n => n.id === id);
  if (!node) return;
  // 模拟点击
  nodeClick(null, node);
  // 飞到节点
  const container = document.getElementById("graph-container");
  const cx = container.clientWidth / 2, cy = container.clientHeight / 2;
  const scale = 1.2;
  const transform = d3.zoomIdentity.translate(cx - node.x * scale, cy - node.y * scale).scale(scale);
  svg.transition().duration(750).call(zoom.transform, transform);
}

// ── 重置视图 ──────────────────────────────────────────────
function resetView() {
  svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity);
  closePanel();
}

// ── 产业分析弹窗 ──────────────────────────────────────────
async function showAnalysis() {
  const modal = document.getElementById("modal");
  const content = document.getElementById("modal-content");
  modal.classList.remove("hidden");
  document.getElementById("modal-overlay").classList.remove("hidden");
  content.innerHTML = '<p style="color:#667">加载中...</p>';

  try {
    const resp = await fetch(`${API_BASE}/analysis`);
    const data = await resp.json();
    renderAnalysis(data, content);
  } catch(e) {
    content.innerHTML = `<p style="color:#E85A5A">加载失败: ${e.message}</p>`;
  }
}

function closeModal() {
  document.getElementById("modal").classList.add("hidden");
  document.getElementById("modal-overlay").classList.add("hidden");
}

function renderAnalysis(data, el) {
  let html = `<h2 style="margin-bottom:8px;">📊 高明区产业综合分析</h2>`;

  // 经济影响
  html += `<div class="analysis-grid">`;
  html += `<div class="analysis-card"><h3>💹 经济影响预测</h3>`;
  (data.economic_impact || []).forEach(eco => {
    html += `<div class="ai">
      <span style="color:#E8A838;font-weight:700;">${eco.year}年</span><br>
      <span class="big">${eco.total_output || 0}</span><span class="unit"> 亿元总产值</span><br>
      <span class="big">${eco.total_emp || 0}</span><span class="unit"> 人就业</span><br>
      <span class="big">${eco.total_gdp || 0}</span><span class="unit"> 亿元GDP贡献</span>
    </div>`;
  });
  html += `</div>`;

  // 城市关系
  html += `<div class="analysis-card"><h3>🏙️ 周边城市关系</h3>`;
  (data.city_relations || []).forEach(cr => {
    const tagClass = cr.relation_type === '竞争' ? 'compete' : cr.relation_type === '合作' ? 'cooperate' : 'complement';
    html += `<div class="city-card">
      <span class="city-name">${cr.city_name}</span>
      <span class="city-tag ${tagClass}">${cr.relation_type}</span>
      <span style="color:#667;font-size:12px;">${cr.industry}</span><br>
      <span style="color:#8899aa;font-size:12px;">${cr.description}</span>
    </div>`;
  });
  html += `</div>`;

  // 产业链缺口
  html += `<div class="analysis-card" style="grid-column:1/-1;"><h3>🔗 产业链缺口与引入建议</h3>`;
  (data.suggestions || []).forEach(s => {
    html += `<div class="gap-item">
      <span class="chain-name">${s.chain}</span><br>
      <span class="gap-desc">⚠️ ${s.gap}</span><br>
      <span class="sol">✅ 建议: ${s.suggestion}</span>
    </div>`;
  });
  html += `</div>`;

  // 各产业链详情
  (data.chain_gaps || []).forEach(cg => {
    html += `<div class="analysis-card"><h3>${cg.chain_name}</h3>
      <div style="font-size:13px;color:#8899aa;">
        现有企业: <b style="color:#4A90D9">${cg.existing_enterprises}</b> 家 &nbsp;|&nbsp;
        招商项目: <b style="color:#E85A5A">${cg.new_investments}</b> 个
      </div>
    </div>`;
  });

  html += `</div>`;
  el.innerHTML = html;
}

// ── 导出图片 ──────────────────────────────────────────────
function exportImage() {
  const svgNode = document.getElementById("graph-svg");
  const serializer = new XMLSerializer();
  const svgString = serializer.serializeToString(svgNode);
  const canvas = document.createElement("canvas");
  const rect = svgNode.getBoundingClientRect();
  canvas.width = rect.width * 2;
  canvas.height = rect.height * 2;
  const ctx = canvas.getContext("2d");
  ctx.scale(2, 2);
  ctx.fillStyle = "#0f1923";
  ctx.fillRect(0, 0, rect.width, rect.height);

  const img = new Image();
  const blob = new Blob([svgString], { type: "image/svg+xml;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  img.onload = () => {
    ctx.drawImage(img, 0, 0, rect.width, rect.height);
    URL.revokeObjectURL(url);
    const a = document.createElement("a");
    a.download = `gaoming-graph-${Date.now()}.png`;
    a.href = canvas.toDataURL("image/png");
    a.click();
  };
  img.src = url;
}

// ── 窗口变化 ──────────────────────────────────────────────
window.addEventListener("resize", () => {
  if (!graphData) return;
  const container = document.getElementById("graph-container");
  const w = container.clientWidth, h = container.clientHeight;
  svg.attr("width", w).attr("height", h);
  if (simulation) simulation.force("center", d3.forceCenter(w / 2, h / 2)).alpha(0.3).restart();
});

// ── 启动 ──────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", init);
