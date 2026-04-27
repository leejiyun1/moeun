# EasyBE Backend Architecture v1

## 지금 읽을 부분

- `추천 구조`: 이 문서의 핵심 결론
- `도메인 경계`: 앱별 책임
- `레이어 규칙`: view / serializer / service / model 기준
- `우선 리팩터링 대상`: 어디부터 손댈지

제품 모델 초안은 `docs/PRODUCT_DOMAIN_MODEL.md` 를 함께 본다.

## 결론

이 백엔드는 `Django app 분리`는 유지하되, 각 앱 내부를 `thin view + serializer + service + selector` 구조로 정리하는 방향이 가장 맞다.

이 방향을 추천하는 이유는 세 가지다.

- Django 정석을 크게 벗어나지 않는다.
- 지금 코드에서 점진적으로 옮기기 쉽다.
- view를 컨트롤러 역할로 얇게 만들기 좋다.

## 왜 이 구조인가

현재 백엔드는 앱 분리는 이미 되어 있다.

- `users`
- `products`
- `taste_test`
- `feedback`
- `cart`
- `orders`
- `stores`

문제는 앱 경계보다 계층 경계가 완전히 정리되지 않았다는 점이다.

- 일부 view가 권한, 검증, 도메인 로직, 에러 응답까지 함께 처리한다.
- 일부 serializer가 파일 업로드 같은 인프라 로직까지 안고 있다.
- 일부 model은 다른 aggregate의 상태까지 같이 변경한다.

즉, 지금 필요한 건 앱을 다시 쪼개는 일이 아니라 `역할 분리`다.

## 선택지 비교

### 옵션 A. 현재 구조 유지 + 파일만 조금 정리

장점:

- 가장 빠르다.
- 기존 코드 수정량이 적다.

단점:

- view/serializer/model에 로직이 계속 새어 나온다.
- 레거시 느낌이 누적된다.
- 운영 이슈가 생길 때 추적이 어렵다.

언제 맞는가:

- 단기 과제성 프로젝트
- 유지보수 기간이 짧은 경우

### 옵션 B. 완전한 Clean Architecture / Repository 패턴

장점:

- 계층이 매우 엄격하다.
- 테스트 분리가 쉽다.

단점:

- Django에서는 과한 추상화가 되기 쉽다.
- 파일 수와 보일러플레이트가 많이 늘어난다.
- 지금 코드베이스에 바로 얹기엔 무겁다.

언제 맞는가:

- 대규모 조직
- 팀 내 아키텍처 규율이 이미 높은 경우

### 옵션 C. 앱 유지 + Thin View + Service + Selector

장점:

- Django 관용구와 잘 맞는다.
- 점진적 리팩터링이 가능하다.
- 책임 분리가 명확해진다.
- 쿼리 최적화와 비즈니스 로직 위치를 통제하기 쉽다.

단점:

- 규칙을 안 지키면 다시 view와 serializer가 두꺼워진다.
- selector/service 분리를 팀이 계속 의식해야 한다.

언제 맞는가:

- 지금 이 프로젝트
- 완성도와 확장성을 동시에 챙기고 싶은 경우

## 추천 구조

추천은 `옵션 C`다.

한 줄로 정리하면 이렇다.

- `View`: 요청을 받는다
- `Serializer`: 입력을 검증하고 출력 형식을 만든다
- `Service`: 비즈니스 규칙을 실행한다
- `Selector`: 읽기 쿼리를 조립한다
- `Model`: 자기 자신의 상태와 불변식만 책임진다

## 레이어 규칙

### 1. View

View는 최대한 컨트롤러 역할만 담당한다.

해야 할 일:

- 인증/권한 확인
- request serializer 호출
- service 또는 selector 호출
- response serializer 또는 응답 반환
- 도메인 예외를 HTTP 응답으로 변환

하지 말아야 할 일:

- 긴 쿼리 작성
- 비즈니스 계산
- 외부 스토리지 호출
- 여러 모델 상태를 직접 갱신
- broad `except Exception` 으로 로직을 덮기
- CORS 같은 인프라 헤더를 직접 관리하기

### 2. Serializer

Serializer는 검증과 변환에 집중한다.

해야 할 일:

- 필드 유효성 검사
- 요청 데이터 정규화
- 응답 필드 구성

하지 말아야 할 일:

- 외부 파일 업로드
- 다른 aggregate 수정
- 긴 분기 로직
- 숨겨진 부수효과

### 3. Service

Service는 write 중심의 비즈니스 유스케이스를 담당한다.

예:

