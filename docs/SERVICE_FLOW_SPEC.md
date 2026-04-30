# Service Flow Spec

## 문서 목적

이 문서는 Moeun 서비스의 실제 흐름을 코드 단위까지 연결해 설명한다.

목적은 세 가지다.

- 기능을 만들 때 어느 파일과 어느 계층을 수정해야 하는지 흔들리지 않게 한다.
- 불필요한 코드, 중복 호출, 임시 우회 로직을 검토할 기준을 만든다.
- 사용자 플로우, 관리자 플로우, 백엔드 모델 변화가 서로 어긋나지 않게 한다.

이 문서는 단순 기획서가 아니다. 앞으로 코드 리뷰 기준으로 사용한다.

## 읽는 방법

각 플로우는 아래 형식으로 정리한다.

- 목표: 이 흐름이 사용자나 운영자에게 제공하는 결과
- 진입점: 화면/URL/버튼
- FE 책임: page, component, hook, api, type 기준 책임
- API 계약: 호출 경로와 요청/응답 기준
- BE 책임: view, serializer, service, model 기준 책임
- 상태 변화: DB에 실제로 남는 변화
- 금지사항: 이 플로우에서 하면 안 되는 구현
- 검증 기준: 완료 판단 기준
- 정리 후보: 불필요하거나 흔들리는 코드 검토 지점

## 전체 플로우 맵

```text
방문자
-> 메인
-> 취향 테스트
-> 추천/검색/패키지 탐색
-> 상품 상세
-> 장바구니
-> 픽업 정보 입력
-> 주문 생성
-> 마이페이지 주문/후기

관리자
-> 관리자 로그인
-> 상품 등록
-> 패키지 정책 등록
-> 고정 패키지 상품 등록
-> 운영 데이터 확인
```

## 공통 원칙

### FE 원칙

- `pages`는 화면 조합을 담당한다.
- 서버 데이터 요청과 조합은 `hooks`에서 담당한다.
- HTTP 호출은 `api`에서 담당한다.
- API 경로는 `constants/apiPaths.ts`만 사용한다.
- 응답 타입은 `types`에 둔다.
- 같은 서버 상태를 zustand store와 React Query에 중복 저장하지 않는다.
- 화면에서 임시 API URL을 직접 만들지 않는다.

### BE 원칙

- `views`는 요청 진입점과 권한, 응답 변환만 담당한다.
- `serializers`는 입력 검증과 출력 변환에 집중한다.
- `services`는 비즈니스 유스케이스와 transaction을 담당한다.
- `selectors`는 조회 쿼리 조립을 담당한다.
- `models`는 자기 상태와 기본 제약만 담당한다.
- cross-domain 상태 변경은 model `save/delete`가 아니라 service에서 처리한다.

### API 원칙

- 신규 API는 `/api/v1/` 기준으로 둔다.
- 프론트 `VITE_API_URL`은 `/api/v1`까지 포함하는 것을 전제로 한다.
- 백엔드 URL과 프론트 `API_PATHS`는 같은 변경 단위에서 수정한다.
- 인증이 필요한 API는 FE guard만 믿지 않고 BE permission도 적용한다.

## Flow 1. 방문자가 메인을 본다

### 목표

사용자가 서비스에 들어왔을 때 대표 상품, 인기 상품, 추천 상품, 패키지 영역을 확인한다.

### 진입점

```text
GET /
```

FE 라우트:

```text
ExcellentFE/src/App.tsx
-> path="/"
-> ExcellentFE/src/pages/Index.tsx
```

### FE 책임

관련 파일:

- `ExcellentFE/src/pages/Index.tsx`
- `ExcellentFE/src/hooks/home/useMainProduct.ts`
- `ExcellentFE/src/hooks/home/useProduct.ts`
- `ExcellentFE/src/api/productApi.ts`
- `ExcellentFE/src/constants/apiPaths.ts`
- `ExcellentFE/src/types/home.ts`
- `ExcellentFE/src/types/product.ts`

책임:

- 메인 화면 섹션을 조합한다.
- 상품 데이터 요청은 hook으로 위임한다.
- API 경로는 `API_PATHS.PRODUCTS`를 사용한다.
- 추천 응답에 `recommendation_reason`이 있으면 표시 여부를 별도 UX 기준으로 결정한다.

### API 계약

