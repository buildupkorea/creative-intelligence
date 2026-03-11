"""
Creative Intelligence — Streamlit Dashboard
엑셀 업로드 → 자동 파싱 → 소재 태깅(8개 기준축) → v5 수준 인사이트 대시보드 + HTML 다운로드
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime

from utils.parser import parse_report
from utils.analyzer import (
    classify_creatives, generate_kpi_summary, rank_by_roas, rank_by_ctr,
    diagnose_low_performers, analyze_by_product, analyze_by_format,
    analyze_by_media, detect_ctr_cvr_pattern, generate_insights,
    generate_briefs, analyze_by_attribute,
)
from utils.image_extractor import extract_images
from utils.html_generator import generate_html_dashboard
from utils.creative_attributes import ATTRIBUTE_SCHEMA, get_default_tags

# ── 페이지 설정 ────────────────────────────────────────
st.set_page_config(
    page_title="Creative Intelligence",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 커스텀 CSS ─────────────────────────────────────────
st.markdown("""
<style>
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #2a2a4a;
    }
    .insight-box {
        background: #0a192f;
        border-left: 4px solid #64ffda;
        padding: 12px 16px;
        margin: 8px 0;
        border-radius: 0 8px 8px 0;
        color: #ccd6f6;
        font-size: 0.9rem;
    }
    .diag-box {
        background: #1a0a0a;
        border-left: 4px solid #ff6b6b;
        padding: 12px 16px;
        margin: 8px 0;
        border-radius: 0 8px 8px 0;
        color: #ccd6f6;
    }
    .tier-S { background: #FFD700; color: #000; }
    .tier-A { background: #C0C0C0; color: #000; }
    .tier-B { background: #CD7F32; color: #fff; }
    .tier-C { background: #4a4a6a; color: #ccc; }
    .tier-D { background: #2a2a3a; color: #888; }
    .tier-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


# ── 사이드바 ────────────────────────────────────────────
with st.sidebar:
    st.title("🎨 Creative Intelligence")
    st.caption("소재 성과 분석 대시보드 v5")
    st.divider()

    uploaded_file = st.file_uploader(
        "📂 엑셀 리포트 업로드",
        type=["xlsx", "xls"],
        help="SENKA, UNO 등 캠페인 리포트 엑셀 파일을 업로드하세요."
    )

    if uploaded_file:
        st.success(f"✅ {uploaded_file.name}")

    st.divider()
    st.markdown("**Made by** SM본부 · 골드넥스")


# ── 랜딩 ────────────────────────────────────────────────
if not uploaded_file:
    st.markdown("# 🎨 Creative Intelligence")
    st.markdown("### 엑셀 업로드 → 소재 태깅 → AI 인사이트 자동 생성")
    st.markdown("")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("#### 📊 성과 총괄")
        st.markdown("KPI, ROAS 랭킹,\n효율 저조 진단")
    with col2:
        st.markdown("#### 🏷️ 소재 태깅")
        st.markdown("8개 기준축\n드롭다운 분류")
    with col3:
        st.markdown("#### 🔍 속성 분석")
        st.markdown("무드·Hook·레이아웃별\n효율 비교")
    with col4:
        st.markdown("#### 📝 제작 브리프")
        st.markdown("3종 자동 생성\nDO/DON'T")

    st.markdown("---")
    st.info("👈 사이드바에서 엑셀 파일을 업로드하세요.")
    st.stop()


# ── 데이터 파싱 ──────────────────────────────────────────
@st.cache_data
def load_data(file_bytes, file_name):
    import io
    buf = io.BytesIO(file_bytes)
    data = parse_report(buf)
    data["creatives"] = classify_creatives(data["creatives"])
    return data


file_bytes = uploaded_file.read()
uploaded_file.seek(0)

with st.spinner("📊 엑셀 파싱 중..."):
    data = load_data(file_bytes, uploaded_file.name)

meta = data["meta"]
creatives = data["creatives"]
daily_df = data["daily"]

# 이미지 추출
images = extract_images(uploaded_file)

# ── 세션 상태: 소재 태깅 데이터 ─────────────────────────
if "tags" not in st.session_state:
    st.session_state.tags = {}

for c in creatives:
    key = f"{c['product']}_{c['name']}"
    if key not in st.session_state.tags:
        st.session_state.tags[key] = get_default_tags()

# 태깅 데이터를 creatives에 머지
for c in creatives:
    key = f"{c['product']}_{c['name']}"
    tags = st.session_state.tags.get(key, {})
    for attr_key in ATTRIBUTE_SCHEMA:
        c[attr_key] = tags.get(attr_key, "")

# 분석 결과 생성
kpi = generate_kpi_summary(meta, creatives)
roas_ranking = rank_by_roas(creatives)
ctr_ranking = rank_by_ctr(creatives)
low_performers = diagnose_low_performers(creatives)
product_analysis = analyze_by_product([c for c in creatives if c.get("roas", 0) > 0])
format_analysis = analyze_by_format([c for c in creatives if c.get("roas", 0) > 0])
media_analysis = analyze_by_media(creatives)
ctr_cvr_pattern = detect_ctr_cvr_pattern(creatives)
insights = generate_insights(creatives, meta)
briefs = generate_briefs(creatives)

# 태깅 완료율
total_tags = len(creatives) * len(ATTRIBUTE_SCHEMA)
filled_tags = sum(1 for c in creatives for attr_key in ATTRIBUTE_SCHEMA if c.get(attr_key, ""))
tag_rate = (filled_tags / total_tags * 100) if total_tags > 0 else 0

# ── 헤더 ────────────────────────────────────────────────
st.markdown(f"# 🎨 {meta.get('client', '캠페인')} — {meta.get('campaign', '')} 소재 인사이트")
st.caption(f"기간: {meta.get('period', '')} | 예산: ₩{meta.get('budget', 0):,.0f} | 소재 {len(creatives)}종 | 태깅 {tag_rate:.0f}%")

# ── 탭 구성 ──────────────────────────────────────────────
tabs = st.tabs([
    "📊 성과 총괄",
    "🏆 소재 랭킹",
    "🏷️ 소재 태깅",
    "🔍 속성 분석",
    "📈 일별 트렌드",
    "⚠️ 효율 진단",
    "📝 제작 브리프",
    "⬇️ HTML 다운로드",
])


# ═══════════════════════════════════════════════════════
# 탭 1: 성과 총괄
# ═══════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("## 📊 성과 총괄")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("총 노출", f"{kpi['total_impressions']:,.0f}")
    with c2:
        st.metric("총 클릭", f"{kpi['total_clicks']:,.0f}")
    with c3:
        st.metric("총 전환", f"{kpi['total_actions']:,.0f}")
    with c4:
        st.metric("Overall ROAS", f"{kpi['overall_roas']:.1f}%")
    with c5:
        st.metric("Overall CTR", f"{kpi['overall_ctr']:.2f}%")

    st.divider()
    st.markdown("### 💡 핵심 인사이트")
    for insight in insights:
        st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)

    st.divider()
    conv_creatives = [c for c in creatives if c.get("roas", 0) > 0]
    if conv_creatives:
        st.markdown("### ROAS 분포")
        df_roas = pd.DataFrame(conv_creatives)
        df_roas["label"] = df_roas["product"] + " " + df_roas["name"]
        df_roas["roas_pct"] = df_roas["roas"] * 100
        fig = px.bar(
            df_roas.sort_values("roas_pct", ascending=True),
            x="roas_pct", y="label", orientation="h", color="tier",
            color_discrete_map={"S": "#FFD700", "A": "#C0C0C0", "B": "#CD7F32", "C": "#4a90d9", "D": "#666"},
            labels={"roas_pct": "ROAS (%)", "label": "소재", "tier": "티어"},
        )
        fig.add_vline(x=100, line_dash="dash", line_color="#64ffda", annotation_text="ROAS 100%")
        fig.update_layout(template="plotly_dark", plot_bgcolor="#0a192f", paper_bgcolor="#0a192f",
                          height=max(400, len(conv_creatives) * 35), yaxis=dict(tickfont=dict(size=11)))
        st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════
# 탭 2: 소재 랭킹
# ═══════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("## 🏆 소재 랭킹")
    rank_col1, rank_col2 = st.columns(2)
    with rank_col1:
        st.markdown("### ROAS TOP")
        for i, c in enumerate(roas_ranking[:10], 1):
            tier_class = f"tier-{c['tier']}"
            catalog_warn = " 📦" if c.get("format") == "카탈로그" else ""
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:10px;margin:6px 0;">'
                f'<span style="font-size:1.2rem;font-weight:700;width:30px;">{i}</span>'
                f'<span class="tier-badge {tier_class}">{c["tier"]}</span>'
                f'<span><b>{c["product"]}</b> {c["name"]}{catalog_warn}</span>'
                f'<span style="margin-left:auto;color:#64ffda;font-weight:700;">{c["roas"]:.1%}</span>'
                f'</div>', unsafe_allow_html=True)
    with rank_col2:
        st.markdown("### CTR TOP")
        for i, c in enumerate(ctr_ranking[:10], 1):
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:10px;margin:6px 0;">'
                f'<span style="font-size:1.2rem;font-weight:700;width:30px;">{i}</span>'
                f'<span><b>{c["product"]}</b> {c["name"]}</span>'
                f'<span style="margin-left:auto;color:#ffd700;font-weight:700;">{c["ctr"]:.3%}</span>'
                f'</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("### 📋 전체 소재 데이터")
    if creatives:
        df_all = pd.DataFrame(creatives)
        display_cols = ["tier", "media", "product", "name", "format", "impressions",
                        "clicks", "actions", "revenue", "ctr", "cvr", "roas", "cpc", "cpa", "spent"]
        available_cols = [col for col in display_cols if col in df_all.columns]
        df_display = df_all[available_cols].copy()
        if "ctr" in df_display.columns:
            df_display["ctr"] = df_display["ctr"].apply(lambda x: f"{x:.3%}" if x else "-")
        if "cvr" in df_display.columns:
            df_display["cvr"] = df_display["cvr"].apply(lambda x: f"{x:.2%}" if x else "-")
        if "roas" in df_display.columns:
            df_display["roas"] = df_display["roas"].apply(lambda x: f"{x:.1%}" if x else "-")
        for col in ["impressions", "clicks", "actions", "revenue", "spent"]:
            if col in df_display.columns:
                df_display[col] = df_display[col].apply(lambda x: f"{x:,.0f}" if x else "-")
        for col in ["cpc", "cpa"]:
            if col in df_display.columns:
                df_display[col] = df_display[col].apply(lambda x: f"₩{x:,.0f}" if x else "-")
        st.dataframe(df_display, use_container_width=True, height=500)


# ═══════════════════════════════════════════════════════
# 탭 3: 소재 태깅 (8개 기준축)
# ═══════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("## 🏷️ 소재 속성 태깅")
    st.markdown(f"태깅 진행률: **{tag_rate:.0f}%** ({filled_tags}/{total_tags})")

    if tag_rate < 100:
        st.warning("⚡ 모든 소재의 속성을 태깅하면 '속성 분석' 탭에서 무드·Hook·레이아웃별 효율 비교가 가능합니다.")
    else:
        st.success("✅ 모든 소재 태깅 완료! '속성 분석' 탭에서 결과를 확인하세요.")

    st.divider()

    with st.expander("📖 8개 기준축 설명", expanded=False):
        for attr_key, schema in ATTRIBUTE_SCHEMA.items():
            label = schema["label"]
            options = schema["options"]
            descs = schema.get("descriptions", {})
            st.markdown(f"**{label}**")
            if descs:
                for opt in options:
                    st.markdown(f"- `{opt}`: {descs.get(opt, '')}")
            else:
                st.markdown(f"- {' / '.join(options)}")
            st.markdown("")

    st.divider()

    media_filter = st.selectbox(
        "매체 필터",
        ["전체"] + list(set(c.get("media", "") for c in creatives if c.get("media"))),
        key="tag_media_filter"
    )
    filtered = creatives if media_filter == "전체" else [c for c in creatives if c.get("media") == media_filter]

    for idx, c in enumerate(filtered):
        ckey = f"{c['product']}_{c['name']}"
        current_tags = st.session_state.tags.get(ckey, get_default_tags())
        filled_count = sum(1 for v in current_tags.values() if v)
        total_count = len(ATTRIBUTE_SCHEMA)
        status = "✅" if filled_count == total_count else f"⬜ {filled_count}/{total_count}"

        with st.expander(
            f"{status}  **{c['product']}** {c['name']}  |  ROAS {c.get('roas', 0):.1%}  |  {c.get('format', '')}",
            expanded=False
        ):
            mc1, mc2, mc3, mc4, mc5 = st.columns(5)
            mc1.metric("노출", f"{c.get('impressions', 0):,.0f}")
            mc2.metric("클릭", f"{c.get('clicks', 0):,.0f}")
            mc3.metric("전환", f"{c.get('actions', 0):,.0f}")
            mc4.metric("ROAS", f"{c.get('roas', 0):.1%}")
            mc5.metric("Tier", c.get("tier", "-"))

            st.markdown("---")

            tag_cols = st.columns(4)
            attr_keys = list(ATTRIBUTE_SCHEMA.keys())
            for ai, attr_key in enumerate(attr_keys):
                schema = ATTRIBUTE_SCHEMA[attr_key]
                col = tag_cols[ai % 4]
                options = [""] + schema["options"]
                current_val = current_tags.get(attr_key, "")
                try:
                    current_idx = options.index(current_val)
                except ValueError:
                    current_idx = 0

                new_val = col.selectbox(
                    schema["label"],
                    options,
                    index=current_idx,
                    key=f"tag_{ckey}_{attr_key}",
                    format_func=lambda x: "(선택)" if x == "" else x,
                )
                if new_val != current_tags.get(attr_key, ""):
                    st.session_state.tags[ckey][attr_key] = new_val

    st.divider()
    st.markdown("### 💾 태깅 데이터")
    if st.button("📋 태깅 JSON 출력"):
        st.json(st.session_state.tags)


# ═══════════════════════════════════════════════════════
# 탭 4: 속성 분석 (태깅 기반)
# ═══════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("## 🔍 속성 분석")

    tagged_creatives = [c for c in creatives if any(c.get(k, "") for k in ATTRIBUTE_SCHEMA)]
    conv_tagged = [c for c in tagged_creatives if c.get("roas", 0) > 0]

    if not conv_tagged:
        st.warning("🏷️ 먼저 '소재 태깅' 탭에서 속성을 태깅해주세요. 태깅 완료 후 속성별 효율 분석이 여기에 표시됩니다.")
        st.info("태깅 없이도 아래 기본 분석(제품별, 형식별, 매체별)은 확인 가능합니다.")

    attr_tabs = st.tabs(
        [schema["label"] for schema in ATTRIBUTE_SCHEMA.values()] + ["제품별", "형식별", "매체별"]
    )

    for ai, (attr_key, schema) in enumerate(ATTRIBUTE_SCHEMA.items()):
        with attr_tabs[ai]:
            tagged_for_attr = [c for c in conv_tagged if c.get(attr_key, "")]
            if not tagged_for_attr:
                st.info(f"'{schema['label']}' 속성이 태깅된 전환 소재가 없습니다.")
                continue

            analysis = analyze_by_attribute(tagged_for_attr, attr_key)
            if analysis:
                df_attr = pd.DataFrame(analysis)
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df_attr["attribute"],
                    y=df_attr["avg_roas"].apply(lambda x: x * 100),
                    marker_color=["#64ffda", "#ffd700", "#ff6b6b", "#a78bfa", "#38bdf8", "#f472b6"][:len(df_attr)],
                    text=df_attr.apply(lambda r: f'{r["avg_roas"]:.1%}<br>n={r["count"]}', axis=1),
                    textposition="outside",
                ))
                fig.update_layout(title=f"{schema['label']}별 평균 ROAS", template="plotly_dark",
                                  plot_bgcolor="#0a192f", paper_bgcolor="#0a192f", height=400, yaxis_title="ROAS (%)")
                st.plotly_chart(fig, use_container_width=True)

                fig2 = go.Figure()
                fig2.add_trace(go.Bar(
                    x=df_attr["attribute"],
                    y=df_attr["avg_cvr"].apply(lambda x: x * 100),
                    marker_color=["#a78bfa", "#38bdf8", "#64ffda", "#ffd700", "#ff6b6b", "#f472b6"][:len(df_attr)],
                    text=df_attr.apply(lambda r: f'{r["avg_cvr"]:.2%}<br>n={r["count"]}', axis=1),
                    textposition="outside",
                ))
                fig2.update_layout(title=f"{schema['label']}별 평균 CVR", template="plotly_dark",
                                   plot_bgcolor="#0a192f", paper_bgcolor="#0a192f", height=400, yaxis_title="CVR (%)")
                st.plotly_chart(fig2, use_container_width=True)
                st.dataframe(df_attr, use_container_width=True)

    # 제품별
    with attr_tabs[len(ATTRIBUTE_SCHEMA)]:
        if product_analysis:
            df_prod = pd.DataFrame(product_analysis)
            fig = make_subplots(rows=1, cols=2, subplot_titles=("평균 ROAS", "평균 CTR"))
            fig.add_trace(go.Bar(x=df_prod["attribute"], y=df_prod["avg_roas"].apply(lambda x: x * 100),
                                 marker_color="#64ffda", text=df_prod.apply(lambda r: f'{r["avg_roas"]:.1%} (n={r["count"]})', axis=1),
                                 textposition="outside", name="ROAS"), row=1, col=1)
            fig.add_trace(go.Bar(x=df_prod["attribute"], y=df_prod["avg_ctr"].apply(lambda x: x * 100),
                                 marker_color="#ffd700", text=df_prod.apply(lambda r: f'{r["avg_ctr"]:.3%}', axis=1),
                                 textposition="outside", name="CTR"), row=1, col=2)
            fig.update_layout(template="plotly_dark", plot_bgcolor="#0a192f", paper_bgcolor="#0a192f", height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df_prod, use_container_width=True)

    # 형식별
    with attr_tabs[len(ATTRIBUTE_SCHEMA) + 1]:
        if format_analysis:
            df_fmt = pd.DataFrame(format_analysis)
            fig = go.Figure()
            fig.add_trace(go.Bar(x=df_fmt["attribute"], y=df_fmt["avg_roas"].apply(lambda x: x * 100),
                                 marker_color=["#64ffda", "#ffd700", "#ff6b6b", "#a78bfa"][:len(df_fmt)],
                                 text=df_fmt.apply(lambda r: f'{r["avg_roas"]:.1%}<br>n={r["count"]}', axis=1),
                                 textposition="outside"))
            fig.update_layout(title="형식별 평균 ROAS", template="plotly_dark", plot_bgcolor="#0a192f",
                              paper_bgcolor="#0a192f", height=400, yaxis_title="ROAS (%)")
            st.plotly_chart(fig, use_container_width=True)

    # 매체별
    with attr_tabs[len(ATTRIBUTE_SCHEMA) + 2]:
        if media_analysis:
            st.dataframe(pd.DataFrame(media_analysis), use_container_width=True)

    st.divider()
    st.markdown("### 🔄 CTR vs CVR 패턴 분석")
    st.markdown(f"**패턴:** {ctr_cvr_pattern['pattern']}")
    st.markdown(ctr_cvr_pattern["details"])
    if ctr_cvr_pattern.get("data"):
        df_pattern = pd.DataFrame(ctr_cvr_pattern["data"])
        fig = px.scatter(df_pattern, x="ctr", y="cvr", text="name", color="product",
                         labels={"ctr": "CTR", "cvr": "CVR"}, title="CTR vs CVR 소재 맵")
        fig.update_traces(textposition="top center", marker=dict(size=12))
        fig.update_layout(template="plotly_dark", plot_bgcolor="#0a192f", paper_bgcolor="#0a192f", height=500)
        st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════
# 탭 5: 일별 트렌드
# ═══════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("## 📈 일별 트렌드")
    if not daily_df.empty:
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            subplot_titles=("노출", "클릭", "전환(Action)"), vertical_spacing=0.08)
        fig.add_trace(go.Scatter(x=daily_df["date"], y=daily_df["total_imps"],
                                 mode="lines+markers", name="Total 노출", line=dict(color="#64ffda")), row=1, col=1)
        fig.add_trace(go.Scatter(x=daily_df["date"], y=daily_df["meta_conv_imps"],
                                 mode="lines", name="META(전환)", line=dict(color="#ffd700", dash="dot")), row=1, col=1)
        fig.add_trace(go.Scatter(x=daily_df["date"], y=daily_df["total_clicks"],
                                 mode="lines+markers", name="Total 클릭", line=dict(color="#a78bfa")), row=2, col=1)
        fig.add_trace(go.Scatter(x=daily_df["date"], y=daily_df["total_actions"],
                                 mode="lines+markers", name="Total 전환", line=dict(color="#ff6b6b"), fill="tozeroy"), row=3, col=1)
        fig.update_layout(template="plotly_dark", plot_bgcolor="#0a192f", paper_bgcolor="#0a192f",
                          height=700, legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 💰 일별 비용")
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=daily_df["date"], y=daily_df["total_cost"], marker_color="#233554", name="일 비용"))
        fig2.update_layout(template="plotly_dark", plot_bgcolor="#0a192f", paper_bgcolor="#0a192f",
                           height=300, yaxis_title="비용 (₩)")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Daily 데이터를 찾을 수 없습니다.")


