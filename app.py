"""
GOLDNEX SM본부 · Creative Intelligence
소재 인사이트 대시보드 — Streamlit 프로토타입

사용법:
1. pip install streamlit pandas openpyxl plotly
2. streamlit run app.py
3. 엑셀 파일 업로드 → 자동 분석
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import base64
from io import BytesIO
from utils.parser import parse_excel
from utils.analyzer import analyze_creatives, generate_brief
from utils.image_extractor import extract_images

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="GOLDNEX · Creative Intelligence",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CUSTOM CSS =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;900&family=Outfit:wght@300;400;500;600;700;800;900&display=swap');
.stApp {font-family: 'Noto Sans KR', sans-serif;}
.main-header {
    background: linear-gradient(135deg, #1A1D26, #2D3348);
    color: white; padding: 20px 28px; border-radius: 14px; margin-bottom: 20px;
}
.main-header h1 {font-family: 'Outfit'; font-weight: 900; font-size: 24px; margin: 0;}
.main-header p {font-size: 12px; opacity: 0.6; margin-top: 4px;}
.kpi-card {
    background: white; border: 1px solid #E2E5EA; border-radius: 14px;
    padding: 16px 18px; text-align: center;
}
.kpi-value {font-family: 'Outfit'; font-size: 28px; font-weight: 800;}
.kpi-label {font-size: 10px; color: #6B7280; text-transform: uppercase; letter-spacing: 0.5px;}
.tier-S {background: #D4A017; color: white; padding: 2px 10px; border-radius: 12px; font-weight: 800; font-size: 11px;}
.tier-A {background: #3B6CF5; color: white; padding: 2px 10px; border-radius: 12px; font-weight: 800; font-size: 11px;}
.tier-B {background: #10B981; color: white; padding: 2px 10px; border-radius: 12px; font-weight: 800; font-size: 11px;}
.tier-C {background: #9CA3AF; color: white; padding: 2px 10px; border-radius: 12px; font-weight: 800; font-size: 11px;}
.tier-D {background: #EF4444; color: white; padding: 2px 10px; border-radius: 12px; font-weight: 800; font-size: 11px;}
.insight-box {
    background: white; border: 1px solid #E2E5EA; border-left: 4px solid #3B6CF5;
    border-radius: 0 14px 14px 0; padding: 14px 18px; margin-bottom: 10px;
}
.insight-good {border-left-color: #10B981;}
.insight-warn {border-left-color: #FF6B2C;}
.insight-bad {border-left-color: #EF4444;}
.brief-card {
    border: 2px solid; border-radius: 14px; overflow: hidden;
}
</style>
""", unsafe_allow_html=True)


def main():
    # ===== SIDEBAR =====
    with st.sidebar:
        st.markdown("### 🎨 Creative Intelligence")
        st.markdown("**GOLDNEX SM본부**")
        st.markdown("---")
        
        uploaded_file = st.file_uploader(
            "📂 캠페인 리포트 업로드",
            type=['xlsx', 'xls'],
            help="올영세일 캠페인 리포트 엑셀 파일을 업로드하세요"
        )
        
        st.markdown("---")
        st.markdown("##### 📖 사용법")
        st.markdown("""
        1. 엑셀 파일 업로드
        2. 자동 파싱 & 소재 분류
        3. 탭별 인사이트 확인
        4. 제작 브리프 생성 & 출력
        """)
        
        st.markdown("---")
        st.markdown("##### 🔢 지표 기준")
        st.markdown("""
        - **CTR**: 0.5%↑ 양호, 1%↑ 우수
        - **ROAS**: 3x↑ 양호, 6x↑ 우수
        - **CPA**: 낮을수록 효율적
        - **티어**: S > A > B > C > D
        """)
    
    # ===== HEADER =====
    st.markdown("""
    <div class="main-header">
        <h1>🎨 Creative Intelligence Dashboard</h1>
        <p>GOLDNEX SM본부 · 소재 인사이트 자동 분석 & 제작 브리프 생성</p>
    </div>
    """, unsafe_allow_html=True)
    
    if uploaded_file is None:
        show_landing_page()
        return
    
    # ===== PARSE DATA =====
    with st.spinner("📊 엑셀 파싱 중..."):
        try:
            data = parse_excel(uploaded_file)
            images = extract_images(uploaded_file)
        except Exception as e:
            st.error(f"파싱 오류: {e}")
            st.info("엑셀 파일 형식을 확인해주세요. 'Creative' 시트와 'Summary' 시트가 필요합니다.")
            return
    
    with st.spinner("🔬 소재 분석 중..."):
        analysis = analyze_creatives(data, images)
    
    # ===== TABS =====
    tabs = st.tabs([
        "📊 성과 총괄",
        "🎨 소재 갤러리",
        "🔬 속성 분석",
        "✍️ 무드·카피",
        "📋 제작 브리프",
        "📈 매체·트렌드"
    ])
    
    with tabs[0]:
        render_overview(data, analysis)
    
    with tabs[1]:
        render_gallery(data, analysis, images)
    
    with tabs[2]:
        render_attributes(data, analysis)
    
    with tabs[3]:
        render_mood_copy(data, analysis)
    
    with tabs[4]:
        render_brief(data, analysis, images)
    
    with tabs[5]:
        render_media_trend(data)


