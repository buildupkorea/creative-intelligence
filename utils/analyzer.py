"""
analyzer.py — 데이터 기반 인사이트 자동 생성
티어 분류, 속성 분석, 효율 진단, 제작 브리프를 자동 생성합니다.
"""
import pandas as pd
from typing import Dict, List, Tuple, Optional


# ── 티어 분류 ──────────────────────────────────────────
def calc_tier_score(row: Dict) -> float:
    """
    스코어 = ROAS × 4 + CVR × 30 + CTR × 10000 × 0.3
    """
    roas = row.get("roas", 0) or 0
    cvr = row.get("cvr", 0) or 0
    ctr = row.get("ctr", 0) or 0
    return roas * 4 + cvr * 30 + ctr * 10000 * 0.3


def assign_tier(score: float, impressions: float) -> str:
    """
    S: 50+, A: 30+, B: 15+, C: 5+, D: 5 미만
    노출 5만 미만 → 한 단계 하향
    """
    if score >= 50:
        tier = "S"
    elif score >= 30:
        tier = "A"
    elif score >= 15:
        tier = "B"
    elif score >= 5:
        tier = "C"
    else:
        tier = "D"
    
    # 노출 5만 미만 → 한 단계 하향
    if impressions < 50000:
        tier_order = ["S", "A", "B", "C", "D"]
        idx = tier_order.index(tier)
        if idx < len(tier_order) - 1:
            tier = tier_order[idx + 1]
    
    return tier


def classify_creatives(creatives: List[Dict]) -> List[Dict]:
    """모든 소재에 티어 점수와 등급 부여"""
    for c in creatives:
        c["tier_score"] = calc_tier_score(c)
        c["tier"] = assign_tier(c["tier_score"], c.get("impressions", 0))
    return creatives


# ── KPI 요약 ──────────────────────────────────────────
def generate_kpi_summary(meta: Dict, creatives: List[Dict]) -> Dict:
    """전체 KPI 요약 생성"""
    budget = meta.get("budget", 0) or 0
    total = meta.get("total_performance", {})
    
    # 소재 중 전환 캠페인만 필터
    conv_creatives = [c for c in creatives if "전환" in c.get("media", "") or "META(전환" in c.get("media", "")]
    
    total_revenue = sum(c.get("revenue", 0) for c in conv_creatives)
    total_spent = sum(c.get("spent", 0) for c in conv_creatives if c.get("spent", 0) > 0)
    total_actions = sum(c.get("actions", 0) for c in conv_creatives)
    total_imps = sum(c.get("impressions", 0) for c in creatives)
    total_clicks = sum(c.get("clicks", 0) for c in creatives)
    
    overall_roas = (total_revenue / total_spent * 100) if total_spent > 0 else 0
    overall_ctr = (total_clicks / total_imps * 100) if total_imps > 0 else 0
    overall_cvr = (total_actions / total_clicks * 100) if total_clicks > 0 else 0
    overall_cpa = (total_spent / total_actions) if total_actions > 0 else 0
    
    return {
        "budget": budget,
        "total_spent": total_spent,
        "budget_rate": (total_spent / budget * 100) if budget > 0 else 0,
        "total_impressions": total_imps,
        "total_clicks": total_clicks,
        "total_actions": total_actions,
        "total_revenue": total_revenue,
        "overall_roas": overall_roas,
        "overall_ctr": overall_ctr,
        "overall_cvr": overall_cvr,
        "overall_cpa": overall_cpa,
        "creative_count": len(creatives),
        "conv_creative_count": len(conv_creatives),
    }


# ── ROAS 랭킹 ─────────────────────────────────────────
def rank_by_roas(creatives: List[Dict]) -> List[Dict]:
    """ROAS 기준 소재 랭킹 (전환 소재만)"""
    conv = [c for c in creatives if c.get("roas", 0) > 0]
    return sorted(conv, key=lambda x: x.get("roas", 0), reverse=True)


def rank_by_ctr(creatives: List[Dict]) -> List[Dict]:
    """CTR 기준 소재 랭킹"""
    valid = [c for c in creatives if c.get("ctr", 0) > 0]
    return sorted(valid, key=lambda x: x.get("ctr", 0), reverse=True)


