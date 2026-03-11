"""
html_generator.py — v5 수준 HTML 대시보드 자동 생성
Chart.js 차트 + 인사이트 + 제작 브리프를 포함한 독립 실행형 HTML
"""
from typing import Dict, List
import json
from datetime import datetime


def generate_html_dashboard(
    meta: Dict,
    creatives: List[Dict],
    kpi: Dict,
    insights: List[str],
    briefs: List[Dict],
    roas_ranking: List[Dict],
    low_performers: List[Dict],
    product_analysis: List[Dict],
    format_analysis: List[Dict],
    ctr_cvr_pattern: Dict,
) -> str:
    """v5 수준 HTML 대시보드 생성"""
    
    client = meta.get("client", "")
    campaign = meta.get("campaign", "")
    period = meta.get("period", "")
    
    # Chart.js 데이터 준비
    roas_labels = [f'{c["product"]} {c["name"]}' for c in roas_ranking[:15]]
    roas_values = [round(c["roas"] * 100, 1) for c in roas_ranking[:15]]
    roas_colors = [_tier_color(c["tier"]) for c in roas_ranking[:15]]
    
    # 제품별 분석 데이터
    prod_labels = [p["attribute"] for p in product_analysis]
    prod_roas = [round(p["avg_roas"] * 100, 1) for p in product_analysis]
    prod_ctr = [round(p["avg_ctr"] * 10000, 2) for p in product_analysis]
    
    # 형식별 분석 데이터
    fmt_labels = [f["attribute"] for f in format_analysis]
    fmt_roas = [round(f["avg_roas"] * 100, 1) for f in format_analysis]
    
    # CTR vs CVR scatter data
    scatter_data = json.dumps(ctr_cvr_pattern.get("data", []))
    
    # 인사이트 HTML
    insights_html = "\n".join(f'<div class="insight-box">{ins}</div>' for ins in insights)
    
    # 소재 랭킹 HTML
    ranking_html = ""
    for i, c in enumerate(roas_ranking[:10], 1):
        ranking_html += f"""
        <div class="rank-row">
            <span class="rank-num">{i}</span>
            <span class="tier-badge tier-{c['tier']}">{c['tier']}</span>
            <span class="rank-name">{c['product']} {c['name']}</span>
            <span class="rank-value">{c['roas']:.1%}</span>
        </div>"""
    
    # 효율 저조 진단 HTML
    diag_html = ""
    for c in low_performers:
        diags = "<br>".join(f"→ {d}" for d in c.get("diagnosis", []))
        diag_html += f"""
        <div class="diag-box">
            <b>{c['product']} {c['name']}</b> — ROAS {c['roas']:.1%} (평균 대비 {c['vs_avg_roas']:+.1f}%)
            <br>Imps {c['impressions']:,.0f} / Clicks {c['clicks']:,.0f} / Actions {c['actions']:,.0f}
            <br>{diags}
        </div>"""
    
    # 브리프 HTML
    brief_html = ""
    for brief in briefs:
        refs = "<br>".join(f"• {r}" for r in brief["reference_creatives"])
        dos = "\n".join(f"<li>{d}</li>" for d in brief["do"])
        donts = "\n".join(f"<li>{d}</li>" for d in brief["dont"])
        avg = brief["avg_metrics"]
        
        brief_html += f"""
        <div class="brief-card">
            <div class="brief-title">{brief['title']} — {brief['subtitle']}</div>
            <p><b>우선순위:</b> {brief['priority']} | <b>KPI 목표:</b> {brief['kpi_target']}</p>
            <p><b>추천 형식:</b> {brief['recommended_format']}</p>
            <p><b>참조 소재:</b><br>{refs}</p>
            <div class="do-dont-grid">
                <div class="do-box"><h4>✅ DO</h4><ul>{dos}</ul></div>
                <div class="dont-box"><h4>❌ DON'T</h4><ul>{donts}</ul></div>
            </div>
            <p class="brief-avg">참조 소재 평균 — CTR: {avg['ctr']:.3%} | CVR: {avg['cvr']:.2%} | ROAS: {avg['roas']:.1%}</p>
        </div>"""
    
    # 전체 소재 테이블
    table_rows = ""
    for c in creatives:
        table_rows += f"""
        <tr>
            <td><span class="tier-badge tier-{c.get('tier', 'D')}">{c.get('tier', '-')}</span></td>
            <td>{c.get('media', '')}</td>
            <td>{c.get('product', '')}</td>
            <td>{c.get('name', '')}</td>
            <td>{c.get('format', '')}</td>
            <td class="num">{c.get('impressions', 0):,.0f}</td>
            <td class="num">{c.get('clicks', 0):,.0f}</td>
            <td class="num">{c.get('actions', 0):,.0f}</td>
            <td class="num">{c.get('ctr', 0):.3%}</td>
            <td class="num">{c.get('cvr', 0):.2%}</td>
            <td class="num highlight">{c.get('roas', 0):.1%}</td>
            <td class="num">₩{c.get('cpc', 0):,.0f}</td>
            <td class="num">₩{c.get('spent', 0):,.0f}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{client} {campaign} — Creative Intelligence</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root {{
    --bg-primary: #0a192f;
    --bg-secondary: #112240;
    --bg-card: #1a1a2e;
    --text-primary: #ccd6f6;
    --text-secondary: #8892b0;
    --accent: #64ffda;
    --gold: #ffd700;
    --red: #ff6b6b;
    --purple: #a78bfa;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    background: var(--bg-primary);
    color: var(--text-primary);
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
    line-height: 1.6;
}}
.container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
header {{
    background: linear-gradient(135deg, var(--bg-secondary), var(--bg-primary));
    padding: 30px 40px;
    border-bottom: 2px solid var(--accent);
}}
header h1 {{ font-size: 1.8rem; color: var(--accent); }}
header p {{ color: var(--text-secondary); margin-top: 4px; }}

/* 탭 */
.tabs {{ display: flex; gap: 4px; margin: 20px 0; flex-wrap: wrap; }}
.tab-btn {{
    padding: 10px 20px; border: 1px solid #233554; border-radius: 8px 8px 0 0;
    background: var(--bg-secondary); color: var(--text-secondary); cursor: pointer;
    font-size: 0.9rem; transition: all 0.2s;
}}
.tab-btn.active {{ background: var(--bg-card); color: var(--accent); border-bottom: 2px solid var(--accent); }}
.tab-content {{ display: none; padding: 20px; background: var(--bg-card); border-radius: 0 0 12px 12px; }}
.tab-content.active {{ display: block; }}

/* KPI 카드 */
.kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin: 20px 0; }}
.kpi-card {{
    background: linear-gradient(135deg, var(--bg-card), var(--bg-secondary));
    border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #233554;
}}
.kpi-card .label {{ color: var(--text-secondary); font-size: 0.85rem; }}
.kpi-card .value {{ color: var(--text-primary); font-size: 1.6rem; font-weight: 700; margin: 4px 0; }}
.kpi-card .sub {{ color: var(--accent); font-size: 0.8rem; }}

/* 인사이트 */
.insight-box {{
    background: rgba(100, 255, 218, 0.05);
    border-left: 4px solid var(--accent);
    padding: 12px 16px; margin: 8px 0;
    border-radius: 0 8px 8px 0; font-size: 0.9rem;
}}

/* 진단 */
.diag-box {{
    background: rgba(255, 107, 107, 0.05);
    border-left: 4px solid var(--red);
    padding: 12px 16px; margin: 8px 0;
    border-radius: 0 8px 8px 0;
}}

/* 랭킹 */
.rank-row {{
    display: flex; align-items: center; gap: 10px;
    padding: 8px 12px; border-bottom: 1px solid #233554;
}}
.rank-num {{ font-size: 1.2rem; font-weight: 700; width: 30px; color: var(--text-secondary); }}
.rank-name {{ flex: 1; }}
.rank-value {{ color: var(--accent); font-weight: 700; font-size: 1.1rem; }}

/* 티어 */
.tier-badge {{ display: inline-block; padding: 2px 10px; border-radius: 12px; font-weight: 700; font-size: 0.8rem; }}
.tier-S {{ background: #FFD700; color: #000; }}
.tier-A {{ background: #C0C0C0; color: #000; }}
.tier-B {{ background: #CD7F32; color: #fff; }}
.tier-C {{ background: #4a90d9; color: #fff; }}
.tier-D {{ background: #444; color: #999; }}

/* 브리프 */
.brief-card {{
    background: linear-gradient(135deg, var(--bg-secondary), var(--bg-card));
    border: 1px solid #233554; border-radius: 12px; padding: 20px; margin: 16px 0;
}}
.brief-title {{ color: var(--accent); font-size: 1.1rem; font-weight: 700; margin-bottom: 10px; }}
.do-dont-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 12px 0; }}
.do-box {{ background: rgba(100, 255, 218, 0.05); padding: 12px; border-radius: 8px; }}
.dont-box {{ background: rgba(255, 107, 107, 0.05); padding: 12px; border-radius: 8px; }}
.do-box h4 {{ color: var(--accent); }} .dont-box h4 {{ color: var(--red); }}
.do-box ul, .dont-box ul {{ margin-left: 16px; font-size: 0.9rem; }}
.brief-avg {{ color: var(--text-secondary); font-size: 0.8rem; margin-top: 8px; }}

/* 테이블 */
table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
th {{ background: var(--bg-secondary); padding: 10px 8px; text-align: left; color: var(--accent); border-bottom: 2px solid #233554; position: sticky; top: 0; }}
td {{ padding: 8px; border-bottom: 1px solid #1a2a44; }}
tr:hover {{ background: rgba(100, 255, 218, 0.03); }}
.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
.highlight {{ color: var(--accent); font-weight: 600; }}

.chart-container {{ background: var(--bg-secondary); border-radius: 12px; padding: 20px; margin: 16px 0; }}
h2 {{ color: var(--accent); margin-bottom: 12px; }}
h3 {{ color: var(--text-primary); margin: 16px 0 8px; }}

footer {{ text-align: center; padding: 30px; color: var(--text-secondary); font-size: 0.8rem; }}
</style>
</head>
<body>

<header>
    <h1>🎨 {client} — {campaign} 소재 인사이트</h1>
    <p>기간: {period} | 예산: ₩{kpi.get('budget', 0):,.0f} | 소재 {len(creatives)}종 분석 | 생성: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
</header>

<div class="container">

<div class="tabs">
    <div class="tab-btn active" onclick="showTab('overview')">📊 성과 총괄</div>
    <div class="tab-btn" onclick="showTab('ranking')">🏆 소재 랭킹</div>
    <div class="tab-btn" onclick="showTab('analysis')">🔍 속성 분석</div>
    <div class="tab-btn" onclick="showTab('diagnosis')">⚠️ 효율 진단</div>
    <div class="tab-btn" onclick="showTab('brief')">📝 제작 브리프</div>
    <div class="tab-btn" onclick="showTab('data')">📋 전체 데이터</div>
</div>

<!-- 성과 총괄 -->
<div id="overview" class="tab-content active">
    <h2>📊 성과 총괄</h2>
    <div class="kpi-grid">
        <div class="kpi-card"><div class="label">총 노출</div><div class="value">{kpi['total_impressions']:,.0f}</div></div>
        <div class="kpi-card"><div class="label">총 클릭</div><div class="value">{kpi['total_clicks']:,.0f}</div></div>
        <div class="kpi-card"><div class="label">총 전환</div><div class="value">{kpi['total_actions']:,.0f}</div></div>
        <div class="kpi-card"><div class="label">Overall ROAS</div><div class="value highlight">{kpi['overall_roas']:.1f}%</div></div>
        <div class="kpi-card"><div class="label">Overall CTR</div><div class="value">{kpi['overall_ctr']:.2f}%</div></div>
        <div class="kpi-card"><div class="label">Overall CVR</div><div class="value">{kpi['overall_cvr']:.2f}%</div></div>
        <div class="kpi-card"><div class="label">평균 CPA</div><div class="value">₩{kpi['overall_cpa']:,.0f}</div></div>
    </div>
    
    <h3>💡 핵심 인사이트</h3>
    {insights_html}
    
    <div class="chart-container">
        <h3>ROAS 분포</h3>
        <canvas id="roasChart" height="400"></canvas>
    </div>
</div>

<!-- 소재 랭킹 -->
<div id="ranking" class="tab-content">
    <h2>🏆 ROAS TOP 10</h2>
    {ranking_html}
</div>

<!-- 속성 분석 -->
<div id="analysis" class="tab-content">
    <h2>🔍 속성 분석</h2>
    <div class="chart-container">
        <h3>제품별 평균 ROAS</h3>
        <canvas id="productChart" height="300"></canvas>
    </div>
    <div class="chart-container">
        <h3>형식별 평균 ROAS</h3>
        <canvas id="formatChart" height="300"></canvas>
    </div>
    <h3>🔄 CTR vs CVR 패턴</h3>
    <p><b>패턴:</b> {ctr_cvr_pattern.get('pattern', '')}</p>
    <p>{ctr_cvr_pattern.get('details', '')}</p>
</div>

<!-- 효율 진단 -->
<div id="diagnosis" class="tab-content">
    <h2>⚠️ 효율 저조 소재 진단</h2>
    {diag_html if diag_html else '<p>효율 저조 소재가 없습니다.</p>'}
</div>

<!-- 제작 브리프 -->
<div id="brief" class="tab-content">
    <h2>📝 제작 브리프</h2>
    {brief_html if brief_html else '<p>브리프 생성에 필요한 데이터가 부족합니다.</p>'}
</div>

<!-- 전체 데이터 -->
<div id="data" class="tab-content">
    <h2>📋 전체 소재 데이터</h2>
    <div style="overflow-x:auto;">
    <table>
        <thead><tr>
            <th>Tier</th><th>매체</th><th>제품</th><th>소재</th><th>형식</th>
            <th>노출</th><th>클릭</th><th>전환</th><th>CTR</th><th>CVR</th>
            <th>ROAS</th><th>CPC</th><th>소진비</th>
        </tr></thead>
        <tbody>{table_rows}</tbody>
    </table>
    </div>
</div>

</div>

<footer>
    Creative Intelligence v5 — {client} {campaign} | Generated {datetime.now().strftime('%Y-%m-%d')} | SM본부 · 골드넥스
</footer>

<script>
// 탭 전환
function showTab(id) {{
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    event.target.classList.add('active');
}}

// ROAS 차트
new Chart(document.getElementById('roasChart'), {{
    type: 'bar',
    data: {{
        labels: {json.dumps(roas_labels)},
        datasets: [{{
            label: 'ROAS (%)',
            data: {json.dumps(roas_values)},
            backgroundColor: {json.dumps(roas_colors)},
            borderWidth: 0,
            borderRadius: 4,
        }}]
    }},
    options: {{
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
            legend: {{ display: false }},
            annotation: {{ annotations: {{ line1: {{ type: 'line', xMin: 100, xMax: 100, borderColor: '#64ffda', borderDash: [5,5] }} }} }}
        }},
        scales: {{
            x: {{ grid: {{ color: '#1a2a44' }}, ticks: {{ color: '#8892b0' }} }},
            y: {{ grid: {{ display: false }}, ticks: {{ color: '#ccd6f6', font: {{ size: 11 }} }} }}
        }}
    }}
}});

// 제품별 차트
new Chart(document.getElementById('productChart'), {{
    type: 'bar',
    data: {{
        labels: {json.dumps(prod_labels)},
        datasets: [{{
            label: 'ROAS (%)',
            data: {json.dumps(prod_roas)},
            backgroundColor: '#64ffda',
            borderRadius: 4,
        }}]
    }},
    options: {{
        responsive: true,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
            y: {{ grid: {{ color: '#1a2a44' }}, ticks: {{ color: '#8892b0' }} }},
            x: {{ grid: {{ display: false }}, ticks: {{ color: '#ccd6f6' }} }}
        }}
    }}
}});

// 형식별 차트
new Chart(document.getElementById('formatChart'), {{
    type: 'bar',
    data: {{
        labels: {json.dumps(fmt_labels)},
        datasets: [{{
            label: 'ROAS (%)',
            data: {json.dumps(fmt_roas)},
            backgroundColor: ['#64ffda', '#ffd700', '#ff6b6b', '#a78bfa', '#38bdf8'],
            borderRadius: 4,
        }}]
    }},
    options: {{
        responsive: true,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
            y: {{ grid: {{ color: '#1a2a44' }}, ticks: {{ color: '#8892b0' }} }},
            x: {{ grid: {{ display: false }}, ticks: {{ color: '#ccd6f6' }} }}
        }}
    }}
}});
</script>
</body>
</html>"""
    
    return html


def _tier_color(tier: str) -> str:
    return {
        "S": "#FFD700",
        "A": "#C0C0C0",
        "B": "#CD7F32",
        "C": "#4a90d9",
        "D": "#666666",
    }.get(tier, "#666666")
