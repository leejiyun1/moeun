# Recommendation System Design

## 문서 목적

이 문서는 상품 추천 구조의 현재 구현과 다음 고도화 기준을 정리한다.

추천은 단순히 상품을 랜덤으로 보여주는 기능이 아니라, 사용자의 취향 테스트와 향후 리뷰 신호를 기반으로 상품을 정렬하고 설명하는 기능이다.

## 현재 구현

현재 추천 API:

```text
GET /api/v1/products/recommended/
```

현재 서비스:

```text
ProductRecommendationService
```

현재 동작:

- 로그인 사용자는 `PreferTasteProfile`을 읽어 취향 유사도 기반으로 상품을 추천한다.
- 비로그인 사용자 또는 취향 프로필이 없는 사용자는 fallback 기준으로 추천한다.
- 추천 대상은 `Product` 기준이다.
- 단일 상품과 고정 패키지 상품 모두 추천 대상에 포함될 수 있다.
- 응답에는 필요 시 `recommendation_score`, `recommendation_reason`을 포함한다.

현재 프론트 타입은 추천 점수와 추천 이유를 받을 수 있다. 다만 화면에서 추천 이유를 적극적으로 보여주는 UX는 아직 1차 반영 전이다.

## 입력 데이터

현재 사용하는 입력:

- 상품의 맛 프로필
- 사용자의 취향 프로필
- 상품 통계 기반 fallback 정보

향후 추가할 입력:

- 리뷰 평점
- 리뷰의 맛별 입맛 적합도
- 후기 텍스트 분석 결과
- 좋아요
- 조회/클릭
- 주문 이력

## 현재 한계

`ProductRecommendationService`가 아직 아래 책임을 함께 가진다.

- 후보 상품 조회
- 점수 계산
- 추천 이유 생성
- fallback 처리

1차 구현으로는 괜찮지만, 리뷰 기반 학습과 검색 결과 개인화까지 연결하려면 분리하는 편이 좋다.

## 목표 구조

장기적으로 추천 구조는 아래처럼 나눈다.

```text
ProductRecommendationService
├── RecommendationCandidateSelector
├── RecommendationScorer
└── RecommendationReasonBuilder
```

### ProductRecommendationService

추천 유스케이스를 조합하는 orchestrator다.

책임:

- 사용자 상태 확인
- 후보 selector 호출
- scorer 호출
- reason builder 호출
- 최종 응답용 product list 반환

하지 않을 일:

- 직접 긴 queryset 조립
- 점수 계산 세부 공식 보유
- 문구 생성 규칙 직접 보유

### RecommendationCandidateSelector

추천 후보 상품을 조회한다.

책임:

- 활성 상품만 조회
- 단일 상품/패키지 상품 포함 기준 적용
- `select_related`, `prefetch_related` 관리
- fallback 후보 조회

### RecommendationScorer

추천 점수를 계산한다.

책임:

- 취향 프로필과 상품 맛 프로필의 유사도 계산
- 리뷰의 입맛 적합도 기반 신호 반영
- 운영 가중치 반영
- fallback 점수 계산

초기 점수는 설명 가능한 규칙 기반으로 유지한다. AI나 모델 기반 추천은 데이터가 쌓인 뒤 검토한다.

### RecommendationReasonBuilder

추천 이유 문구를 만든다.

책임:

- 점수 근거를 사용자에게 이해 가능한 문장으로 변환
- 개인화 추천과 fallback 추천 문구 구분
- 과장된 표현 방지

예:

```text
취향 기반:
단맛과 향 선호도가 비슷해 추천했어요.

fallback:
최근 많이 찾는 상품 기준으로 추천했어요.
```

## 리뷰 기반 학습과의 연결

리뷰 기반 입맛 학습은 `docs/REVIEW_TASTE_LEARNING_DESIGN.md`를 따른다.

추천 서비스는 리뷰 원문을 직접 분석하지 않는다.

올바른 흐름:

```text
Feedback
-> FeedbackAnalysis
-> TasteProfileUpdateLog
-> PreferTasteProfile
-> ProductRecommendationService
```

추천 서비스는 최종적으로 정리된 취향 프로필과 신뢰 가능한 신호만 읽는다.

## 프론트 UX 기준

프론트는 실제 추천 방식과 문구를 일치시켜야 한다.

로그인 + 취향 프로필 있음:

- “취향 기반 추천”
- 추천 이유 표시 가능

비로그인 또는 취향 프로필 없음:

- “인기와 운영 기준 추천”
- 개인화처럼 보이는 문구 금지

추천 이유는 카드에 바로 노출할지, 상세 진입 후 보여줄지 아직 결정 전이다.

## 운영 기준

추천은 아래 기준을 지킨다.

- 추천 실패가 상품 목록 실패로 이어지면 안 된다.
- 개인화 데이터가 부족하면 fallback으로 자연스럽게 전환한다.
- 점수 계산 공식은 서비스 내부에 숨기되, 문서로 설명 가능해야 한다.
- 추천 문구는 실제 계산 근거와 맞아야 한다.
- 불필요한 쿼리와 중복 계산을 늘리지 않는다.

## 다음 작업

1. 프론트 추천 UX 문구 반영
2. 추천 reason 노출 위치 결정
3. `RecommendationCandidateSelector` 분리
4. `RecommendationScorer` 분리
5. `RecommendationReasonBuilder` 분리
6. 리뷰 태그/분석 구조 반영 후 scorer 입력 확장
