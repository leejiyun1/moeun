# Review Taste Learning Design

## 문서 목적

이 문서는 리뷰 작성 흐름에 `태그 선택`을 넣고, 사용자의 평점/후기/태그를 기반으로 입맛 프로필을 학습하는 구조를 정의한다.

핵심은 아래다.

- 사용자는 복잡한 맛 점수를 직접 입력하지 않는다.
- 사용자는 평점, 후기, 좋았던 점/아쉬웠던 점 태그를 남긴다.
- 시스템은 태그와 후기를 분석해 어떤 맛을 좋게 느꼈는지 또는 부담스럽게 느꼈는지 판단한다.
- 입맛 프로필은 확실한 신호만 조금씩 반영한다.

## 기존 방식의 문제

현재 리뷰 구조는 사용자가 `sweetness`, `acidity`, `body`, `carbonation`, `bitterness`, `aroma` 같은 맛 점수를 직접 남길 수 있다.

문제는 이 점수가 무엇을 의미하는지 애매하다는 점이다.

예:

```text
단맛이 4점인 술에 사용자가 단맛 4점을 남김
```

이 값은 아래 둘 중 무엇인지 구분하기 어렵다.

- 이 술이 달게 느껴졌다.
- 나는 단맛을 좋아한다.

따라서 직접 맛 점수만으로 입맛 프로필을 바꾸면 `사용자가 느낀 맛`과 `사용자의 선호도`가 섞일 수 있다.

## 목표 방식

리뷰 입력을 단순화한다.

사용자 입력:

- 평점
- 후기 텍스트
- 좋았던 점 태그
- 아쉬웠던 점 태그

시스템 처리:

- 태그와 후기에서 맛 신호를 추출한다.
- 평점과 맛 신호가 같은 방향인지 확인한다.
- 신뢰도가 충분할 때만 입맛 프로필을 조금씩 반영한다.

현재 코드 기준:

- 백엔드 원본 모델명은 `Feedback`이다.
- 프론트 사용자 화면에서는 `리뷰/후기`라고 부른다.
- 현재 `Feedback`에는 직접 맛 점수 필드와 `selected_tags` JSONField가 이미 있다.
- 현재 프론트에는 별점, 맛 점수 슬라이더, 신뢰도 슬라이더, 단순 맛 태그가 있다.
- 목표 구조에서는 직접 맛 점수/신뢰도 입력을 사용자 흐름에서 제거하고, 긍정 태그와 부정 태그를 분리한다.

예:

```text
평점 5
후기: 달달하고 향이 좋아서 마시기 편했어요.
좋았던 점: 달달함, 향

결과:
단맛 선호도 소폭 증가
향 선호도 소폭 증가
```

```text
평점 2
후기: 제 입에는 너무 달아서 부담스러웠어요.
아쉬웠던 점: 너무 달다

결과:
단맛 선호도 소폭 감소
```

## 핵심 개념

### 1. Feedback

사용자가 직접 남기는 원본 후기다.

책임:

- 평점 저장
- 후기 텍스트 저장
- 이미지 저장
- 주문 상품과 사용자 연결

하지 않을 일:

- 입맛 프로필 직접 변경
- AI 분석 직접 실행
- 상품 통계 외 다른 도메인 상태 직접 변경

현재 제거해야 할 문제:

- `Feedback.save()`가 상품 리뷰 수 증가와 취향 프로필 업데이트를 직접 수행한다.
- `Feedback.delete()`가 이미지 삭제와 상품 리뷰 수 감소를 직접 수행한다.
- 이 부수효과는 `FeedbackCommandService`로 옮긴다.

### 2. FeedbackTag

사용자가 선택하는 태그다.

태그는 점수가 아니라 `사용자가 느낀 방향`을 표현한다.

태그는 두 그룹으로 나눈다.

- 좋았던 점
- 아쉬웠던 점

이렇게 나누는 이유는 단순히 `달달함` 태그만 있으면 긍정인지 부정인지 모호하기 때문이다.

예:

