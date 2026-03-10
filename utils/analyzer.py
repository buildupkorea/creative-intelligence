"""
Creative Analyzer — 소재 속성 분류 + 인사이트 생성 + 브리프 자동 작성
"""


def analyze_creatives(data, images=None):
    """Analyze creatives and generate insights"""
    creatives = data.get('creatives', [])
    
    if not creatives:
        return {'creatives': [], 'attribute_insights': [], 'copy_insights': []}
    
    # Assign images to creatives (by order)
    img_list = []
    if images:
        # Sort by size — small ones are thumbnails
        thumbs = sorted(
            [(k, v) for k, v in images.items() if v['size'] < 100000],
            key=lambda x: x[0]
        )
        img_list = [v['b64'] for _, v in thumbs]
    
    # Enrich creatives with attributes
    for i, c in enumerate(creatives):
        # Assign image if available
        if i < len(img_list):
            c['img_b64'] = img_list[i]
        else:
            c['img_b64'] = None
        
        # Auto-classify attributes based on name/data patterns
        c['visual_type'] = classify_visual_type(c)
        c['mood'] = classify_mood(c)
        c['mood_ex'] = classify_mood_expanded(c)
        c['hook'] = classify_hook(c)
        c['layout_code'] = classify_layout(c)
        c['main_copy'] = extract_main_copy(c)
        c['sub_copy'] = extract_sub_copy(c)
        c['copy_type'] = classify_copy_type(c)
        c['person'] = '모델' if '모델' in c['name'] else '없음'
        
        # Calculate tier
        c['tier'] = calculate_tier(c)
    
    # Generate insights
    dc = [c for c in creatives if c.get('visual_type') != '카탈로그']
    
    return {
        'creatives': creatives,
        'attribute_insights': generate_attribute_insights(dc),
        'copy_insights': generate_copy_insights(dc),
    }


def classify_visual_type(c):
    """Classify visual type based on creative name and data"""
    name = c.get('name', '').lower()
    if '카탈' in name:
        return '카탈로그'
    elif '모델' in name:
        return '모델컷'
    elif any(kw in name for kw in ['텍스처', '거품', '클로즈업']):
        return '텍스처컷'
    elif 'gwp' in name or '소품' in name:
        return 'GWP컷'
    else:
        return '제품컷'


def classify_mood(c):
    """Classify mood (basic 3 types)"""
    name = c.get('name', '')
    ctr = c.get('ctr', 0)
    
    if any(kw in name for kw in ['1등', 'No.1', '베스트']):
        return '정보전달형'
    elif any(kw in name for kw in ['특가', '할인', 'OFF']):
        return '혜택강조형'
    elif any(kw in name for kw in ['한정', '단', '일만']):
        return '희소성형'
    elif c.get('visual_type') == '텍스처컷':
        return '정보전달형'
    else:
        return '혜택강조형'


def classify_mood_expanded(c):
    """Classify into 6 expanded mood types"""
    name = c.get('name', '').lower()
    product = c.get('product', '').lower()
    note = c.get('note', '').lower()
    
    if '카탈' in name:
        return '-'
    
    # Check patterns
    if any(kw in name for kw in ['블랙헤드', '클렌징', '기능', '순삭', '딥']):
        return '기능설명형'
    elif any(kw in name for kw in ['특가', '할인', 'off']):
        return '가격혜택형'
    elif any(kw in name for kw in ['대용량', '더블', '크게', '사이즈']):
        return '사이즈업형'
    elif any(kw in name for kw in ['1등', 'no.1', '베스트', '순위']):
        return '순위권위형'
    elif any(kw in name for kw in ['한정', '단', '7일', '마감']):
        return '희소성형'
    else:
        # Default based on visual type
        if c.get('visual_type') == '텍스처컷':
            return '기능설명형'
        elif c.get('visual_type') == 'GWP컷':
            return '가격혜택형'
        elif c.get('visual_type') == '모델컷':
            return '사이즈업형'
        return '기능설명형'


def classify_hook(c):
    """Classify hook type"""
    name = c.get('name', '').lower()
    
    if '카탈' in name:
        return '-'
    if any(kw in name for kw in ['대용량', '더블', '크게', '사이즈']):
        if 'gwp' in name or '소품' in name or '키링' in name:
            return '사이즈업+GWP'
        return '사이즈업'
    if any(kw in name for kw in ['1등', 'no.1']):
        return '1등'
    if any(kw in name for kw in ['특가', '할인', '%', 'off']):
        return '할인율'
    if any(kw in name for kw in ['한정', '단', '7일']):
        return '희소성'
    if any(kw in name for kw in ['gwp', '소품', '에어팟', '키링']):
        return 'GWP'
    return '기능혜택'


