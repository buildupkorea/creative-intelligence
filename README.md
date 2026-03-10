# 🎨 GOLDNEX Creative Intelligence

SM본부 소재 인사이트 대시보드 — 엑셀 업로드 → 자동 분석 → 제작 브리프 생성

## 빠른 시작

```bash
# 1. 설치
pip install -r requirements.txt

# 2. 실행
streamlit run app.py

# 3. 브라우저에서 열림 → 엑셀 파일 업로드
```

## 기능

| 탭 | 기능 | 활용 |
|---|---|---|
| 📊 성과 총괄 | KPI + ROAS 랭킹 + 효율 저조 진단 | 캠페인 건강도 파악 |
| 🎨 소재 갤러리 | 이미지 + 속성 태그 + 레이아웃 리뷰 | 소재별 시각적 비교 |
| 🔬 속성 분석 | 비주얼/Hook/레이아웃별 성과 | 어떤 요소가 전환에 기여하는지 |
| ✍️ 무드·카피 | 6가지 무드 + 카피 텍스트 분석 | 카피 제작 방향 도출 |
| 📋 제작 브리프 | 3종 소재 브리프 자동 생성 | 디자이너에게 바로 전달 |
| 📈 매체·트렌드 | 매체별 비교 + 일별 추이 | 매체 예산 배분 |

## 지원 파일 형식

- 올영세일 캠페인 리포트 (`.xlsx`)
- 필수 시트: `Creative`, `Summary`
- 선택 시트: `Daily`, `META(전환)`, `META(장바구니)` 등

## 확장 로드맵

- **Phase 1** (현재): 엑셀 → 자동 분석 → 대시보드
- **Phase 2**: 분석 → 제작 브리프 자동 생성
- **Phase 3**: 브리프 → AI 소재 시안 생성 (Claude API 연동)

## 기술 스택

- **Frontend**: Streamlit + Plotly
- **Backend**: Python (pandas, openpyxl)
- **배포**: Streamlit Cloud / 사내 서버

---
GOLDNEX SM본부 · Creative Intelligence v1.0