```text
좋았던 점: 달달함
→ 단맛을 좋게 느낀 신호

아쉬웠던 점: 너무 달다
→ 단맛을 부담스럽게 느낀 신호
```

### 3. FeedbackAnalysis

AI 또는 규칙 기반 분석 결과다.

책임:

- 후기 텍스트에서 맛 신호 추출
- 태그와 후기의 일치 여부 판단
- 분석 신뢰도 계산
- 입맛 프로필 반영 가능 여부 판단

주의:

- AI 분석 결과는 원본 데이터가 아니라 해석 데이터다.
- 분석 실패가 리뷰 저장 실패로 이어지면 안 된다.
- 분석 결과는 저장해두고 나중에 재분석 가능해야 한다.

### 4. TasteProfileUpdateLog

입맛 프로필에 실제로 반영된 기록이다.

책임:

- 어떤 리뷰가 어떤 맛 선호도에 영향을 줬는지 저장
- 얼마나 반영했는지 저장
- 왜 반영했는지 추적 가능하게 남김

이 기록이 필요한 이유:

- 나중에 학습 로직을 바꿔도 기존 반영 근거를 확인할 수 있다.
- 잘못 반영된 리뷰를 되돌리거나 재계산할 수 있다.

## 태그 설계

### 태그 그룹

태그는 같은 테이블 또는 같은 상수 안에서 `sentiment`로 구분한다.

```text
POSITIVE
좋았던 점

NEGATIVE
아쉬웠던 점
```

### 태그와 맛 축 매핑

각 태그는 입맛 프로필의 맛 축과 연결된다.

```text
달달함 -> sweetness
상큼함 -> acidity
묵직함 -> body
톡 쏘는 느낌 -> carbonation
쌉쌀함 -> bitterness
향긋함 -> aroma
```

부정 태그도 같은 맛 축에 연결하되 방향만 반대로 본다.

```text
너무 달다 -> sweetness, negative
너무 시다 -> acidity, negative
너무 묵직하다 -> body, negative
탄산이 부담스럽다 -> carbonation, negative
너무 쓰다 -> bitterness, negative
향이 강하다 -> aroma, negative
```

### 1차 태그 후보

좋았던 점:

- 달달함
- 상큼함
- 묵직함
- 톡 쏘는 느낌
- 쌉쌀함
- 향긋함

아쉬웠던 점:

- 너무 달다
- 너무 시다
- 너무 묵직하다
- 탄산이 부담스럽다
- 너무 쓰다
- 향이 강하다

주의:

- 1차 태그는 6개 맛 축에 긍정/부정 1개씩 맞춰 12개로 시작한다.
- 추천 학습에 쓰지 못하는 감성 태그는 1차에서는 줄인다.
- 운영 중 자주 선택되는 태그를 보고 추가한다.

## 데이터 모델 초안

### Feedback

현재 리뷰 원본 모델로 유지한다.

현재 필드:

- `rating`
- `comment`
- `image_url`
- `selected_tags`
- `sweetness`, `acidity`, `body`, `carbonation`, `bitterness`, `aroma`
- `confidence`
- `created_at`
- `updated_at`

1차 변경 방향:

- 사용자 입력 API에서는 직접 맛 점수와 신뢰도 입력을 받지 않는다.
- `selected_tags`는 임시로 유지하되 긍정/부정 그룹을 표현할 수 있게 계약을 정리한다.
- 장기적으로 `selected_tags` JSONField는 `FeedbackTagSelection`으로 분리한다.
- 직접 맛 점수 필드는 당장 삭제하지 않고 deprecated 처리한다. 기존 데이터와 화면 표시 호환 때문이다.

장기 방향:

- `selected_tags` JSONField는 `FeedbackTagSelection`으로 분리한다.
- 직접 맛 점수 필드는 제거하거나 deprecated 처리한다.

### FeedbackTag

관리 가능한 태그 사전이다.

예상 필드:

- `id`
- `label`
- `sentiment`
- `taste_axis`
- `is_active`
- `sort_order`

### FeedbackTagSelection

사용자가 리뷰에서 선택한 태그다.