현재 사용 가능 API:

```text
GET /api/v1/products/monthly/
GET /api/v1/products/popular/
GET /api/v1/products/recommended/
GET /api/v1/products/featured/
```

추천 API 기준:

- 로그인 사용자는 취향 프로필 기반 추천을 받을 수 있다.
- 취향 프로필이 없거나 비로그인이면 fallback 추천을 받는다.
- 추천 응답은 `recommendation_score`, `recommendation_reason`을 포함할 수 있다.

### BE 책임

관련 파일:

- `EasyBE/apps/products/views/product/sections.py`
- `EasyBE/apps/products/views/product/public.py`
- `EasyBE/apps/products/selectors.py`
- `EasyBE/apps/products/services/recommendation_service.py`
- `EasyBE/apps/products/services/search_service.py`
- `EasyBE/apps/products/serializers/product/list.py`

책임:

- view는 요청을 받고 selector/service 호출만 한다.
- 섹션별 상품 조회 쿼리는 selector에서 관리한다.
- 추천은 `ProductRecommendationService`에서 담당한다.
- 응답 직렬화는 product list serializer에서 담당한다.

### 상태 변화

메인 조회 자체는 상태를 변경하지 않는다.

단, 상세 조회에서는 `view_count` 증가 여부를 별도 정책으로 둔다.

### 금지사항

- 메인 페이지에서 상품 데이터를 하드코딩하지 않는다.
- 추천 실패를 화면 전체 실패로 만들지 않는다.
- 비로그인 fallback 추천을 개인화 추천처럼 표현하지 않는다.
- view에서 추천 점수 계산을 직접 하지 않는다.

### 검증 기준

- 메인 진입 시 필요한 상품 섹션이 표시된다.
- 추천 API 실패 시에도 다른 섹션이 가능하면 표시된다.
- 로그인/비로그인 추천 문구가 다르게 표현된다.

### 정리 후보

- 메인에서 여러 섹션 API를 동시에 호출할 때 중복 상품 조회가 과한지 확인한다.
- 추천 UX가 아직 API 응답의 `recommendation_reason`을 충분히 쓰지 못한다.

## Flow 2. 사용자가 취향 테스트를 한다

### 목표

사용자가 간단한 테스트를 통해 초기 입맛 프로필을 만든다.

### 진입점

```text
GET /test
```

FE 라우트:

```text
ExcellentFE/src/pages/tasteTest/index.tsx
-> ExcellentFE/src/components/taste-test/TestContainer.tsx
```

### FE 책임

관련 파일:

- `ExcellentFE/src/pages/tasteTest/index.tsx`
- `ExcellentFE/src/components/taste-test/*`
- `ExcellentFE/src/hooks/taste-test/useTasteTest.ts`
- `ExcellentFE/src/hooks/taste-test/nonMemberTest.ts`
- `ExcellentFE/src/api/taste-test/index.ts`
- `ExcellentFE/src/types/tasteTypes.ts`

책임:

- 테스트 질문을 보여준다.
- 사용자의 답변 상태를 관리한다.
- 제출 시 테스트 결과 API를 호출한다.
- 비회원 테스트 결과는 로그인 이후 연결 가능한지 별도 흐름을 유지한다.

### API 계약

```text
GET  /api/v1/taste_test/questions/
POST /api/v1/taste_test/submit/
POST /api/v1/taste_test/retake/
GET  /api/v1/user/taste_test/profile/
GET  /api/v1/taste_test/types/
```

현재 FE 상수:

```text
API_PATHS.TASTE_TEST.QUESTIONS
API_PATHS.TASTE_TEST.RESULT
API_PATHS.TASTE_TEST.RETAKE
API_PATHS.USER.TASTE_TEST_PROFILE
```

### BE 책임

관련 파일:

- `EasyBE/apps/taste_test/views/test_views.py`
- `EasyBE/apps/taste_test/views/profile_views.py`
- `EasyBE/apps/taste_test/services/calculator.py`
- `EasyBE/apps/taste_test/services/storage.py`
- `EasyBE/apps/taste_test/services/profile_handler.py`
- `EasyBE/apps/taste_test/serializers/request.py`
- `EasyBE/apps/taste_test/serializers/response.py`
- `EasyBE/apps/taste_test/models.py`
- `EasyBE/apps/users/models.py`

