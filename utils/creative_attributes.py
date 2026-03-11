"""
creative_attributes.py — 소재 속성 분류 체계 (8개 기준축)
이 기준축은 고정이며, 매번 동일하게 적용됩니다.
"""

# ── 1. 비주얼 유형 ────────────────────────────────────
VISUAL_TYPES = {
    "모델컷": "모델 인물이 화면 30%+ 차지",
    "제품컷": "제품 단독 또는 소품과 함께",
    "텍스처컷": "거품/오일/크림 텍스처 클로즈업이 화면 주도",
    "GWP컷": "경품/소품이 화면 중앙 차지",
    "카탈로그": "META 자동 최적화 소재",
}

# ── 2. 소재 무드 (6가지 확장) ──────────────────────────
MOOD_TYPES = {
    "기능설명형": '"블랙헤드 순삭 비결", "딥클렌징" 등 구체적 기능',
    "가격혜택형": '"최대특가 38% OFF" 등 가격 자체가 핵심',
    "사이즈업형": '"대용량 더블기획", "폼크게" 등 양/크기',
    "순위권위형": '"1등 클렌징폼", "No.1" 등 순위·배지',
    "희소성형": '"단 7일만!", "한정수량" 등 시간 압박',
    "감성라이프형": "분위기, 라이프스타일 연출",
}

# ── 3. Hook 유형 ───────────────────────────────────────
HOOK_TYPES = [
    "사이즈업",
    "1등",
    "할인율",
    "GWP",
    "기능혜택",
    "희소성",
    "사이즈업+GWP",
    "기능+할인",
]

# ── 4. 인물 유무 ───────────────────────────────────────
PERSON_TYPES = ["모델", "없음"]

# ── 5. 배경 스타일 ─────────────────────────────────────
BACKGROUND_TYPES = [
    "하늘/물방울",
    "클린화이트",
    "제품클로즈업",
    "패턴소품",
]

# ── 6. 올영배지 유무 ───────────────────────────────────
BADGE_TYPES = ["O", "X"]

# ── 7. 가격 표기 ───────────────────────────────────────
PRICE_TYPES = [
    "할인율+가격",
    "가격만",
    "미표기",
]

# ── 8. 레이아웃 패턴 ──────────────────────────────────
LAYOUT_TYPES = {
    "A: 모델+제품열": "상단 카피+배지, 중단 모델+제품, 하단 가격",
    "B: 제품중앙+기능카피": "상단 기능카피, 중단 제품, 하단 가격+할인",
    "C: 텍스처풀샷": "상단 카피+배지, 중단 텍스처가득, 하단 제품+가격",
    "D: GWP소품구성": "상단 카피+배지, 중단 소품, 하단 가격+제품",
}

# ── 전체 속성 스키마 (태깅 UI용) ───────────────────────
ATTRIBUTE_SCHEMA = {
    "visual_type": {
        "label": "비주얼 유형",
        "options": list(VISUAL_TYPES.keys()),
        "descriptions": VISUAL_TYPES,
    },
    "mood": {
        "label": "소재 무드",
        "options": list(MOOD_TYPES.keys()),
        "descriptions": MOOD_TYPES,
    },
    "hook": {
        "label": "Hook 유형",
        "options": HOOK_TYPES,
    },
    "person": {
        "label": "인물 유무",
        "options": PERSON_TYPES,
    },
    "background": {
        "label": "배경 스타일",
        "options": BACKGROUND_TYPES,
    },
    "badge": {
        "label": "올영배지",
        "options": BADGE_TYPES,
    },
    "price_display": {
        "label": "가격 표기",
        "options": PRICE_TYPES,
    },
    "layout": {
        "label": "레이아웃",
        "options": list(LAYOUT_TYPES.keys()),
        "descriptions": LAYOUT_TYPES,
    },
}


def get_default_tags() -> dict:
    """기본 태그값 반환 (미분류 상태)"""
    return {
        "visual_type": "",
        "mood": "",
        "hook": "",
        "person": "",
        "background": "",
        "badge": "",
        "price_display": "",
        "layout": "",
    }