예상 필드:

- `feedback`
- `tag`

### FeedbackAnalysis

AI 분석 결과다.

예상 필드:

- `feedback`
- `status`
- `analyzer`
- `raw_input`
- `raw_output`
- `confidence`
- `sentiment`
- `taste_signals`
- `summary`
- `analyzed_at`

`taste_signals` 예시:

```json
{
  "sweetness": {
    "direction": "positive",
    "confidence": 0.82,
    "source": ["tag", "text"]
  },
  "aroma": {
    "direction": "positive",
    "confidence": 0.76,
    "source": ["text"]
  }
}
```

### TasteProfileUpdateLog

입맛 프로필 반영 기록이다.

예상 필드:

- `user`
- `feedback`
- `analysis`
- `taste_axis`
- `direction`
- `delta`
- `reason`
- `created_at`

## 처리 흐름

### 1. 리뷰 저장

```text
사용자 리뷰 작성
→ Feedback 저장
→ 태그 선택 저장
→ 상품 review_count 증가
→ 분석 대기 상태 생성
```

리뷰 저장은 AI 분석과 분리한다.

이유:

- AI 분석이 실패해도 리뷰는 남아야 한다.
- 로컬 LLM 실행 시간이 길어져도 사용자 응답을 막지 않아야 한다.

### 2. 리뷰 분석

```text
FeedbackAnalysis 대기 항목 조회
→ 태그 기반 1차 신호 생성
→ 후기 텍스트 로컬 LLM 분석
→ 태그 신호와 텍스트 신호 비교
→ confidence 계산
→ FeedbackAnalysis 저장
```

분석은 처음에는 동기 처리도 가능하지만, 운영 기준에서는 비동기 작업으로 분리하는 게 맞다.

### 3. 입맛 프로필 반영

```text
분석 결과 confidence 확인
→ 평점과 방향 일치 여부 확인
→ TasteProfileUpdateLog 생성
→ PreferTasteProfile 점수 조정
```

반영하지 않는 경우:

- confidence가 낮다.
- 평점과 분석 방향이 크게 충돌한다.
- 후기 내용이 너무 짧거나 의미가 없다.
- 태그와 후기 내용이 서로 반대다.

## 점수 반영 기준

1차에서는 크게 움직이지 않는다.

권장 기준:

```text
평점 4~5 + positive 신호
→ 해당 맛 선호도 소폭 증가

평점 1~2 + negative 신호
→ 해당 맛 선호도 소폭 감소

평점 3
→ 기본적으로 반영하지 않거나 매우 약하게 반영
```

반영 강도:

```text
delta = base_delta * confidence * rating_weight
```

예:

```text
base_delta = 0.1
confidence = 0.8
rating_weight = 1.0
최종 delta = 0.08
```

최대 변화량:

- 리뷰 1개당 한 맛 축 최대 `0.1`
- 한 리뷰 전체 최대 변화량 `0.2`
- 프로필 점수는 `0.0 ~ 5.0` 범위 유지

## 서비스 구조

### FeedbackCommandService

책임:

- 리뷰 생성
- 리뷰 수정
- 리뷰 삭제
- 이미지 처리 위임
- 상품 리뷰 수 갱신
- 분석 대기 항목 생성

### FeedbackQueryService

책임:

- 후기 목록 조회
- 내 후기 조회
- 인기 후기 조회
- 개인화 후기 후보 조회

### FeedbackAnalysisService

책임:

- 태그 기반 신호 생성
- 로컬 LLM 호출
- 분석 결과 저장
- 실패 처리

### TasteProfileLearningService

책임:

- 분석 결과를 입맛 프로필에 반영할지 판단
- 반영 delta 계산
- `PreferTasteProfile` 업데이트
- `TasteProfileUpdateLog` 저장

### LocalReviewAnalyzer

책임:

- 로컬 LLM 실행
- 고정 JSON 스키마로 응답 받기
- 응답 파싱 실패 처리

## API 응답 방향

리뷰 작성 요청:

```json
{
  "order_item": 1,
  "rating": 5,
  "comment": "달달하고 향이 좋아서 마시기 편했어요.",
  "positive_tag_ids": [1, 5],
  "negative_tag_ids": []
}
```

현재 프론트/백엔드 계약은 `selected_tags` 기반이다. 위 요청 형태는 목표 계약이며, 구현 시 기존 `selected_tags`와의 호환 기간을 둔다.

리뷰 작성 응답:

```json
{
  "id": 10,
  "rating": 5,
  "comment": "달달하고 향이 좋아서 마시기 편했어요.",
  "analysis_status": "PENDING"
}
```

주의:

- 리뷰 작성 응답에서 분석 결과를 바로 보장하지 않는다.
- 분석 결과는 나중에 별도 조회하거나 내부 학습에만 사용한다.

## 프론트 화면 방향

리뷰 작성 UI:

```text
별점
후기
좋았던 점 태그
아쉬웠던 점 태그
이미지
```

사용자에게 보여줄 문구:

```text
좋았던 점을 선택해주세요
아쉬웠던 점이 있다면 선택해주세요
```

피해야 할 문구:

```text
단맛 점수를 입력해주세요
산미 점수를 입력해주세요
입맛 프로필에 반영할 값을 입력해주세요
```

이유:

- 사용자가 맛을 객관적으로 평가해야 한다고 느끼면 부담이 커진다.
- 서비스는 사용자의 평가 부담을 줄이고, 시스템이 뒤에서 해석하는 방향이 맞다.

## 구현 단계

### 1단계

- 설계 문서 확정
- 기존 직접 맛 점수 입력 UI 제거 또는 숨김
- 평점, 후기, 좋았던 점/아쉬웠던 점 태그 UI 추가
- 태그는 상수 기반으로 시작

### 2단계

- `FeedbackCommandService` 추가
- `Feedback.save()` side effect 제거
- 리뷰 저장과 분석 대기 생성 분리

### 3단계

- `FeedbackAnalysis` 모델 추가
- 태그 기반 규칙 분석 먼저 구현
- 로컬 LLM 분석은 나중에 붙일 수 있게 인터페이스만 분리

### 4단계

- 로컬 LLM 분석 연결
- JSON schema 검증
- 실패/재시도 처리

### 5단계

- `TasteProfileLearningService` 추가
- confidence 높은 분석만 프로필에 소폭 반영
- 추천 결과 변화 검증

## 운영 리스크

### AI 분석 오류

대응:

- confidence 낮으면 반영하지 않는다.
- raw output을 저장해 재분석 가능하게 한다.
- 태그와 텍스트가 충돌하면 반영하지 않는다.

### 사용자가 태그를 대충 누름

대응:

- 태그만으로 강하게 반영하지 않는다.
- 평점, 태그, 후기 방향이 맞을 때만 반영한다.

### 리뷰 수가 적음

대응:

- 초기에는 취향 테스트 기반 프로필 영향력을 유지한다.
- 리뷰 1개당 변화량을 작게 제한한다.

### 제품 맛 프로필 자체가 부정확함

대응:

- 리뷰 학습만으로 모든 추천을 바꾸지 않는다.
- 상품의 기본 맛 프로필 품질도 관리자 데이터로 관리한다.

## 결론

1차 목표는 완벽한 추천이 아니다.

1차 목표는 아래다.

- 사용자가 쉽게 리뷰를 남긴다.
- 리뷰 데이터가 입맛 학습에 쓸 수 있는 형태로 쌓인다.
- 분석 실패가 서비스 흐름을 깨지 않는다.
- 입맛 프로필은 확실한 신호만 천천히 반영한다.

따라서 구조는 아래 방향으로 간다.

```text
Feedback
원본 리뷰

FeedbackTag / FeedbackTagSelection
사용자가 선택한 좋았던 점/아쉬웠던 점

FeedbackAnalysis
태그와 후기 텍스트 분석 결과

TasteProfileUpdateLog
입맛 프로필 반영 기록

TasteProfileLearningService
분석 결과를 실제 프로필 변화로 적용
```