책임:

- 질문 제공
- 답변 검증
- 테스트 결과 계산
- 사용자 취향 프로필 초기화

### 상태 변화

로그인 사용자:

```text
PreferenceTestResult 생성 또는 갱신
PreferTasteProfile 생성 또는 갱신
```

비로그인 사용자:

```text
프론트 임시 상태 또는 별도 임시 흐름
```

### 금지사항

- 취향 테스트 view에서 CORS 같은 인프라 헤더를 직접 관리하지 않는다.
- 테스트 계산 공식을 프론트에 중복 구현하지 않는다.
- 추천 서비스가 테스트 view 내부 로직에 의존하지 않는다.

### 검증 기준

- 질문 목록이 정상 표시된다.
- 답변 제출 후 결과 타입이 표시된다.
- 로그인 사용자의 취향 프로필이 추천 API에서 재사용된다.

### 정리 후보

- `taste_test/services`의 하위 호환 코드가 남아 있다. 기존 import와 테스트 의존 제거 후 정리한다.
- 취향 프로필 조회/분석 책임은 `users` 쪽 service로 분리할 필요가 있다.

## Flow 3. 사용자가 상품을 검색한다

### 목표

사용자가 조건을 선택해 상품을 찾고, 검색 결과를 확인한다.

### 진입점

```text
GET /search
```

FE 라우트:

```text
ExcellentFE/src/pages/Search.tsx
```

### FE 책임

관련 파일:

- `ExcellentFE/src/pages/Search.tsx`
- `ExcellentFE/src/hooks/useProductSearch.ts`
- `ExcellentFE/src/hooks/useSearchFilters.ts`
- `ExcellentFE/src/api/searchApi.ts`
- `ExcellentFE/src/api/productApi.ts`
- `ExcellentFE/src/types/search.ts`

책임:

- 검색어와 필터 상태를 관리한다.
- 검색 API 호출은 hook/api로 위임한다.
- 검색 결과 카드에 상품 타입, 가격, 이미지, 찜 상태를 표시한다.

### API 계약

```text
GET /api/v1/products/search/
```

필터 기준은 백엔드 `ProductSearchService`가 소유한다.

### BE 책임

관련 파일:

- `EasyBE/apps/products/views/product/public.py`
- `EasyBE/apps/products/services/search_service.py`
- `EasyBE/apps/products/selectors.py`
- `EasyBE/apps/products/serializers/product/list.py`

책임:

- 검색 조건을 검증한다.
- 상품 조회 쿼리를 구성한다.
- 정렬과 필터를 일관되게 적용한다.

### 상태 변화

현재 검색은 상태를 변경하지 않는다.

향후 검색 로그를 남길 경우 별도 로그 모델 또는 이벤트 수집 구조로 분리한다.

### 금지사항

- 검색 필터 기준을 프론트와 백엔드에 서로 다르게 중복 구현하지 않는다.
- view에서 긴 queryset 조립을 하지 않는다.
- 검색 결과 개인화와 기본 검색을 구분 없이 섞지 않는다.

### 검증 기준

- 검색어/필터 조합이 API 요청에 반영된다.
- 빈 결과 상태가 표시된다.
- API 경로는 `API_PATHS.SEARCHPRODUCTS.SEARCH`만 사용한다.

### 정리 후보

- `SEARCHPRODUCTS` 상수명은 장기적으로 `SEARCH` 또는 `PRODUCT_SEARCH`로 정리하는 편이 낫다.
- 검색 로그 TODO는 실제 운영 지표 설계 이후 구현한다.

## Flow 4. 사용자가 상품 상세를 본다

### 목표

사용자가 단일 상품 또는 패키지 상품의 상세 정보와 후기 정보를 확인한다.

### 진입점

```text
GET /product/:id
GET /package/:id
```

FE 라우트:

```text
ExcellentFE/src/pages/Detail.tsx
```

### FE 책임

관련 파일:

- `ExcellentFE/src/pages/Detail.tsx`
- `ExcellentFE/src/components/detail/DetailProduct.tsx`
- `ExcellentFE/src/components/detail/DetailFeedback.tsx`
- `ExcellentFE/src/hooks/home/useDetailPage.ts`
- `ExcellentFE/src/api/productApi.ts`
- `ExcellentFE/src/types/product.ts`

책임:

- 상품 상세 정보를 표시한다.
- 상품 타입에 따라 구성 정보를 표시한다.
- 장바구니 추가 버튼을 제공한다.
- 픽업 매장/날짜 선택은 상세가 아니라 장바구니에서 한다.

### API 계약

```text
GET  /api/v1/products/{id}/
POST /api/v1/cart/
```

상세 API는 상품 정보만 제공한다. 주문에 필요한 픽업 정보는 장바구니 단계에서 입력한다.

### BE 책임

관련 파일:

- `EasyBE/apps/products/views/product/public.py`
- `EasyBE/apps/products/selectors.py`
- `EasyBE/apps/products/serializers/product/detail.py`
- `EasyBE/apps/cart/views.py`
- `EasyBE/apps/cart/serializers.py`

책임:

- 상품 상세 조회
- 상품 타입별 응답 조립
- 장바구니 추가 시 상품 유효성 검증

### 상태 변화

상세 조회:

```text
필요 시 Product.view_count 증가
```

장바구니 추가:

```text
CartItem 생성 또는 quantity 증가
```

### 금지사항

- 상세 페이지에서 픽업 매장/날짜를 하드코딩하지 않는다.
- 상세 페이지에서 가짜 후기 데이터를 넣지 않는다.
- 패키지 상품을 단일 상품처럼 억지로 변환하지 않는다.
- 장바구니 추가 API payload에 운영과 무관한 임시 날짜를 넣지 않는다.

### 검증 기준

- 단일 상품과 패키지 상품 상세가 모두 열린다.
- 장바구니 추가 시 pickup 정보 없이도 임시 담기가 가능하다.
- checkout 전에는 pickup 정보 누락이 차단된다.

### 정리 후보

- 상세 후기 영역은 실제 feedback API와 연결 기준을 다시 정해야 한다.
- 상세 페이지의 상품 타입별 UI 분기 기준을 `product_type` 중심으로 정리한다.

## Flow 5. 사용자가 장바구니에서 픽업 정보를 입력한다

### 목표

사용자가 담아둔 상품에 대해 픽업 매장과 날짜를 선택하고 주문 가능한 상태로 만든다.

### 진입점

```text
GET /cart
```

FE 라우트:

```text
ExcellentFE/src/pages/Cart.tsx
```

### FE 책임

관련 파일:

- `ExcellentFE/src/pages/Cart.tsx`
- `ExcellentFE/src/hooks/cart/useUserCart.ts`
- `ExcellentFE/src/hooks/cart/useCartItem.ts`
- `ExcellentFE/src/hooks/cart/useUserPostOrder.ts`
- `ExcellentFE/src/hooks/store/useStores.ts`
- `ExcellentFE/src/api/store.ts`
- `ExcellentFE/src/types/cart.ts`

책임:

- 장바구니 목록을 조회한다.
- 픽업 매장 목록을 조회한다.
- 각 장바구니 항목의 픽업 매장/날짜를 수정한다.
- 선택한 항목만 주문으로 넘긴다.
- 선택한 일반 상품에 픽업 정보가 없으면 주문 버튼을 막는다.

### API 계약

```text
GET    /api/v1/cart/
POST   /api/v1/cart/
PATCH  /api/v1/cart/{id}/
DELETE /api/v1/cart/{id}/
GET    /api/v1/stores/
POST   /api/v1/orders/create_from_cart/
```

주문 생성 payload:

```json
{
  "item_ids": [1, 2],
  "package_draft_ids": [10]
}
```

### BE 책임

관련 파일:

- `EasyBE/apps/cart/views.py`
- `EasyBE/apps/cart/serializers.py`
- `EasyBE/apps/cart/services.py`
- `EasyBE/apps/cart/models.py`
- `EasyBE/apps/stores/views.py`
- `EasyBE/apps/orders/views.py`
- `EasyBE/apps/orders/services.py`

책임:

- 장바구니 항목 조회
- 수량 수정
- 픽업 매장/날짜 수정
- 주문 생성 전 필수 정보 검증
- 선택 항목만 주문으로 변환

### 상태 변화

장바구니 수정:

```text
CartItem.pickup_store 변경
CartItem.pickup_date 변경
CartItem.quantity 변경
```

주문 생성:

```text
Order 생성
OrderItem 생성
선택된 CartItem 삭제 또는 주문 처리
```