# ── 효율 저조 진단 ─────────────────────────────────────
def diagnose_low_performers(creatives: List[Dict]) -> List[Dict]:
    """효율 저조 소재 진단 + 원인 분석"""
    conv = [c for c in creatives if c.get("roas") is not None and c.get("spent", 0) > 0 and "전환" in c.get("media", "")]
    
    if not conv:
        return []
    
    avg_roas = sum(c["roas"] for c in conv) / len(conv) if conv else 0
    avg_ctr = sum(c.get("ctr", 0) for c in conv) / len(conv) if conv else 0
    avg_cvr = sum(c.get("cvr", 0) for c in conv) / len(conv) if conv else 0
    
    low_performers = []
    for c in conv:
        if c["roas"] < avg_roas * 0.7:  # 평균 ROAS의 70% 미만
            diagnosis = []
            
            if c.get("ctr", 0) < avg_ctr * 0.7:
                diagnosis.append("CTR 저조 → 소재 주목도 부족 (Hook/비주얼 개선 필요)")
            
            if c.get("cvr", 0) < avg_cvr * 0.7:
                diagnosis.append("CVR 저조 → 클릭 후 전환 실패 (랜딩/혜택 소구 개선 필요)")
            
            if c.get("cpc", 0) > 0:
                avg_cpc = sum(c2.get("cpc", 0) for c2 in conv) / len(conv)
                if c["cpc"] > avg_cpc * 1.3:
                    diagnosis.append(f"CPC 과다 (₩{c['cpc']:,.0f} vs 평균 ₩{avg_cpc:,.0f}) → 타겟 경쟁 심화")
            
            if c.get("impressions", 0) < 100000:
                diagnosis.append("노출 소규모 → 데이터 신뢰도 제한 (추가 테스트 필요)")
            
            if not diagnosis:
                diagnosis.append("전반적 효율 저하 → A/B 테스트 통한 개선점 발굴 필요")
            
            c["diagnosis"] = diagnosis
            c["vs_avg_roas"] = ((c["roas"] - avg_roas) / avg_roas * 100) if avg_roas > 0 else 0
            low_performers.append(c)
    
    return sorted(low_performers, key=lambda x: x["roas"])


# ── 속성별 분석 ────────────────────────────────────────
def analyze_by_attribute(creatives: List[Dict], attribute: str) -> List[Dict]:
    """특정 속성 기준으로 소재 그룹화 + 평균 효율 계산"""
    groups = {}
    for c in creatives:
        key = c.get(attribute, "미분류")
        if key not in groups:
            groups[key] = []
        groups[key].append(c)
    
    results = []
    for key, items in groups.items():
        n = len(items)
        avg_roas = sum(c.get("roas", 0) for c in items) / n if n > 0 else 0
        avg_ctr = sum(c.get("ctr", 0) for c in items) / n if n > 0 else 0
        avg_cvr = sum(c.get("cvr", 0) for c in items) / n if n > 0 else 0
        avg_cpc = sum(c.get("cpc", 0) for c in items) / n if n > 0 else 0
        total_spent = sum(c.get("spent", 0) for c in items)
        total_imps = sum(c.get("impressions", 0) for c in items)
        
        results.append({
            "attribute": key,
            "count": n,
            "avg_roas": avg_roas,
            "avg_ctr": avg_ctr,
            "avg_cvr": avg_cvr,
            "avg_cpc": avg_cpc,
            "total_spent": total_spent,
            "total_impressions": total_imps,
            "note": f"n={n}" + (" ⚠️ 소규모 표본" if n < 3 else ""),
        })
    
    return sorted(results, key=lambda x: x["avg_roas"], reverse=True)


def analyze_by_product(creatives: List[Dict]) -> List[Dict]:
    """제품별 분석"""
    return analyze_by_attribute(creatives, "product")


def analyze_by_format(creatives: List[Dict]) -> List[Dict]:
    """소재 형식(이미지/영상/카탈로그)별 분석"""
    return analyze_by_attribute(creatives, "format")


def analyze_by_media(creatives: List[Dict]) -> List[Dict]:
    """매체별 분석"""
    return analyze_by_attribute(creatives, "media")


