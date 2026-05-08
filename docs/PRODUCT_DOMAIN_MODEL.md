# Product Domain Model

## 문서 목적

이 문서는 Moeun의 상품, 패키지, 시음, 장바구니 커스텀 패키지 구조를 설명한다.

핵심은 아래다.

- 판매 가능한 카탈로그 상품은 `Product`로 본다.
- `Product`는 단일 술 `Drink` 또는 고정 패키지 `Package` 중 하나만 참조한다.
- 고객이 직접 고른 패키지는 카탈로그 상품이 아니라 장바구니 안의 `PackageDraft`다.
- 시음은 상품 타입이 아니라 상품/패키지 선택 옵션이다.

## 현재 결론

현재 구조는 아래 기준으로 확정한다.

- 단일 상품: `Product.drink`가 있는 상품
- 고정 패키지 상품: `Product.package`가 있는 상품
- 커스텀 패키지: `cart.PackageDraft`와 `cart.PackageDraftItem`
- 주문 확정 후 커스텀 패키지: `orders.OrderCustomPackage` snapshot
- 패키지 구성 규칙: `PackagePolicy`
- 시음 가능 여부: `Product.is_tasting_available`
- 시음 선택 여부: `PackageDraft.is_tasting_selected`, 주문 snapshot의 `is_tasting_selected`

`Product`는 공통 판매 껍데기지만, 고객 커스텀 패키지까지 억지로 `Product`에 넣지 않는다.

## 왜 이렇게 나누는가

카탈로그 상품과 사용자 임시 조합은 lifecycle이 다르다.

- 카탈로그 상품은 검색, 추천, 좋아요, 관리자 등록 대상이다.
- 커스텀 패키지는 특정 사용자가 장바구니에서 잠깐 구성하는 주문 전 상태다.
- 주문이 생성되면 당시 구성과 가격은 snapshot으로 고정되어야 한다.

따라서 고객이 만든 조합을 `Product`에 넣으면 검색/추천/운영 데이터와 섞인다. 이 구조는 운영으로 갈수록 레거시가 되기 쉽다.

## 모델 구조

### Brewery

양조장 정보다.

주요 책임:

- 양조장명
- 지역/주소
- 연락처
- 설명/이미지
- 활성 상태

### Drink

술 원본 정보다.

주요 책임:

- 술 이름
- 양조장
- 주종
- 도수
- 용량
- 원재료
- 맛 프로필 6축

맛 프로필 6축:

- `sweetness_level`
- `acidity_level`
- `body_level`
- `carbonation_level`
- `bitterness_level`
- `aroma_level`

`Drink`는 “무엇을 마시는가”를 나타낸다. 가격, 좋아요, 리뷰 수 같은 판매 통계는 `Product`가 가진다.

### Package

운영자가 등록하는 고정 패키지 원본이다.

현재 책임:

- 패키지명
- 패키지 타입
- 연결된 `PackagePolicy`
- 구성 술 목록

현재 `PackageItem`은 `Drink` 기준으로 구성된다.

```text
Package
-> PackageItem
-> Drink
```

고정 패키지도 실제 판매 대상이 되려면 반드시 `Product.package`로 연결되어야 한다.

### PackageItem

고정 패키지 구성품이다.

현재 필드:

- `package`
- `drink`
- `quantity`
- `sort_order`

같은 술을 여러 번 담는 것은 row 중복이 아니라 `quantity` 증가로 표현한다. 그래서 `unique(package, drink)`를 유지한다.

장기적으로 고정 패키지 안에 다른 패키지 상품까지 넣어야 한다면 `Drink` 기준에서 `Product` 기준 구성품으로 이행한다. 지금 1차 범위에서는 고정 패키지 구성품을 술 단위로 두는 것이 더 단순하다.

### Product

판매 가능한 카탈로그 상품이다.

현재 구조:

```text
Product
├── drink   nullable one-to-one
└── package nullable one-to-one
```

제약:

- `drink`와 `package` 중 하나는 반드시 있어야 한다.
- 둘을 동시에 가질 수 없다.

현재 주요 필드:

- 가격: `price`, `original_price`, `discount`
- 설명: `description`, `description_image_url`
- 시음 설정: `is_tasting_available`
- 통계: `view_count`, `order_count`, `like_count`, `review_count`
- 상태: `ACTIVE`, `INACTIVE`, `OUT_OF_STOCK`

현재 `name`과 `product_type`은 DB 필드가 아니라 property다.

```text
Product.name
-> drink.name 또는 package.name

Product.product_type
-> individual 또는 package
```