- 장바구니에서 주문 생성
- 피드백 작성/수정/삭제
- 취향 프로필 갱신
- 좋아요 토글
- 회원 탈퇴/복구

규칙:

- transaction 경계는 service에 둔다.
- 다른 모델을 함께 갱신하는 로직은 service에 둔다.
- 실패 가능한 비즈니스 규칙은 명시적 예외로 표현한다.

### 4. Selector

Selector는 read 전용 쿼리를 담당한다.

예:

- 제품 검색 쿼리
- 메인 섹션 목록 조회
- 후기 목록/상세 조회
- 마이페이지용 주문/리뷰 조회

규칙:

- `select_related`, `prefetch_related`, `annotate`, `order_by`는 selector에서 관리한다.
- pagination 전의 queryset 조립은 selector에서 끝낸다.
- view에서 직접 queryset을 길게 만들지 않는다.

### 5. Model

Model은 자기 자신의 상태와 불변식만 책임진다.

허용:

- `clean`
- 자기 자신의 값 계산
- 자기 자신의 상태 전환 메서드

지양:

- 다른 aggregate를 같이 수정하는 `save` / `delete` 오버라이드
- 외부 스토리지 삭제/업로드 호출
- 서비스 수준의 오케스트레이션

즉, `Feedback.save()` 가 `Product.review_count` 나 `TasteProfile` 까지 수정하는 구조는 장기적으로 service로 빼는 게 맞다.

## 권장 앱 내부 구조

앱마다 완전히 똑같을 필요는 없지만, 목표 형태는 아래와 같다.

```text
apps/<domain>/
├── models.py
├── urls.py
├── exceptions.py
├── permissions.py
├── selectors.py
├── services/
│   ├── __init__.py
│   ├── commands.py
│   ├── queries.py  # 필요 시
│   └── helpers.py
├── serializers/
│   ├── __init__.py
│   ├── request.py
│   └── response.py
├── views/
│   ├── __init__.py
│   ├── public.py
│   └── admin.py
└── tests/
```

모든 앱에 이 구조를 강제할 필요는 없다. 다만 아래 원칙은 유지한다.

- public/admin API는 가능하면 분리
- request/response serializer 분리 고려
- read/write 로직 분리

## 도메인 경계

### users

책임:

- 사용자 계정
- 소셜 로그인 연결
- 성인 인증 상태
- 회원 탈퇴/복구
- 진화형 취향 프로필

하지 않을 일:

- 테스트 질문/결과 계산 로직 직접 소유
- 후기 도메인 직접 소유

### taste_test

책임:

- 테스트 질문 제공
- 답변 채점
- 테스트 결과 계산 및 저장

하지 않을 일:

- 사용자 취향 프로필의 장기 학습 로직 직접 소유

### products

책임:

- 카탈로그
- 검색
- 섹션별 상품 조회
- 좋아요
- 상품 조회수/정적 통계
- 패키지 정책 관리
- 상품 write orchestration

하지 않을 일:

- 주문 생성
- 후기 생성

### feedback

책임:

- 후기 작성/수정/삭제
- 후기 이미지 메타데이터
- 후기 조회
- 후기 기반 taste signal 생성

하지 않을 일:

- 취향 프로필 직접 영속 업데이트
- 상품 통계 직접 갱신

이런 cross-domain 업데이트는 service 조합 계층에서 처리한다.

### cart

책임:

- 주문 전 임시 담기 상태
- 수량 조정
- 픽업 정보 임시 관리

### orders

책임:

- 주문 생성
- 주문 항목 보존
- 주문 상태 전이

원칙:

- 주문 생성 이후에는 당시 가격/상품 snapshot 성격을 유지한다.

### stores

책임:

- 픽업 매장 정보

### common / core

책임:

- 공통 middleware
- 외부 인프라 연동
- 공통 유틸

원칙:

- 도메인 규칙을 `common` 으로 올리지 않는다.

## 요청 흐름 표준

권장 흐름:

1. `View` 가 request serializer를 호출
2. serializer가 입력을 검증
3. `Service` 또는 `Selector` 호출
4. 필요 시 service 내부에서 transaction 실행
5. 응답 serializer로 포맷
6. view가 최종 HTTP 응답 반환

예시:

```text
HTTP Request
-> View
-> Request Serializer
-> Service / Selector
-> Domain Models
-> Response Serializer
-> HTTP Response
```

## 공통 설계 규칙

### API 정책

- 새 엔드포인트는 `/api/v1/` 기준으로 통일
- public/admin 경로와 view 모듈도 같이 분리
- 응답 형식은 도메인별로 크게 흔들리지 않게 유지

### 예외 처리