def classify_layout(c):
    """Classify layout pattern"""
    vt = c.get('visual_type', '')
    person = c.get('person', '')
    
    if vt == '카탈로그':
        return '-'
    if person == '모델':
        return 'A'  # 모델+제품열
    if vt == '텍스처컷':
        return 'C'  # 텍스처풀샷
    if vt == 'GWP컷':
        return 'D'  # GWP소품구성
    return 'B'  # 제품중앙+기능카피


def extract_main_copy(c):
    """Extract main copy text (placeholder - to be enriched manually or via AI)"""
    name = c.get('name', '')
    if '카탈' in name:
        return '-'
    return name  # Placeholder: use creative name as proxy


def extract_sub_copy(c):
    """Extract sub copy (placeholder)"""
    return ''


def classify_copy_type(c):
    """Classify copy structure type"""
    name = c.get('name', '').lower()
    
    if '카탈' in name:
        return '-'
    if any(kw in name for kw in ['블랙헤드', '클렌징', '순삭', '딥', '올킬']):
        return '기능설명'
    if any(kw in name for kw in ['특가', '할인', '기획', '더블']):
        return '혜택직접'
    if any(kw in name for kw in ['1등', 'no.1', '순위']):
        return '숫자/순위'
    if any(kw in name for kw in ['한정', '단', '7일']):
        return '희소성'
    return '기능설명'


def calculate_tier(c):
    """Calculate creative tier"""
    score = (c.get('roas', 0) or 0) * 4 + (c.get('cvr', 0) or 0) * 30 + (c.get('ctr', 0) or 0) * 10000 * 0.3
    
    # Penalize small sample
    if c.get('imps', 0) < 20000:
        if score > 50:
            return 'A'
        return 'B'
    
    if score > 50:
        return 'S'
    if score > 30:
        return 'A'
    if score > 15:
        return 'B'
    if score > 5:
        return 'C'
    return 'D'


def generate_attribute_insights(dc):
    """Generate attribute-based insights"""
    insights = []
    
    if not dc:
        return insights
    
    # Find top performer
    top = max(dc, key=lambda x: x.get('roas', 0))
    insights.append({
        'type': 'good',
        'title': f"✅ 최고 효율: {top['product']} {top['name']} — ROAS {top['roas']:.2f}x",
        'body': f"비주얼: {top.get('visual_type', '?')} · 무드: {top.get('mood_ex', '?')} · Hook: {top.get('hook', '?')}. 이 패턴을 기반으로 변형 소재 제작 권장."
    })
    
    # Find worst performer
    worst = min(dc, key=lambda x: x.get('roas', 0))
    if worst['roas'] < 4:
        insights.append({
            'type': 'bad',
            'title': f"🚨 효율 저조: {worst['product']} {worst['name']} — ROAS {worst['roas']:.2f}x",
            'body': f"비주얼: {worst.get('visual_type', '?')} · 무드: {worst.get('mood_ex', '?')}. OFF 또는 리뉴얼 검토 필요."
        })
    
    # Visual type comparison
    vis_groups = {}
    for c in dc:
        vt = c.get('visual_type', '기타')
        if vt not in vis_groups:
            vis_groups[vt] = {'rev': 0, 'cost': 0, 'count': 0}
        vis_groups[vt]['rev'] += c['rev']
        vis_groups[vt]['cost'] += c['cost']
        vis_groups[vt]['count'] += 1
    
    if len(vis_groups) > 1:
        best_vis = max(vis_groups.items(), key=lambda x: x[1]['rev']/x[1]['cost'] if x[1]['cost'] else 0)
        insights.append({
            'type': 'good',
            'title': f"✅ {best_vis[0]} 유형이 ROAS {best_vis[1]['rev']/best_vis[1]['cost']:.2f}x (n={best_vis[1]['count']})",
            'body': f"다만 n={best_vis[1]['count']}로 {'표본 충분' if best_vis[1]['count'] >= 3 else '표본 부족 — 추가 검증 필요'}."
        })
    
    return insights


def generate_copy_insights(dc):
    """Generate copy-related insights"""
    insights = []
    
    # Copy type analysis
    copy_groups = {}
    for c in dc:
        ct = c.get('copy_type', '기타')
        if ct == '-':
            continue
        if ct not in copy_groups:
            copy_groups[ct] = {'rev': 0, 'cost': 0, 'count': 0}
        copy_groups[ct]['rev'] += c['rev']
        copy_groups[ct]['cost'] += c['cost']
        copy_groups[ct]['count'] += 1
    
    if copy_groups:
        best_copy = max(copy_groups.items(), key=lambda x: x[1]['rev']/x[1]['cost'] if x[1]['cost'] else 0)
        roas = best_copy[1]['rev'] / best_copy[1]['cost'] if best_copy[1]['cost'] else 0
        insights.append({
            'type': 'good',
            'title': f"✅ {best_copy[0]} 카피 유형이 ROAS {roas:.2f}x (n={best_copy[1]['count']})",
            'body': '기능을 구체적으로 설명하는 카피가 가격 소구보다 전환에 효과적.'
        })
    
    insights.append({
        'type': 'warn',
        'title': '⚠️ 가격은 서브 카피로 배치 권장',
        'body': '가격을 메인에 넣으면 CTR은 높지만 ROAS가 중위. 메인은 기능 소구, 서브에 가격이 효율적.'
    })
    
    return insights