### 금지사항

- 프론트에서 `pickup_store_id = 1` 같은 기본값을 하드코딩하지 않는다.
- 프론트에서 임시 날짜를 자동 주입하지 않는다.
- 백엔드에서 pickup 정보 누락을 프론트만 믿고 통과시키지 않는다.
- 선택하지 않은 장바구니 항목을 주문에 포함하지 않는다.

### 검증 기준

- 매장 목록이 API에서 로드된다.
- 장바구니 항목별 픽업 매장/날짜가 수정된다.
- 선택 항목에 픽업 정보가 없으면 주문이 막힌다.
- 선택한 항목만 주문으로 생성된다.

### 정리 후보

- 커스텀 패키지 draft는 아직 장바구니 UI에서 충분히 다루지 못한다.
- 픽업 가능 날짜 정책은 아직 상수/설정으로 중앙화되어 있지 않다.

## Flow 6. 사용자가 커스텀 패키지를 만든다

### 목표

사용자가 관리자 정책 안에서 여러 상품을 골라 자신만의 시음/패키지 구성을 만든다.

### 현재 상태

백엔드 모델과 주문 snapshot 기반은 있다.

현재 부족한 것:

- 프론트 커스텀 패키지 구성 UI
- 패키지 정책 선택 UI
- draft 생성/수정 API의 프론트 연결
- 장바구니에서 draft 표시와 pickup 정보 입력

### 목표 진입점

후보:

```text
GET /package/custom
GET /package-policies/:id/build
```

아직 라우트 미구현이다.

### FE 책임

예상 파일:

- `ExcellentFE/src/pages/Package.tsx`
- `ExcellentFE/src/pages/package-builder/*`
- `ExcellentFE/src/api/packageDraft.ts`
- `ExcellentFE/src/hooks/package/usePackageDraft.ts`
- `ExcellentFE/src/types/package.ts`

책임:

- 패키지 정책 목록을 보여준다.
- 정책별 허용 상품을 보여준다.
- 상품 추가/삭제/수량 변경을 처리한다.
- 중복 허용 여부를 UI에서 1차 안내한다.
- 최종 검증은 백엔드에 맡긴다.

### API 계약

현재 백엔드 라우터 기준:

```text
GET    /api/v1/cart/package-drafts/
POST   /api/v1/cart/package-drafts/
GET    /api/v1/cart/package-drafts/{id}/
PATCH  /api/v1/cart/package-drafts/{id}/
DELETE /api/v1/cart/package-drafts/{id}/
```

정책 조회:

```text
GET /api/v1/package-policies/manage/
```

운영 공개용 정책 조회 API는 별도로 분리하는 것이 좋다.

### BE 책임

관련 파일:

- `EasyBE/apps/cart/models.py`
- `EasyBE/apps/cart/views.py`
- `EasyBE/apps/cart/serializers.py`
- `EasyBE/apps/cart/services.py`
- `EasyBE/apps/products/models.py`
- `EasyBE/apps/products/serializers/package_policy.py`
- `EasyBE/apps/products/services/package_policy_command_service.py`

책임:

- draft 생성
- draft 구성품 추가/삭제/수량 변경
- `PackagePolicy` 기준 검증
- 가격 합산
- 할인 적용
- 시음 선택 가능 여부 검증

### 상태 변화

```text
PackageDraft 생성/수정
PackageDraftItem 생성/수정/삭제
PackageDraft.base_price 갱신
PackageDraft.discount_amount 갱신
PackageDraft.final_price 갱신
PackageDraft.status 갱신
```

### 금지사항

- 고객 커스텀 패키지를 `Product`로 저장하지 않는다.
- 같은 상품 중복 담기를 row 중복으로 표현하지 않는다.
- 정책 검증을 프론트에서만 처리하지 않는다.
- 관리 API를 공개 사용자 패키지 구성 화면에서 그대로 사용하지 않는다.

### 검증 기준

- 정책의 최소/최대 수량을 초과하면 저장이 실패한다.
- 중복 불가 정책에서 같은 상품을 여러 개 담을 수 없다.
- `ALLOWED_SET` 정책에서는 허용 상품 외 상품을 담을 수 없다.
- 주문 생성 시 draft는 `OrderCustomPackage` snapshot으로 고정된다.