# ═══════════════════════════════════════════════════════
# 탭 6: 효율 진단
# ═══════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("## ⚠️ 효율 저조 소재 진단")
    if low_performers:
        for c in low_performers:
            st.markdown(
                f'<div class="diag-box">'
                f'<b>{c["product"]} {c["name"]}</b> — '
                f'ROAS {c["roas"]:.1%} (평균 대비 {c["vs_avg_roas"]:+.1f}%)<br>'
                f'Imps {c["impressions"]:,.0f} / Clicks {c["clicks"]:,.0f} / Actions {c["actions"]:,.0f}<br>'
                + "<br>".join(f"→ {d}" for d in c.get("diagnosis", []))
                + '</div>', unsafe_allow_html=True)
    else:
        st.success("효율 저조 소재가 없거나 전환 데이터가 부족합니다.")

    st.divider()
    st.markdown("### 🔀 소재 1:1 비교")
    creative_names = [f"{c['product']} {c['name']}" for c in creatives]
    comp_col1, comp_col2 = st.columns(2)
    with comp_col1:
        sel1 = st.selectbox("소재 A", creative_names, index=0, key="comp_a")
    with comp_col2:
        sel2 = st.selectbox("소재 B", creative_names, index=min(1, len(creative_names)-1), key="comp_b")

    if sel1 and sel2:
        c1_data = creatives[creative_names.index(sel1)]
        c2_data = creatives[creative_names.index(sel2)]
        metrics = ["impressions", "clicks", "actions", "ctr", "cvr", "roas", "cpc", "cpa", "spent"]
        labels = ["노출", "클릭", "전환", "CTR", "CVR", "ROAS", "CPC", "CPA", "소진비"]

        def fmt_val(val, metric):
            if metric in ("ctr", "cvr", "roas"):
                return f"{val:.3%}" if val else "-"
            elif metric in ("cpc", "cpa", "spent"):
                return f"₩{val:,.0f}" if val else "-"
            else:
                return f"{val:,.0f}" if val else "-"

        formatted = pd.DataFrame({
            "지표": labels,
            sel1: [fmt_val(c1_data.get(m, 0), m) for m in metrics],
            sel2: [fmt_val(c2_data.get(m, 0), m) for m in metrics],
        })
        st.dataframe(formatted, use_container_width=True, hide_index=True)

        st.markdown("**속성 비교**")
        attr_comp = pd.DataFrame({
            "속성": [schema["label"] for schema in ATTRIBUTE_SCHEMA.values()],
            sel1: [c1_data.get(k, "-") or "-" for k in ATTRIBUTE_SCHEMA],
            sel2: [c2_data.get(k, "-") or "-" for k in ATTRIBUTE_SCHEMA],
        })
        st.dataframe(attr_comp, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════
# 탭 7: 제작 브리프
# ═══════════════════════════════════════════════════════
with tabs[6]:
    st.markdown("## 📝 제작 브리프")
    if briefs:
        for i, brief in enumerate(briefs):
            with st.expander(f"📋 {brief['title']} — {brief['subtitle']}", expanded=(i == 0)):
                st.markdown(f"**우선순위:** {brief['priority']}")
                st.markdown(f"**KPI 목표:** {brief['kpi_target']}")
                st.markdown(f"**추천 형식:** {brief['recommended_format']}")
                st.markdown("**참조 소재:**")
                for ref in brief["reference_creatives"]:
                    st.markdown(f"- {ref}")
                col_do, col_dont = st.columns(2)
                with col_do:
                    st.markdown("**✅ DO**")
                    for item in brief["do"]:
                        st.markdown(f"- {item}")
                with col_dont:
                    st.markdown("**❌ DON'T**")
                    for item in brief["dont"]:
                        st.markdown(f"- {item}")
                avg = brief["avg_metrics"]
                st.caption(f"참조 소재 평균 — CTR: {avg['ctr']:.3%} | CVR: {avg['cvr']:.2%} | ROAS: {avg['roas']:.1%}")
    else:
        st.info("전환 소재 데이터가 부족하여 브리프를 생성할 수 없습니다.")


# ═══════════════════════════════════════════════════════
# 탭 8: HTML 다운로드
# ═══════════════════════════════════════════════════════
with tabs[7]:
    st.markdown("## ⬇️ HTML 대시보드 다운로드")
    st.markdown("분석 결과를 독립 실행형 HTML 파일로 다운로드합니다.")

    if st.button("🔨 HTML 대시보드 생성", type="primary"):
        with st.spinner("HTML 생성 중..."):
            html_content = generate_html_dashboard(
                meta=meta, creatives=creatives, kpi=kpi, insights=insights,
                briefs=briefs, roas_ranking=roas_ranking, low_performers=low_performers,
                product_analysis=product_analysis, format_analysis=format_analysis,
                ctr_cvr_pattern=ctr_cvr_pattern,
            )
        filename = f"{meta.get('client', 'campaign')}_{meta.get('campaign', '')}_{datetime.now().strftime('%y%m%d')}_인사이트.html"
        st.download_button(label="⬇️ HTML 다운로드", data=html_content, file_name=filename, mime="text/html")
        st.success(f"✅ HTML 생성 완료! ({len(html_content):,} bytes)")