def show_landing_page():
    """Show landing page when no file is uploaded"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 👋 환영합니다")
        st.markdown("좌측 사이드바에서 **캠페인 리포트 엑셀 파일**을 업로드하면 자동으로 분석이 시작됩니다.")
        
        st.markdown("### 📂 지원 파일 형식")
        st.markdown("""
        - 올영세일 캠페인 리포트 (`.xlsx`)
        - 필수 시트: `Creative`, `Summary`
        - 선택 시트: `Daily`, `META(전환)`, `META(장바구니)` 등
        """)
        
        st.markdown("### 🔄 분석 프로세스")
        st.markdown("""
        1. **데이터 파싱** — 엑셀에서 소재별 성과 데이터 추출
        2. **이미지 추출** — 엑셀에 포함된 소재 이미지 자동 추출
        3. **속성 분류** — 비주얼 유형, 무드, Hook, 레이아웃 자동/수동 분류
        4. **인사이트 생성** — 속성별 성과 분석 + 효율 저조 진단
        5. **제작 브리프** — 다음 캠페인 소재 제작 지시서 자동 생성
        """)


def render_overview(data, analysis):
    """Render overview tab"""
    creatives = analysis['creatives']
    media = data.get('media', [])
    
    # KPIs
    total_imps = sum(c.get('imps', 0) for c in creatives)
    total_clicks = sum(c.get('clicks', 0) for c in creatives)
    total_action = sum(c.get('action', 0) for c in creatives)
    total_rev = sum(c.get('rev', 0) for c in creatives)
    total_cost = sum(c.get('cost', 0) for c in creatives)
    avg_ctr = total_clicks / total_imps if total_imps else 0
    avg_roas = total_rev / total_cost if total_cost else 0
    
    cols = st.columns(6)
    kpi_data = [
        ("총 노출", f"{total_imps:,.0f}", "#3B6CF5"),
        ("총 클릭", f"{total_clicks:,.0f}", "#10B981"),
        ("CTR", f"{avg_ctr*100:.2f}%", "#FF6B2C"),
        ("전환(Action)", f"{total_action:,.0f}건", "#8B5CF6"),
        ("매출", f"₩{total_rev:,.0f}", "#EF4444"),
        ("ROAS", f"{avg_roas:.2f}x", "#D4A017"),
    ]
    
    for col, (label, value, color) in zip(cols, kpi_data):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value" style="color:{color}">{value}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ROAS Ranking Chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 소재별 ROAS 랭킹")
        df = pd.DataFrame(creatives).sort_values('roas', ascending=True)
        fig = px.bar(df, x='roas', y='name', orientation='h',
                     color='product', color_discrete_sequence=['#3B6CF5', '#10B981', '#8B5CF6', '#FF6B2C'],
                     labels={'roas': 'ROAS', 'name': '', 'product': '제품'})
        fig.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0), 
                         paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("##### 제품별 전환·ROAS 비교")
        products = df.groupby('product').agg({
            'action': 'sum', 'rev': 'sum', 'cost': 'sum'
        }).reset_index()
        products['roas'] = products['rev'] / products['cost']
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=products['product'], y=products['action'], name='Action',
                            marker_color='#3B6CF5', opacity=0.7), secondary_y=False)
        fig.add_trace(go.Scatter(x=products['product'], y=products['roas'], name='ROAS',
                                mode='lines+markers', marker=dict(size=10, color='#FF6B2C'),
                                line=dict(color='#FF6B2C', width=2)), secondary_y=True)
        fig.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0),
                         paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig.update_yaxes(title_text="Action", secondary_y=False)
        fig.update_yaxes(title_text="ROAS", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)
    
    # Low Performers
    avg_roas_val = avg_roas
    low = [c for c in creatives if c['roas'] < avg_roas_val and c.get('visual_type') != '카탈로그']
    if low:
        st.markdown("##### 🚨 효율 저조 소재 진단")
        for c in sorted(low, key=lambda x: x['roas']):
            tier_class = f"tier-{c.get('tier', 'C')}"
            st.markdown(f"""
            <div class="insight-box insight-bad">
                <strong>{c['product']} {c['name']}</strong> — ROAS {c['roas']:.2f}x 
                <span class="{tier_class}">{c.get('tier', 'C')}</span><br>
                <span style="color:#6B7280;font-size:11px">
                CTR {c['ctr']*100:.2f}% · CPC ₩{c['cpc']:,.0f} · Action {c['action']}건 · 
                소진 ₩{c['cost']:,.0f}
                </span>
            </div>
            """, unsafe_allow_html=True)
    
    # Detailed Table
    st.markdown("##### 소재 성과 상세")
    df_display = pd.DataFrame(creatives)[['product', 'name', 'imps', 'clicks', 'action', 'rev', 'ctr', 'cpc', 'cpa', 'roas', 'cost', 'tier']]
    df_display.columns = ['제품', '소재', '노출', '클릭', 'Action', '매출', 'CTR', 'CPC', 'CPA', 'ROAS', '소진광고비', '티어']
    df_display['CTR'] = df_display['CTR'].apply(lambda x: f"{x*100:.2f}%")
    df_display['ROAS'] = df_display['ROAS'].apply(lambda x: f"{x:.2f}x")
    df_display['매출'] = df_display['매출'].apply(lambda x: f"₩{x:,.0f}")
    df_display['CPC'] = df_display['CPC'].apply(lambda x: f"₩{x:,.0f}")
    df_display['CPA'] = df_display['CPA'].apply(lambda x: f"₩{x:,.0f}" if x > 0 else '-')
    df_display['소진광고비'] = df_display['소진광고비'].apply(lambda x: f"₩{x:,.0f}")
    df_display['노출'] = df_display['노출'].apply(lambda x: f"{x:,.0f}")
    df_display['클릭'] = df_display['클릭'].apply(lambda x: f"{x:,.0f}")
    st.dataframe(df_display.sort_values('ROAS', ascending=False), use_container_width=True, hide_index=True)


def render_gallery(data, analysis, images):
    """Render creative gallery"""
    creatives = analysis['creatives']
    
    for product in sorted(set(c['product'] for c in creatives)):
        st.markdown(f"##### {product}")
        items = [c for c in creatives if c['product'] == product and c.get('img_b64')]
        
        cols = st.columns(min(len(items), 5))
        for col, c in zip(cols, items):
            with col:
                # Show image
                if c.get('img_b64'):
                    st.image(f"data:image/png;base64,{c['img_b64']}", use_container_width=True)
                
                # Tier badge + name
                tier = c.get('tier', 'B')
                st.markdown(f"<span class='tier-{tier}'>{tier}</span> **{c['name']}**", unsafe_allow_html=True)
                
                # Tags
                tags = []
                if c.get('mood'): tags.append(c['mood'])
                if c.get('hook'): tags.append(c['hook'])
                if c.get('layout_code'): tags.append(f"{c['layout_code']}패턴")
                st.caption(" · ".join(tags))
                
                # Metrics
                st.metric("ROAS", f"{c['roas']:.2f}x")
                cols_m = st.columns(2)
                cols_m[0].metric("CTR", f"{c['ctr']*100:.2f}%")
                cols_m[1].metric("CPA", f"₩{c['cpa']:,.0f}" if c['cpa'] > 0 else "-")
    
    # Layout Review
    st.markdown("---")
    st.markdown("##### 📐 소재 레이아웃 리뷰")
    st.info("소재를 선택하면 요소 배치를 확인하고 수정할 수 있습니다.")
    
    items_with_img = [c for c in creatives if c.get('img_b64')]
    if items_with_img:
        selected = st.selectbox(
            "소재 선택",
            options=range(len(items_with_img)),
            format_func=lambda i: f"{items_with_img[i]['product']} {items_with_img[i]['name']} (ROAS {items_with_img[i]['roas']:.2f}x)"
        )
        
        c = items_with_img[selected]
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if c.get('img_b64'):
                st.image(f"data:image/png;base64,{c['img_b64']}", width=200)
        
        with col2:
            st.markdown(f"**{c['product']} {c['name']}** — ROAS {c['roas']:.2f}x · Action {c['action']}건")
            
            # Editable grid
            positions = ['좌상', '중상', '우상', '좌중', '중앙', '우중', '좌하', '중하', '우하']
            elements = ['비움', '카피', '제품', '모델', '가격', '할인율', '배지', '텍스처', 'GWP', '소품', '1등']
            
            grid_data = c.get('grid', {})
            pos_keys = ['TL', 'TC', 'TR', 'ML', 'MC', 'MR', 'BL', 'BC', 'BR']
            
            grid_cols = st.columns(3)
            for i, (pos, key) in enumerate(zip(positions, pos_keys)):
                col_idx = i % 3
                default = grid_data.get(key, '비움')
                default_idx = elements.index(default) if default in elements else 0
                grid_cols[col_idx].selectbox(pos, elements, index=default_idx, key=f"grid_{selected}_{key}")


def render_attributes(data, analysis):
    """Render attribute analysis"""
    creatives = analysis['creatives']
    dc = [c for c in creatives if c.get('visual_type') != '카탈로그']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 비주얼 유형별 ROAS")
        vis_data = {}
        for c in dc:
            vt = c.get('visual_type', '기타')
            if vt not in vis_data:
                vis_data[vt] = {'rev': 0, 'cost': 0, 'count': 0}
            vis_data[vt]['rev'] += c['rev']
            vis_data[vt]['cost'] += c['cost']
            vis_data[vt]['count'] += 1
        
        vis_df = pd.DataFrame([
            {'유형': k, 'ROAS': v['rev']/v['cost'] if v['cost'] else 0, 'n': v['count']}
            for k, v in vis_data.items()
        ])
        fig = px.bar(vis_df, x='유형', y='ROAS', text=vis_df.apply(lambda r: f"{r['ROAS']:.2f}x (n={r['n']})", axis=1),
                     color_discrete_sequence=['#3B6CF5'])
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("##### Hook 유형별 ROAS")
        hook_data = {}
        for c in dc:
            h = c.get('hook', '기타')
            if h not in hook_data:
                hook_data[h] = {'rev': 0, 'cost': 0, 'count': 0}
            hook_data[h]['rev'] += c['rev']
            hook_data[h]['cost'] += c['cost']
            hook_data[h]['count'] += 1
        
        hook_df = pd.DataFrame([
            {'Hook': k, 'ROAS': v['rev']/v['cost'] if v['cost'] else 0, 'n': v['count']}
            for k, v in hook_data.items()
        ])
        fig = px.bar(hook_df, x='Hook', y='ROAS', text=hook_df.apply(lambda r: f"{r['ROAS']:.2f}x (n={r['n']})", axis=1),
                     color_discrete_sequence=['#10B981'])
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)
    
    # Insights
    for ins in analysis.get('attribute_insights', []):
        cls = 'insight-good' if ins['type'] == 'good' else 'insight-warn' if ins['type'] == 'warn' else 'insight-bad'
        st.markdown(f"""
        <div class="insight-box {cls}">
            <strong>{ins['title']}</strong><br>
            <span style="color:#6B7280;font-size:11px">{ins['body']}</span>
        </div>
        """, unsafe_allow_html=True)


def render_mood_copy(data, analysis):
    """Render mood and copy analysis"""
    creatives = analysis['creatives']
    dc = [c for c in creatives if c.get('visual_type') != '카탈로그']
    
    # Mood Grid
    st.markdown("##### 🎭 소재 무드 확장 분류")
    moods = {}
    for c in dc:
        m = c.get('mood_ex', c.get('mood', '기타'))
        if m not in moods:
            moods[m] = {'rev': 0, 'cost': 0, 'items': []}
        moods[m]['rev'] += c['rev']
        moods[m]['cost'] += c['cost']
        moods[m]['items'].append(c)
    
    mood_cols = st.columns(len(moods))
    for col, (name, data_m) in zip(mood_cols, moods.items()):
        roas = data_m['rev'] / data_m['cost'] if data_m['cost'] else 0
        with col:
            st.metric(name, f"{roas:.2f}x", f"n={len(data_m['items'])}")
    
    st.markdown("---")
    
    # Copy Analysis Table
    st.markdown("##### ✍️ 카피 텍스트 분석")
    copy_data = []
    for c in dc:
        if c.get('main_copy') and c['main_copy'] != '-':
            copy_data.append({
                '제품': c['product'],
                '소재': c['name'],
                '메인 카피': c.get('main_copy', ''),
                '서브 카피': c.get('sub_copy', ''),
                '카피 유형': c.get('copy_type', ''),
                'ROAS': f"{c['roas']:.2f}x"
            })
    
    if copy_data:
        st.dataframe(pd.DataFrame(copy_data), use_container_width=True, hide_index=True)
    
    # Copy insights
    for ins in analysis.get('copy_insights', []):
        cls = 'insight-good' if ins['type'] == 'good' else 'insight-warn' if ins['type'] == 'warn' else ''
        st.markdown(f"""
        <div class="insight-box {cls}">
            <strong>{ins['title']}</strong><br>
            <span style="color:#6B7280;font-size:11px">{ins['body']}</span>
        </div>
        """, unsafe_allow_html=True)


def render_brief(data, analysis, images):
    """Render creative brief"""
    brief = generate_brief(analysis)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <div style="font-size:10px;letter-spacing:2px;opacity:.5">GOLDNEX SM본부 · CREATIVE BRIEF</div>
        <h1>차기 캠페인 소재 제작 브리프</h1>
        <p>분석 데이터 기반 자동 생성</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Summary
    st.markdown("##### 📌 핵심 요약")
    st.info(brief['summary'])
    
    # 3 Brief Cards
    cols = st.columns(3)
    for col, b in zip(cols, brief['briefs']):
        with col:
            st.markdown(f"###### {b['num']}: {b['title']}")
            st.markdown(f"_{b['subtitle']}_")
            
            m1, m2 = st.columns(2)
            m1.metric("목표 ROAS", b['target_roas'])
            m2.metric("목표 CPA", b['target_cpa'])
            
            st.markdown(f"""
            - **비주얼**: {b['visual']}
            - **무드**: {b['mood']}
            - **인물**: {b['person']}
            - **예산**: {b['budget']}
            """)
            
            with st.expander("상세 스펙"):
                st.markdown(f"**레이아웃:**\n{b['layout']}")
                st.markdown(f"**메인 카피:** {b['copy_main']}")
                st.markdown(f"**서브 카피:** {b['copy_sub']}")
                st.markdown(f"**A/B 변형:** {b['ab_test']}")
                st.markdown(f"**근거:** {b['rationale']}")
    
    # DO / DON'T
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### ✅ DO — 이렇게 만들어 주세요")
        for item in brief['dos']:
            st.markdown(f"✅ {item}")
    with col2:
        st.markdown("##### ❌ DON'T — 이것만은 피해 주세요")
        for item in brief['donts']:
            st.markdown(f"❌ {item}")
    
    # KPI Targets
    st.markdown("---")
    st.markdown("##### 🎯 예상 KPI 목표")
    cols = st.columns(5)
    for col, (label, value) in zip(cols, brief['kpi_targets']):
        with col:
            st.metric(label, value)


def render_media_trend(data):
    """Render media and trend analysis"""
    media = data.get('media', [])
    daily = data.get('daily', [])
    
    if media:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### 매체별 노출·클릭")
            mdf = pd.DataFrame(media)
            fig = px.bar(mdf, x='name', y='imps', color_discrete_sequence=['#3B6CF5'],
                        labels={'imps': '노출', 'name': ''})
            fig.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("##### 매체별 CPC·CTR")
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Bar(x=mdf['name'], y=mdf['cpc'], name='CPC',
                                marker_color='#FF6B2C', opacity=0.7), secondary_y=False)
            fig.add_trace(go.Scatter(x=mdf['name'], y=mdf['ctr'].apply(lambda x: x*100),
                                    name='CTR(%)', mode='lines+markers',
                                    marker=dict(size=8, color='#8B5CF6')), secondary_y=True)
            fig.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig, use_container_width=True)
    
    if daily:
        st.markdown("##### 일별 노출·Action 추이")
        ddf = pd.DataFrame(daily)
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=ddf['date'], y=ddf['imps'].apply(lambda x: x/10000),
                            name='노출(만)', marker_color='#3B6CF5', opacity=0.5), secondary_y=False)
        fig.add_trace(go.Scatter(x=ddf['date'], y=ddf['action'], name='Action',
                                mode='lines+markers', marker=dict(size=8, color='#10B981'),
                                line=dict(width=2)), secondary_y=True)
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0))
        fig.update_yaxes(title_text="노출(만)", secondary_y=False)
        fig.update_yaxes(title_text="Action", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