### 정리 후보

- 공개용 package policy 조회 API와 관리자용 manage API를 분리해야 한다.
- draft UI가 구현되면 cart 응답 타입과 화면 표시를 다시 정리해야 한다.

## Flow 7. 사용자가 주문을 생성한다

### 목표

사용자가 선택한 일반 상품과 커스텀 패키지를 주문으로 확정한다.

### 진입점

```text
POST /api/v1/orders/create_from_cart/
```

FE 호출:

- `ExcellentFE/src/hooks/cart/useUserPostOrder.ts`
- `ExcellentFE/src/api/order.ts`

### FE 책임

- 선택한 `CartItem` id 목록을 보낸다.
- 선택한 `PackageDraft` id 목록을 보낸다.
- 픽업 정보 누락을 1차 차단한다.
- 주문 성공 후 장바구니/주문내역 이동 기준을 정한다.

### BE 책임

관련 파일:

- `EasyBE/apps/orders/views.py`
- `EasyBE/apps/orders/services.py`
- `EasyBE/apps/orders/models.py`
- `EasyBE/apps/cart/models.py`

책임:

- 요청 사용자의 장바구니 항목만 주문 가능하게 한다.
- 선택 항목만 주문한다.
- 픽업 정보가 없으면 실패시킨다.
- 일반 상품은 `OrderItem`으로 snapshot한다.
- 커스텀 패키지는 `OrderCustomPackage`와 `OrderCustomPackageItem`으로 snapshot한다.

### 상태 변화

```text
Order 생성
OrderItem 생성
OrderCustomPackage 생성
OrderCustomPackageItem 생성
PackageDraft.status = ORDERED
```

### 금지사항

- 주문 생성 후 상품 가격 변경이 과거 주문 금액에 영향을 주면 안 된다.
- 다른 사용자의 cart item id를 주문할 수 있으면 안 된다.
- package draft를 주문 후에도 DRAFT로 남기면 안 된다.

### 검증 기준

- 선택한 일반 상품만 주문된다.
- 선택한 커스텀 패키지만 주문된다.
- 주문 snapshot에 상품명, 가격, 수량, 정책명, 픽업 정보가 보존된다.

## Flow 8. 사용자가 리뷰를 남긴다

### 목표

사용자가 주문/시음 후 후기를 남기고, 장기적으로 입맛 프로필 학습에 활용한다.

### 현재 상태

현재 리뷰 모델과 API는 존재하지만, 태그 기반 학습 구조는 아직 구현 전이다.

상세 설계:

```text
docs/REVIEW_TASTE_LEARNING_DESIGN.md
```

### 현재 FE 책임

관련 파일:

- `ExcellentFE/src/pages/Feedback.tsx`
- `ExcellentFE/src/pages/my-page/TastingReviewModal.tsx`
- `ExcellentFE/src/hooks/order/useSubmitFeedback.ts`
- `ExcellentFE/src/hooks/order/useTastingReview.ts`
- `ExcellentFE/src/api/feedback/index.ts`
- `ExcellentFE/src/types/feedback.ts`

### 현재 API 계약

```text
GET    /api/v1/feedbacks/
POST   /api/v1/feedbacks/
GET    /api/v1/feedbacks/{id}/
PATCH  /api/v1/feedbacks/{id}/
DELETE /api/v1/feedbacks/{id}/
GET    /api/v1/feedbacks/recent/
GET    /api/v1/feedbacks/popular/
GET    /api/v1/feedbacks/personalized/
GET    /api/v1/user/feedbacks/
```

### 목표 리뷰 입력

사용자 입력:

- 평점
- 후기
- 좋았던 점 태그
- 아쉬웠던 점 태그
- 이미지

사용자가 직접 맛 점수를 다 입력하는 방식은 줄인다.

### 목표 BE 책임

예상 파일:

- `EasyBE/apps/feedback/services/feedback_command_service.py`
- `EasyBE/apps/feedback/selectors.py`
- `EasyBE/apps/feedback/services/feedback_analysis_service.py`
- `EasyBE/apps/users/services/taste_profile_learning_service.py`

책임:

- 리뷰 저장
- 태그 저장
- 상품 리뷰 수 갱신
- 분석 대기 상태 생성
- 분석 결과가 신뢰 가능한 경우에만 취향 프로필 반영

### 상태 변화