# ── CTR vs CVR 역상관 패턴 ────────────────────────────
def detect_ctr_cvr_pattern(creatives: List[Dict]) -> Dict:
    """CTR vs CVR 역상관 패턴 확인"""
    conv = [c for c in creatives 
            if c.get("ctr", 0) > 0 and c.get("cvr", 0) > 0 
            and "전환" in c.get("media", "")]
    
    if len(conv) < 3:
        return {"pattern": "데이터 부족", "details": "분석 가능 소재 3개 미만"}
    
    # CTR 상위 vs 하위 그룹의 CVR 비교
    sorted_by_ctr = sorted(conv, key=lambda x: x["ctr"], reverse=True)
    mid = len(sorted_by_ctr) // 2
    high_ctr = sorted_by_ctr[:mid]
    low_ctr = sorted_by_ctr[mid:]
    
    avg_cvr_high_ctr = sum(c["cvr"] for c in high_ctr) / len(high_ctr)
    avg_cvr_low_ctr = sum(c["cvr"] for c in low_ctr) / len(low_ctr)
    
    if avg_cvr_high_ctr < avg_cvr_low_ctr:
        pattern = "역상관 시그널"
        detail = (f"CTR 상위 그룹 평균 CVR: {avg_cvr_high_ctr:.2%} vs "
                  f"CTR 하위 그룹 평균 CVR: {avg_cvr_low_ctr:.2%} → "
                  "주목도 높은 소재가 전환으로 이어지지 않는 패턴. "
                  "클릭 유도형 Hook과 전환 유도형 소구 분리 전략 검토 필요.")
    else:
        pattern = "양의 상관"
        detail = (f"CTR 상위 그룹 평균 CVR: {avg_cvr_high_ctr:.2%} vs "
                  f"CTR 하위 그룹 평균 CVR: {avg_cvr_low_ctr:.2%} → "
                  "CTR 높은 소재가 CVR도 높은 긍정적 패턴.")
    
    return {
        "pattern": pattern,
        "details": detail,
        "data": [
            {"name": c["name"], "product": c["product"], "ctr": c["ctr"], "cvr": c["cvr"]}
            for c in conv
        ]
    }


# ── 인사이트 텍스트 생성 ──────────────────────────────
def generate_insights(creatives: List[Dict], meta: Dict) -> List[str]:
    """핵심 인사이트 자동 생성"""
    insights = []
    
    conv_creatives = [c for c in creatives if c.get("roas", 0) > 0 and "전환" in c.get("media", "")]
    
    if not conv_creatives:
        insights.append("전환 소재 데이터가 충분하지 않아 상세 인사이트 생성이 제한됩니다.")
        return insights
    
    # 1. 최고 ROAS 소재
    best = max(conv_creatives, key=lambda x: x["roas"])
    insights.append(
        f"🏆 최고 ROAS 소재: {best['product']} {best['name']} "
        f"(ROAS {best['roas']:.1%}, CVR {best['cvr']:.2%}, n=Action {best['actions']:,}건). "
        f"{'⚠️ 카탈로그 소재로 단일 소재와 직접 비교 시 주의 필요.' if '카탈로그' in best.get('format', '') else ''}"
    )
    
    # 2. 최저 ROAS 소재
    worst = min(conv_creatives, key=lambda x: x["roas"])
    insights.append(
        f"⚠️ 최저 ROAS 소재: {worst['product']} {worst['name']} "
        f"(ROAS {worst['roas']:.1%}, CPC ₩{worst.get('cpc', 0):,.0f}). "
        f"전체 평균 대비 효율 저조 — 소재 교체 또는 타겟 조정 검토 필요."
    )
    
    # 3. 형식별 비교
    format_analysis = analyze_by_format(conv_creatives)
    if len(format_analysis) >= 2:
        best_fmt = format_analysis[0]
        insights.append(
            f"📊 형식별: '{best_fmt['attribute']}' 형식이 평균 ROAS {best_fmt['avg_roas']:.1%}로 최고 효율 "
            f"(n={best_fmt['count']}). "
            f"{'소규모 표본에서 확인된 시그널로 추가 검증 필요.' if best_fmt['count'] < 3 else ''}"
        )
    
    # 4. 제품별 비교
    product_analysis = analyze_by_product(conv_creatives)
    if len(product_analysis) >= 2:
        best_prod = product_analysis[0]
        worst_prod = product_analysis[-1]
        insights.append(
            f"📦 제품별: '{best_prod['attribute']}' 평균 ROAS {best_prod['avg_roas']:.1%} vs "
            f"'{worst_prod['attribute']}' 평균 ROAS {worst_prod['avg_roas']:.1%}. "
            f"제품 간 효율 격차 확인 → 예산 재배분 시그널."
        )
    
    # 5. CVR 100% 초과 경고
    high_cvr = [c for c in conv_creatives if c.get("cvr", 0) > 1.0]
    if high_cvr:
        names = ", ".join(f"{c['product']} {c['name']}" for c in high_cvr[:3])
        insights.append(
            f"⚠️ CVR 100% 초과 소재 감지: {names}. "
            "뷰스루(View-through) 전환이 포함되었을 가능성 높음 — 실제 클릭 전환만으로 재산출 권장."
        )
    
    # 6. 예산 소진율
    budget = meta.get("budget", 0)
    if budget > 0:
        total_spent = sum(c.get("spent", 0) for c in creatives if c.get("spent", 0) > 0)
        rate = total_spent / budget * 100
        insights.append(
            f"💰 예산 소진율: {rate:.1f}% (₩{total_spent:,.0f} / ₩{budget:,.0f})"
        )
    
    return insights