이 방식은 현재 스키마 변경량을 줄이는 장점이 있다. 다만 판매명과 원본명이 달라져야 하는 운영 요구가 생기면 `Product.name`을 실제 필드로 승격하는 것이 맞다.

### ProductTag

운영자가 직접 만들고 바꿀 수 있는 상품 분류 태그다.

기존 상품 boolean 필드는 제거한다.

```text
ProductTag
├── name
├── slug
├── group
├── description
├── is_active
└── sort_order

ProductTagging
├── product
└── tag
```

태그는 상품의 실제 판매 상태가 아니라 노출/추천/특성 분류다.

예:

- `award-winning`: 수상작
- `regional-specialty`: 지역 특산주
- `premium`: 프리미엄
- `gift-suitable`: 선물 적합
- `limited-edition`: 한정판
- `organic`: 유기농

태그가 늘어나도 `Product` 필드나 마이그레이션을 추가하지 않는다.

`is_tasting_available`은 태그가 아니라 시음 판매 정책이므로 `Product` 필드로 유지한다.

### ProductImage

상품 이미지다.

현재 책임:

- 이미지 URL
- 메인 이미지 여부

상품당 메인 이미지는 하나만 허용한다.

### ProductLike

상품 좋아요다.

좋아요는 카탈로그 상품 기준으로만 동작한다. `PackageDraft` 같은 사용자 임시 조합에는 좋아요를 붙이지 않는다.

## PackagePolicy

패키지 구성과 할인 규칙이다.

현재 필드:

- `name`
- `status`
- `min_items`
- `max_items`
- `allow_duplicate_items`
- `allowed_item_scope`
- `discount_type`
- `discount_value`
- `allowed_products`

`allowed_item_scope`:

- `ALL_PRODUCTS`: 모든 카탈로그 상품 허용
- `SINGLE_PRODUCTS`: 단일 상품만 허용
- `PACKAGE_PRODUCTS`: 패키지 상품만 허용
- `ALLOWED_SET`: 명시적으로 허용한 상품만 허용

`discount_type`:

- `NONE`
- `FIXED_AMOUNT`

정책은 두 곳에서 쓰인다.

- 운영자가 만든 고정 패키지의 구성 규칙
- 고객이 장바구니에서 만드는 커스텀 패키지 draft의 구성 규칙

## PackagePolicyAllowedProduct

`ALLOWED_SET` 정책에서 명시적으로 허용한 상품 목록이다.

```text
PackagePolicy
-> PackagePolicyAllowedProduct
-> Product
```

정책의 허용 대상은 `Drink`가 아니라 `Product`다. 고객이 실제로 고르는 대상이 판매 상품이기 때문이다.

## 커스텀 패키지

### PackageDraft

사용자가 장바구니에서 구성 중인 커스텀 패키지다.

주요 필드:

- `user`
- `policy`
- `display_name`
- `base_price`
- `discount_amount`
- `final_price`
- `status`
- `pickup_store`
- `pickup_date`
- `is_tasting_selected`

주의:

- `pickup_store`, `pickup_date`는 현재 구현 기준의 주문 전 정보다.
- 실제 운영 방식이 픽업, 배송, 문의형 신청 중 무엇으로 갈지 확정되기 전까지 이 필드를 더 강한 운영 정책으로 확장하지 않는다.
- 운영 방식 확정 후 필요하면 `fulfillment` 구조로 일반화한다.

상태:

- `DRAFT`: 작성 중
- `READY`: 주문 가능
- `ORDERED`: 주문 완료

`PackageDraft`는 카탈로그 상품이 아니다. 검색, 추천, 좋아요 대상도 아니다.

### PackageDraftItem

커스텀 패키지 구성품이다.

주요 필드:

- `draft`
- `product`
- `quantity`
- `sort_order`

같은 상품을 여러 번 담으면 row를 추가하지 않고 `quantity`를 증가시킨다. 중복 허용 여부는 `PackagePolicy.allow_duplicate_items`로 판단한다.

## 주문 snapshot

주문 생성 후에는 장바구니 상태가 아니라 주문 당시 상태를 보존해야 한다.

현재 주문은 실제 판매 운영 전 단계이므로 테스트 결제 모드로 동작한다.

기준:

- 화면과 데이터 구조는 실제 주문/결제로 전환 가능하게 만든다.
- 운영 면허와 판매 주체가 확정되기 전까지 실제 결제 승인으로 처리하지 않는다.
- 주문 데이터에는 테스트 주문 여부를 명시한다.
- 결제 정보는 `Order`에 직접 넣지 않고 `Payment`로 분리한다.