목표:

```text
Feedback 생성
FeedbackTagSelection 생성
FeedbackAnalysis 생성
TasteProfileUpdateLog 생성
PreferTasteProfile 소폭 갱신
```

### 금지사항

- AI 분석 실패 때문에 리뷰 저장을 실패시키지 않는다.
- `Feedback.save()`에서 취향 프로필까지 직접 수정하지 않는다.
- 평점만으로 입맛 프로필을 크게 바꾸지 않는다.
- 직접 맛 점수와 선호도를 같은 값처럼 취급하지 않는다.

### 검증 기준

- 리뷰 저장과 분석은 분리된다.
- 태그/후기/평점 신호가 일치할 때만 입맛 프로필에 반영된다.
- 어떤 리뷰가 어떤 입맛 축을 변경했는지 추적 가능하다.

## Flow 9. 관리자가 로그인한다

### 목표

관리자만 운영 화면에 접근한다.

### 진입점

```text
GET /admin/login
```

FE 라우트:

```text
ExcellentFE/src/pages/admin/AdminLogin.tsx
```

### FE 책임

관련 파일:

- `ExcellentFE/src/pages/admin/AdminLogin.tsx`
- `ExcellentFE/src/components/RequireAdmin.tsx`
- `ExcellentFE/src/stores/authStore.ts`
- `ExcellentFE/src/api/auth/index.ts`
- `ExcellentFE/src/constants/apiPaths.ts`

책임:

- 관리자 로그인 폼 제공
- 로그인 성공 시 토큰 저장
- 관리자 권한이 아니면 admin route 차단
- 일반 헤더에는 관리자 메뉴를 노출하지 않음
- 마이페이지 내부에서 관리자에게만 진입구 노출

### API 계약

```text
POST /api/v1/auth/admin/login/
```

### BE 책임

관련 파일:

- `EasyBE/apps/users/views/admin_login_view.py`
- `EasyBE/apps/users/models.py`
- `EasyBE/apps/users/serializers.py`

책임:

- 이메일/비밀번호 검증
- 관리자 권한 확인
- JWT 발급

### 상태 변화

서버 DB 상태 변화는 없다.

클라이언트:

```text
access token 저장
refresh token 저장
user role 저장
```

### 금지사항

- 관리자 화면 링크를 공개 헤더에 노출하지 않는다.
- FE guard만으로 관리자 API를 보호했다고 판단하지 않는다.
- 일반 로그인과 관리자 로그인을 섞어서 권한 의미를 흐리지 않는다.

### 검증 기준

- 일반 사용자는 `/admin` 접근 불가
- 관리자는 마이페이지에서 관리자 진입구 확인 가능
- 비로그인 사용자는 `/admin` 접근 시 차단

## Flow 10. 관리자가 상품과 패키지 정책을 등록한다

### 목표

운영자가 개발자 도움 없이 기본 상품, 고정 패키지, 패키지 정책을 등록한다.

### 진입점

```text
GET /admin
GET /admin/products
GET /admin/products/new
GET /admin/package-policies
```

### FE 책임

관련 파일:

- `ExcellentFE/src/pages/admin/AdminHome.tsx`
- `ExcellentFE/src/pages/admin/AdminProducts.tsx`
- `ExcellentFE/src/pages/admin/AdminProductCreate.tsx`
- `ExcellentFE/src/pages/admin/AdminPackagePolicies.tsx`
- `ExcellentFE/src/pages/admin/AdminPageShell.tsx`
- `ExcellentFE/src/api/admin/index.ts`
- `ExcellentFE/src/types/admin.ts`
- `ExcellentFE/src/constants/admin.ts`

책임:

- 상품 목록 조회
- 일반 상품 등록
- 고정 패키지 상품 등록
- 패키지 정책 목록/등록
- 시음 가능 여부 설정
- 폼 선택지를 상수로 관리

### API 계약

```text
GET    /api/v1/products/manage/
GET    /api/v1/products/{id}/manage/
PATCH  /api/v1/products/{id}/manage/
DELETE /api/v1/products/{id}/manage/

POST   /api/v1/products/individual/create/
POST   /api/v1/products/package/create/

GET    /api/v1/drinks/for-package/
GET    /api/v1/breweries/

GET    /api/v1/package-policies/manage/
POST   /api/v1/package-policies/manage/
GET    /api/v1/package-policies/{id}/manage/
PATCH  /api/v1/package-policies/{id}/manage/
DELETE /api/v1/package-policies/{id}/manage/
```