# ── 제작 브리프 자동 생성 ────────────────────────────────
def generate_briefs(creatives: List[Dict]) -> List[Dict]:
    """분석 결과 기반 3종 제작 브리프 자동 생성"""
    conv = [c for c in creatives if c.get("roas", 0) > 0 and "전환" in c.get("media", "")]
    
    if not conv:
        return []
    
    briefs = []
    
    # Brief #1: 효율 극대화형 (최고 ROAS 패턴)
    best_roas = sorted(conv, key=lambda x: x["roas"], reverse=True)[:3]
    briefs.append(_build_brief(
        title="효율 극대화형",
        subtitle="최고 ROAS 패턴 재현",
        reference_creatives=best_roas,
        priority="ROAS 극대화",
        kpi_target=f"목표 ROAS {best_roas[0]['roas']:.0%} 이상",
    ))
    
    # Brief #2: 볼륨 확보형 (최다 Action 패턴)
    best_action = sorted(conv, key=lambda x: x.get("actions", 0), reverse=True)[:3]
    briefs.append(_build_brief(
        title="볼륨 확보형",
        subtitle="최다 전환 패턴 재현",
        reference_creatives=best_action,
        priority="전환 수 극대화",
        kpi_target=f"목표 CPA ₩{best_action[0].get('cpa', 0):,.0f} 이하",
    ))
    
    # Brief #3: 기능 소구형 (안정적 중효율)
    mid_roas = sorted(conv, key=lambda x: abs(x["roas"] - sum(c["roas"] for c in conv) / len(conv)))[:3]
    briefs.append(_build_brief(
        title="기능 소구형",
        subtitle="안정적 중효율 패턴",
        reference_creatives=mid_roas,
        priority="안정적 ROAS + 볼륨 균형",
        kpi_target="평균 ROAS 유지하며 노출 확대",
    ))
    
    return briefs


def _build_brief(title: str, subtitle: str, reference_creatives: List[Dict], 
                  priority: str, kpi_target: str) -> Dict:
    """개별 브리프 구조 생성"""
    # 참조 소재들의 공통 패턴 추출
    formats = [c.get("format", "") for c in reference_creatives]
    products = [c.get("product", "") for c in reference_creatives]
    
    most_common_format = max(set(formats), key=formats.count) if formats else "미정"
    
    avg_ctr = sum(c.get("ctr", 0) for c in reference_creatives) / len(reference_creatives)
    avg_cvr = sum(c.get("cvr", 0) for c in reference_creatives) / len(reference_creatives)
    avg_roas = sum(c.get("roas", 0) for c in reference_creatives) / len(reference_creatives)
    
    return {
        "title": f"Brief #{len(title)}: {title}",
        "subtitle": subtitle,
        "priority": priority,
        "kpi_target": kpi_target,
        "recommended_format": most_common_format,
        "reference_creatives": [
            f"{c['product']} {c['name']} (ROAS {c['roas']:.1%})"
            for c in reference_creatives
        ],
        "avg_metrics": {
            "ctr": avg_ctr,
            "cvr": avg_cvr,
            "roas": avg_roas,
        },
        "do": [
            f"소재 형식: {most_common_format} 기반 제작",
            f"CTR 목표: {avg_ctr:.2%} 이상 유지",
            "상위 소재의 Hook/비주얼 패턴 참고",
            "제품 베네핏 명확한 카피 작성",
        ],
        "dont": [
            "노출 5만 미만 소재의 패턴을 일반화하지 말 것",
            "CTR만 높고 CVR 낮은 자극적 훅 지양",
            "카탈로그 소재와 단일 소재 효율 직접 비교 주의",
        ]
    }