- `ValueError`, `PermissionError` 를 view에서 임의로 잡아 쓰기보다 도메인 예외를 정의
- DRF exception handler 또는 view 공통 베이스에서 HTTP 변환 규칙을 통일

### 트랜잭션

- 다중 모델 갱신은 service에서 `transaction.atomic`
- serializer나 model save에서 transaction 경계를 숨기지 않기

### 쿼리 최적화

- selector에서 relation loading 정책을 관리
- view마다 제각각 `select_related` 하지 않기
- count/update 패턴은 race condition 가능성까지 검토

### 외부 인프라

- S3/Object Storage
- OAuth provider
- Email

이런 요소는 service 또는 infra adapter를 통해 접근하고, serializer/model에 직접 박지 않는다.

## 현재 코드 기준 좋은 점

- 앱 분리는 이미 비교적 명확하다.
- `products` 는 public/admin/sections 분리가 시작돼 있다.
- `orders`, `cart` 는 service 사용이 비교적 잘 보인다.
- `taste_test` 는 serializer + service 흐름을 일부 갖추고 있다.

## 현재 코드 기준 우선 문제

### 1. feedback

문제:

- view에서 권한/중복 체크/에러 응답을 많이 처리
- serializer가 파일 업로드를 직접 수행
- model `save/delete` 가 다른 aggregate 상태를 수정

왜 문제인가:

- 책임이 view, serializer, model에 동시에 흩어진다.
- 운영 이슈가 나면 추적이 어렵다.
- 테스트 경계가 애매하다.

추천:

- `FeedbackCommandService`
- `FeedbackSelector`
- `FeedbackImageService`
- `FeedbackDomainException`

형태로 분리

### 2. taste_test

문제:

- view가 CORS 헤더까지 직접 처리
- controller_support service가 있지만 경계가 아직 애매함

왜 문제인가:

- HTTP 인프라와 도메인 로직이 섞인다.

추천:

- CORS는 middleware/settings로 이동
- 테스트 계산과 저장 orchestration을 service로 더 명확히 구분

### 3. users taste profile

문제:

- profile 조회 API가 생성, 분석 필요 여부 판단, 분석 실행, 응답까지 모두 수행
- broad exception 사용

추천:

- `TasteProfileService.get_or_build_profile(user)`
- `TasteProfileAnalysisService.refresh_if_needed(profile)`

형태로 분리

### 4. model side effects

문제:

- `Feedback.save/delete`
- 일부 model method에서 cross-domain 변경 수행

추천:

- model은 자기 상태만
- cross-domain write는 service orchestration으로 이동

## 구현 우선순위

### P0

- API version 정책 통일
- 도메인 예외 체계 도입
- view에서 broad exception 제거
- CORS/infra 로직을 view에서 제거

### P1

- `feedback` 레이어 정리
- `taste_profile` 조회/분석 흐름 분리
- selector 패턴 도입

### P2

- `products` read path를 selector 중심으로 통일
- `products` create/update/delete 를 command service 중심으로 전환
- 통계 갱신 정책 재정의
- 이미지/외부 스토리지 adapter 분리

진행 상태:

- `products` 는 public/admin/section 조회를 selector 기준으로 정리했다.
- 관리자 상품 생성/수정/비활성화는 `ProductCommandService` 기준으로 전환했다.
- 관리자 패키지 정책 생성/수정/비활성화는 `PackagePolicyCommandService` 기준으로 추가했다.
- 현재 패키지 구성 수정은 `PackageItem.quantity` 기반 수량 교체까지 지원한다.
- product 기준 커스텀 패키지 draft는 `cart.PackageDraft` / `PackageDraftItem` 으로 분리했다.
- 주문 생성 시 커스텀 패키지는 `orders.OrderCustomPackage` snapshot 으로 고정한다.

## 설계 채택 기준

앞으로 백엔드 코드가 좋은 방향인지 판단할 때는 아래만 보면 된다.

- view가 얇은가
- serializer가 검증에 집중하는가
- service가 business use case를 소유하는가
- model이 자기 책임만 지는가
- 쿼리와 write 로직이 분리되어 있는가
- 하드코딩과 임시 분기가 줄어드는가
- 운영 시 추적과 테스트가 쉬워지는가

## 다음 작업 추천

전반 설계 다음에 실제 코드로 들어갈 첫 타겟은 `feedback` 이다.

이유:

- 현재 가장 많이 섞여 있다.
- 후기, 상품, 취향 프로필, 이미지 업로드까지 얽혀 있다.
- 여기 정리 방식이 다른 앱의 기준 템플릿이 될 수 있다.