### BE 책임

관련 파일:

- `EasyBE/apps/products/views/product/admin.py`
- `EasyBE/apps/products/views/drink.py`
- `EasyBE/apps/products/views/brewery.py`
- `EasyBE/apps/products/serializers/product/create.py`
- `EasyBE/apps/products/serializers/product/update.py`
- `EasyBE/apps/products/serializers/package_policy.py`
- `EasyBE/apps/products/services/product_command_service.py`
- `EasyBE/apps/products/services/package_policy_command_service.py`
- `EasyBE/apps/products/models.py`

책임:

- 관리자 권한 확인
- 상품 생성 입력 검증
- `Drink`, `Package`, `Product`, `PackageItem`, `ProductImage` 생성 transaction 처리
- `PackagePolicy` 생성/수정/비활성화
- 상품 상태 변경

### 상태 변화

일반 상품 등록:

```text
Drink 생성
Product 생성
ProductImage 생성
```

패키지 상품 등록:

```text
Package 생성
PackageItem 생성
Product 생성
ProductImage 생성
```

패키지 정책 등록:

```text
PackagePolicy 생성
PackagePolicyAllowedProduct 생성
```

### 금지사항

- 관리자용 API를 `AllowAny`로 열어두지 않는다.
- 상품 생성 transaction을 serializer 안에 숨기지 않는다.
- 패키지 구성 수량을 row 중복으로 만들지 않는다.
- 시음 가능 여부를 상품 타입으로 분리하지 않는다.

### 검증 기준

- 관리자가 단일 상품을 등록할 수 있다.
- 관리자가 고정 패키지 상품을 등록할 수 있다.
- 관리자가 패키지 정책을 등록할 수 있다.
- 등록된 상품이 일반 상품 API에서 조회된다.
- `is_tasting_available`이 응답에 반영된다.

### 정리 후보

- 상품 수정 화면이 아직 없다.
- 이미지 URL 입력은 운영 전 파일 업로드 여부를 결정해야 한다.
- 양조장/술 원본 데이터 등록 화면이 별도로 필요하다.

## 코드 검토 체크리스트

새 코드가 들어오면 아래를 확인한다.

- 이 코드는 어느 Flow에 속하는가?
- Flow 문서에 없는 새 상태 변화가 생겼는가?
- FE API 경로가 `API_PATHS`를 거치는가?
- BE view가 service/selector 없이 직접 로직을 많이 갖고 있지 않은가?
- serializer가 외부 호출이나 cross-model write를 하지 않는가?
- model `save/delete`에 다른 도메인 변경이 들어가지 않았는가?
- 하드코딩된 id, 날짜, URL, 정책값이 생기지 않았는가?
- 운영자용 API와 공개 API가 섞이지 않았는가?
- 커스텀 패키지를 `Product`로 저장하려는 흐름이 생기지 않았는가?
- 리뷰 분석 실패가 사용자 행동 실패로 이어지지 않는가?
- 추천 문구가 실제 추천 근거보다 과장되어 있지 않은가?

## 불필요 코드 제거 기준

아래에 해당하면 제거 또는 리팩터링 후보로 본다.

- 실제 Flow에서 호출되지 않는 page/component/hook/api
- 현재 API 경로와 맞지 않는 mock handler
- 같은 응답을 다른 type으로 중복 정의한 코드
- FE 화면에서만 유지되는 서버 상태 복사본
- serializer와 service 양쪽에 중복된 검증
- view에 남아 있는 긴 queryset 조립
- model `save/delete`에 숨어 있는 side effect
- 관리자 화면에서만 필요한 코드를 일반 사용자 플로우에 끼워 넣은 경우
- 운영 정책을 문자열/숫자로 하드코딩한 경우

## 문서 갱신 규칙

아래 변경이 생기면 이 문서를 같이 수정한다.

- 라우트 추가/삭제
- API 경로 변경
- 모델 상태 변화 추가
- 주문/장바구니/패키지 lifecycle 변경
- 리뷰/추천/입맛 학습 기준 변경
- 관리자 입력 방식 변경
- 공개 API와 관리자 API의 책임 경계 변경