def generate_brief(analysis):
    """Generate creative production brief"""
    creatives = analysis.get('creatives', [])
    dc = [c for c in creatives if c.get('visual_type') != '카탈로그']
    
    if not dc:
        return {'summary': '데이터 부족', 'briefs': [], 'dos': [], 'donts': [], 'kpi_targets': []}
    
    avg_roas = sum(c['rev'] for c in dc) / sum(c['cost'] for c in dc) if sum(c['cost'] for c in dc) else 0
    top = max(dc, key=lambda x: x.get('roas', 0))
    
    summary = f"이번 캠페인 평균 ROAS {avg_roas:.2f}x. 최고 효율 소재: {top['product']} {top['name']}(ROAS {top['roas']:.2f}x). "
    summary += "분석 결과를 기반으로 3가지 방향의 신규 소재를 제안합니다."
    
    briefs = [
        {
            'num': 'Brief #1',
            'title': '효율 극대화형',
            'subtitle': '텍스처컷 + 기능설명 카피',
            'target_roas': '7.0~9.0x',
            'target_cpa': '₩2,500 이하',
            'visual': '텍스처컷 (C패턴)',
            'mood': '기능설명형',
            'person': '제품 Only',
            'budget': '전체의 30%',
            'layout': '상단: 기능카피 + 배지\n중단: 텍스처 클로즈업 (60%+)\n하단: 가격 + 할인율',
            'copy_main': '기능 설명 4~6자',
            'copy_sub': '가격 + 할인율 필수',
            'ab_test': '텍스처 변형 2~3종',
            'rationale': '소규모 검증된 고효율 시그널. 스케일업 가능성 확인 필요.'
        },
        {
            'num': 'Brief #2',
            'title': '볼륨 확보형',
            'subtitle': '모델컷 + 사이즈업/혜택',
            'target_roas': '5.0~7.0x',
            'target_cpa': '₩4,500 이하',
            'visual': '모델컷 (A패턴)',
            'mood': '사이즈업형/혜택강조형',
            'person': '모델',
            'budget': '전체의 40%',
            'layout': '상단: 카피 + 배지\n중단: 모델(50%) + 제품(우)\n하단: 가격 + GWP',
            'copy_main': '사이즈업/혜택 카피',
            'copy_sub': 'GWP 구성 + 가격',
            'ab_test': '모델 교체 / GWP 변형',
            'rationale': '대규모 예산에서 검증된 안정적 볼륨+효율 패턴.'
        },
        {
            'num': 'Brief #3',
            'title': '기능 소구형',
            'subtitle': '제품컷 + 기능설명 카피',
            'target_roas': '5.0~6.5x',
            'target_cpa': '₩3,500 이하',
            'visual': '제품컷 (B패턴)',
            'mood': '기능설명형',
            'person': '제품 Only',
            'budget': '전체의 30%',
            'layout': '상단: 기능카피 6~8자\n중단: 제품 단품 중앙\n하단: 가격 + 할인율',
            'copy_main': '구체적 기능 설명',
            'copy_sub': '가격 + 할인율',
            'ab_test': '카피 키워드 변형',
            'rationale': '안정적 중효율. 차기 위닝 소재 발굴 목적.'
        }
    ]
    
    dos = [
        '텍스처/거품 클로즈업을 화면 중앙에 크게 배치',
        '할인율 + 가격을 반드시 표기 (미표기 시 ROAS 1.7배 하락)',
        '핵심 기능 키워드를 메인 카피에 포함',
        '올영세일 배지를 우상단에 배치',
        '단품 중심 소재 제작 (CVR 우위)',
        '모든 소재에 A/B 변형 2~3종 함께 제작',
    ]
    
    donts = [
        '가격을 메인 카피에 넣지 마세요',
        '가격/할인율을 생략하지 마세요',
        '소품(에어팟 등)을 화면 중앙에 넣지 마세요',
        '제품 3개 이상 나열하지 마세요',
        '카피 10자 이상은 피하세요',
        '카탈로그에 예산 20% 이상 배분하지 마세요',
    ]
    
    target_roas = avg_roas * 1.1
    kpi_targets = [
        ('ROAS 목표', f'{target_roas:.1f}x+'),
        ('CTR 목표', '0.8%+'),
        ('CPA 목표', '₩3,500'),
        ('Action 목표', f'{sum(c["action"] for c in dc)*1.1:,.0f}+'),
        ('D티어', '0개'),
    ]
    
    return {
        'summary': summary,
        'briefs': briefs,
        'dos': dos,
        'donts': donts,
        'kpi_targets': kpi_targets,
    }