일반 상품:

```text
Order
-> OrderItem
-> Product
-> Payment
```

커스텀 패키지:

```text
Order
-> OrderCustomPackage
-> OrderCustomPackageItem
-> Product
```

`OrderCustomPackage`는 아래 값을 snapshot으로 보존한다.

- 패키지 표시명
- 정책명
- 구성품 합산가
- 할인 금액
- 최종 가격
- 현재 구현 기준의 픽업 매장/날짜
- 시음 선택 여부

`OrderCustomPackageItem`은 주문 당시 상품명, 단가, 수량을 보존한다.

### Payment

주문 결제 상태를 관리하는 모델이다.

```text
Payment
├── order
├── provider
├── payment_key
├── merchant_uid
├── amount
├── status
├── is_test_payment
├── approved_at
└── raw_response
```

현재 구현은 `provider=TOSS_TEST`를 사용해 토스페이먼츠 테스트 결제창을 연동한다.

토스페이먼츠 테스트 결제 흐름:

```text
Order 생성
-> Payment 생성(provider=TOSS_TEST, status=READY)
-> FE 토스 결제창 요청
-> successUrl로 paymentKey/orderId/amount 반환
-> BE가 주문 금액 검증
-> BE가 토스 결제 승인 API 호출
-> Payment.status=PAID
-> Order.payment_status=PAID
```

시크릿 키는 백엔드 환경 변수 `TOSS_PAYMENTS_SECRET_KEY`에만 둔다. 프론트에는 `VITE_TOSS_PAYMENTS_CLIENT_KEY`만 노출한다.

주문 상태와 결제 상태는 분리한다.

```text
Order.status
-> 주문/수령 처리 상태

Order.payment_status
-> 결제 처리 상태
```

테스트 결제 승인 전 주문은 `PENDING_PAYMENT`로 생성된다. 테스트 결제가 승인되면 `payment_status=PAID`, `Order.status=CONFIRMED`로 전환한다.

주문 수령 방식은 `fulfillment_method`로 관리한다.

- `PICKUP`: 매장 수령
- `DELIVERY`: 배송
- `UNDECIDED`: 운영 방식 미정 또는 데모

현재 기존 장바구니 UI는 픽업 기준이므로 1차 주문 생성은 `PICKUP`을 기본값으로 사용한다.

## 시음 설계

시음은 별도 모델로 시작하지 않는다.

현재 기준:

- 상품이 시음 신청 가능한지: `Product.is_tasting_available`
- 고객이 커스텀 패키지에서 시음을 선택했는지: `PackageDraft.is_tasting_selected`
- 주문 후 시음 선택 snapshot: `OrderCustomPackage.is_tasting_selected`

별도 `TastingRequest` 모델은 아직 만들지 않는다.

이유:

- 현재 시음은 별도 승인/처리 workflow가 아니라 주문 선택 옵션에 가깝다.
- 별도 상태 관리가 생기기 전까지는 필드가 더 단순하고 안전하다.

나중에 아래 요구가 생기면 모델 승격을 검토한다.

- 시음 신청 승인/거절
- 시음 준비 상태
- 시음 전용 재고
- 관리자 처리 이력

## 관리자 입력 흐름

관리자는 현재 아래를 등록할 수 있다.

- 단일 상품
- 고정 패키지 상품
- 패키지 정책
- 상품별 시음 가능 여부

상품 등록은 `ProductCommandService`가 담당한다. serializer는 입력 검증에 집중하고, 여러 모델을 함께 만드는 transaction은 service가 책임진다.

## 남은 설계 판단

아직 확정하지 않은 항목:

- `Product.name`을 실제 DB 필드로 승격할지
- 고정 패키지 구성품을 `Drink` 기준에서 `Product` 기준으로 바꿀지
- 시음 처리를 별도 업무 모델로 승격할지
- 패키지 할인 정책에 퍼센트 할인을 추가할지
- 운영 이미지 업로드를 URL 입력에서 파일 업로드로 바꿀지

## 현재 완료 기준

이 문서 기준으로 현재 구조가 맞으려면 아래를 만족해야 한다.

- 단일 상품과 고정 패키지는 모두 `Product`로 조회된다.
- 고객 커스텀 패키지는 `Product`가 아니라 `PackageDraft`로 관리된다.
- 패키지 구성 정책은 `PackagePolicy`에 모인다.
- 시음 가능 여부는 상품 설정값으로 관리된다.
- 주문 생성 시 커스텀 패키지는 snapshot으로 보존된다.
