# Product Domain Model v1

## 지금 읽을 부분

- `핵심 결론`: 제품을 어떤 모델로 나눌지
- `모델 초안`: 실제 엔티티 구조
- `분리 기준`: 카탈로그 상품과 커스텀 패키지를 왜 분리하는지
- `보류 항목`: 아직 결정하지 않은 것

## 결론

제품 도메인은 아래 기준으로 설계한다.

- 카탈로그 상품은 `단일 제품`, `고정 패키지` 2종류로 본다.
- DB 구조는 `Product` 공통 엔티티 + 상세 엔티티 분리로 간다.
- `고객이 고른 패키지`는 `Product` 가 아니다.
- 고객 커스텀 패키지는 `임시 조합(draft)` 으로 저장하고, 주문 시 snapshot 으로 고정한다.
- 관리자는 고정 패키지를 등록/관리할 수 있다.
- 고객은 관리자 정책 안에서 패키지를 조합하고 관리할 수 있다.
- `시음`은 제품 타입이 아니라, 제품/패키지에 붙는 단순 옵션 기능이다.

한 줄로 요약하면 이렇다.

- `카탈로그 상품`과 `사용자 조합물`을 같은 모델에 넣지 않는다.

## 왜 이렇게 가는가

### 현재 요구사항

제품은 크게 3가지다.

- 단일 제품
- 패키지 제품
- 시음 신청 대상

그리고 패키지는 다시 두 종류가 있다.

- 우리가 정한 고정 패키지
- 고객이 주문 직전에 조합하는 커스텀 패키지

여기서 확정된 요구사항은 다음과 같다.

1. 관리자는 고정 패키지를 등록하고 관리할 수 있어야 한다.
2. 고객은 패키지를 직접 조합할 수 있어야 한다.
3. 고객이 조합할 수 있는 범위는 관리자 정책으로 열고 제한할 수 있어야 한다.
4. 고객은 장바구니 안에서 커스텀 패키지를 여러 개 만들고 수정할 수 있어야 한다.
5. 시음은 단일 제품에도, 고정 패키지에도, 고객이 만든 패키지에도 적용 가능해야 한다.
6. 패키지 정책은 패키지별로 고정 가능해야 한다.

이 상황에서 가장 중요한 설계 기준은 다음 두 가지다.

1. 카탈로그에 공개되는 상품과 사용자 개인 조합 상태를 섞지 않는다.
2. 시음은 제품 분류가 아니라 별도 옵션으로 분리한다.

## 선택지 비교

### 옵션 A. `Product` 하나에 모든 경우를 분기 처리

예:

- `Product.drink`
- `Product.package`
- `Product.tasting_config`
- `Product.custom_package_config`

장점:

- 처음엔 구현이 빠르다.
- 테이블 수가 적다.

단점:

- 타입 분기가 계속 늘어난다.
- serializer, view, service가 쉽게 두꺼워진다.
- 커스텀 패키지까지 상품처럼 취급하게 되어 책임이 섞인다.
- 레거시 냄새가 강해진다.

판단:

- 채택하지 않는다.

### 옵션 B. 타입별 상세 엔티티 분리 + 커스텀 패키지 별도 도메인

장점:

- 책임이 명확하다.
- 고정 패키지와 고객 커스텀 패키지를 다른 lifecycle 로 분리할 수 있다.
- 커스텀 패키지를 장바구니/주문 흐름으로 자연스럽게 넣을 수 있다.
- 운영 정책과 확장성 면에서 안전하다.
- 시음을 모델이 아닌 필드/정책으로 처리하기 쉽다.

단점:

- 모델 수가 늘어난다.
- 초기 마이그레이션 비용이 있다.

판단:

- 채택한다.

## 제품 도메인 핵심 원칙

1. `Product` 는 판매 단위다.
2. `Drink` 는 원본 술 정보다.
3. `Package` 는 번들 상품이지만, `Tasting` 은 상품 타입이 아니다.
4. 커스텀 패키지는 카탈로그 상품이 아니라 사용자 임시 조합이다.
5. 주문이 생성되면 당시 구성과 가격은 snapshot 으로 고정한다.
6. 관리자용 고정 패키지와 고객용 조합 패키지는 서로 다른 lifecycle 을 가진다.
7. 패키지 규칙은 `PackagePolicy` 가 담당하고, 시음 가능 여부는 필드와 정책 설정으로 제어한다.

## 카탈로그 모델 초안

### 1. Brewery

양조장 기본 정보.

예상 책임:

- 이름
- 지역
- 설명
- 연락처
- 활성 상태

이 모델은 지금 구조를 거의 그대로 유지해도 된다.

### 2. Drink

술 원본 정보.

예상 책임:

- 술 이름
- 양조장
- 원재료
- 주종
- 도수
- 용량
- 맛 프로필

원칙:

- `Drink` 는 “무엇을 마시는가”를 표현한다.
- 판매 가격, 좋아요, 리뷰 수 같은 판매 통계는 여기 두지 않는다.

### 3. Product

공통 판매 단위.

예상 필드:

- `id`
- `product_type = SINGLE | PACKAGE`
- `name`
- `status`
- `description`
- `description_image_url`
- `price`
- `original_price`
- `discount_amount`
- `is_gift_suitable`
- `is_award_winning`
- `is_regional_specialty`
- `is_limited_edition`
- `is_premium`
- `is_organic`
- `is_tasting_available`
- `view_count`
- `order_count`
- `like_count`
- `review_count`
- `created_at`
- `updated_at`

### 왜 `Product.name` 을 직접 두는가

장점:

- 검색/정렬/응답 구성이 단순해진다.
- `drink.name` 과 `package.name` 분기 의존이 줄어든다.
- serializer가 훨씬 깔끔해진다.

단점:

- 일부 이름 중복이 생길 수 있다.
- 원본 정보와 판매용 이름이 분리된다.

채택 이유:

- 판매 단위 이름과 원본 drink/package 이름은 실제 서비스에서 다를 수 있다.
- 응답과 검색을 단순화하는 이점이 더 크다.

### 4. SingleProduct

단일 판매 상품 상세.

예상 필드:

- `product` 1:1
- `drink` 1:1

의미:

- 한 병 단위로 판매하는 일반 상품

### 5. BundleProduct

고정 번들 상품 상세.

예상 필드:

- `product` 1:1
- `package_policy`
- `is_tasting_available`

의미:

- 우리가 정한 고정 패키지
- 이 패키지에 고정 적용되는 패키지 정책 참조
- 이 패키지 자체의 시음 가능 여부 표시

### 왜 `PackagePolicy` 를 패키지에 연결하는가

장점:

- 패키지별로 다른 규칙을 가질 수 있다.
- 관리자가 운영 정책을 패키지 단위로 고정할 수 있다.
- 같은 검증 규칙을 고정 패키지와 고객 draft 에 일관되게 재사용할 수 있다.

단점:

- 정책 엔티티가 추가된다.
- 주문 시 snapshot 범위를 더 신경써야 한다.

채택 이유:

- 사용자가 “패키지별로 고정 가능한 정책”을 원한다는 요구사항과 정확히 맞는다.

### 6. BundleProductItem

번들 구성품.

예상 필드:

- `bundle_product`
- `product`
- `quantity`
- `sort_order`

해석:

- 기본적으로는 패키지를 구성하는 판매 단위를 담는다.
- 필요 시 정책으로 허용 타입을 제한한다.

현재 코드 적용:

- 기존 스키마 호환을 위해 현재는 `PackageItem` 이 `package + drink + quantity + sort_order` 를 가진다.
- 같은 술을 여러 번 담는 행위는 row 중복이 아니라 `quantity` 증가로 표현한다.
- `unique(package, drink)` 는 유지한다.
- 장기적으로 “모든 제품/패키지를 구성품으로 허용”하려면 `product` 기준 item으로 이행한다.

### 7. ProductImage

공통 상품 이미지.

예상 책임:

- `product`
- `image_url`
- `is_main`
- `sort_order`

원칙:

- 이미지 구조는 공통 모델을 유지한다.

### 8. ProductLike

공통 좋아요.

예상 책임:

- `user`
- `product`

원칙:

- 좋아요는 카탈로그 상품 기준으로만 동작한다.
- 커스텀 패키지에는 좋아요를 붙이지 않는다.

## 커스텀 패키지 도메인 초안

## 핵심 판단

고객이 고른 패키지는 `Product` 로 저장하지 않는다.

이유:

- 공개 카탈로그 상품이 아니다.
- 사용자별 임시 상태다.
- 검색/추천/좋아요 대상이 아니다.
- 주문 직전에만 의미가 있다.

대신 아래처럼 나눈다.

- 관리자는 `고정 패키지 상품` 을 카탈로그에 등록한다.
- 관리자는 `패키지 규칙(policy)` 도 관리한다.
- 고객은 그 policy 를 기반으로 자신의 패키지 draft 를 만든다.

### 1. PackagePolicy

관리자가 만드는 패키지 규칙.

예상 필드:

- `name`
- `description`
- `status`
- `selection_scope = ALL_PRODUCTS | ALLOWED_SET | CATEGORY_LIMITED`
- `duplicate_policy = ALLOW | DENY`
- `min_total_quantity`
- `max_total_quantity`
- `max_quantity_per_product`
- `allowed_product_types`
- `is_tasting_allowed`
- `discount_type = NONE | FIXED_AMOUNT | PERCENTAGE`
- `discount_value`
- `created_at`
- `updated_at`

이 모델은 패키지 구성 규칙만 담당한다.

적용 방식:

- `BundleProduct.package_policy`
- `PackageDraft.package_policy`
- `PackageDraft` 의 시음 가능 여부도 이 정책을 따른다.

현재 코드 적용:

- `PackagePolicy` 는 `min_items`, `max_items`, `allow_duplicate_items`, `allowed_item_scope`, `discount_type`, `discount_value` 를 가진다.
- 고정 패키지는 `Package.policy` 로 정책을 참조한다.
- `PackagePolicyAllowedProduct` 는 허용 상품 집합을 저장하기 위한 기반 모델로 추가한다.
- 관리자 정책 생성/수정은 `PackagePolicyCommandService` 와 `/api/v1/package-policies/*/manage/` 경로에서 처리한다.
- 고정 패키지는 `Drink` 구성 기반이지만, 정책의 허용 상품 검증은 `Drink.product` 를 통해 product 기준으로 맞춘다.
- 고객 커스텀 draft는 처음부터 `Product` 구성 기반이므로 `allowed_item_scope` 와 `allowed_products` 를 직접 검증한다.

### 2. PackagePolicyAllowedProduct

허용 목록 기반 정책일 때 사용.

예상 필드:

- `package_policy`
- `product`

### 선택 범위 해석

- `ALL_PRODUCTS`: 정책상 허용된 모든 카탈로그 상품을 선택 가능
- `ALLOWED_SET`: 관리자가 지정한 상품 집합 안에서만 선택 가능
- `CATEGORY_LIMITED`: 특정 상품 타입/카테고리 조건 안에서만 선택 가능

### 왜 drink 가 아니라 product 기준인가

장점:

- 고객이 선택하는 대상을 카탈로그 판매 단위 기준으로 맞출 수 있다.
- 가격과 노출 정보를 공통적으로 다루기 쉽다.
- 관리자 정책에서 허용 상품 범위를 더 유연하게 제어할 수 있다.

단점:

- 실제로는 단일 상품만 허용하는 정책이 더 많을 수 있어 검증 규칙이 중요하다.

채택 이유:

- “모든 제품 또는 패키지를 정책 안에서 허용/제한할 수 있어야 한다”는 요구사항과 가장 잘 맞는다.

### 3. PackageDraft

사용자의 장바구니 안 임시 조합.

예상 필드:

- `user`
- `package_policy`
- `display_name`
- `base_price`
- `discount_amount`
- `final_price`
- `status`
- `created_at`
- `updated_at`

원칙:

- 사용자당 여러 개 생성 가능해야 한다.
- 장바구니에서 독립 엔티티로 동작한다.

현재 코드 적용:

- `cart.PackageDraft` 로 구현한다.
- `user`, `policy`, `display_name`, `base_price`, `discount_amount`, `final_price`, `status`, `pickup_store`, `pickup_date`, `is_tasting_selected` 를 가진다.
- 장바구니 목록은 일반 `CartItem` 과 `PackageDraft` 를 함께 반환하고 총액도 함께 합산한다.
- 주문 생성 시 draft는 삭제하지 않고 `ORDERED` 상태로 전환한다.

### 4. PackageDraftItem

임시 조합 구성품.

예상 필드:

- `draft`
- `product`
- `quantity`

제약:

- `unique(draft, product)`

현재 코드 적용:

- `cart.PackageDraftItem` 으로 구현한다.
- 같은 상품을 여러 번 담으면 row를 늘리지 않고 `quantity` 를 증가시킨다.
- `sort_order` 로 노출 순서를 관리한다.
- 정책의 `min_items`, `max_items`, `allow_duplicate_items`, `allowed_item_scope`, `allowed_products` 를 service에서 최종 검증한다.

### 왜 `1 row + quantity` 인가

장점:

- 수량, 가격, 수정, 삭제가 단순하다.
- 중복 허용/금지 정책을 service에서 쉽게 검증할 수 있다.
- 주문 snapshot 으로 넘기기 쉽다.

단점:

- UI에서 사용자가 “반복해서 담는 행위”를 row 추가로 표현하고 싶다면 별도 처리 필요

채택 이유:

- 데이터 정합성과 운영 단순성이 훨씬 중요하다.

## 시음 옵션 설계

## 핵심 판단

시음은 별도 요청 모델로 시작하지 않는다.

대신 아래 방식으로 설계한다.

- `Product.is_tasting_available`
- `BundleProduct.is_tasting_available`
- `PackagePolicy.is_tasting_allowed`
- 필요 시 `PackageDraft.is_tasting_selected`
- 주문 snapshot 에 `is_tasting_selected`

### 왜 단순 필드로 가는가

장점:

- 구조가 단순하다.
- 현재 요구사항에 맞다.
- 별도 승인/처리 workflow 가 없을 때 과설계를 막을 수 있다.
- 장바구니/주문 흐름에 자연스럽게 녹일 수 있다.

단점:

- 나중에 시음 승인 상태, 처리 이력, 관리자 워크플로우가 생기면 모델 승격이 필요하다.

채택 이유:

- 지금 시점의 시음은 독립 업무 흐름보다 “선택 가능한 옵션”에 가깝다.
- 따라서 모델보다 필드와 정책 설정으로 다루는 편이 더 정석적이고 단순하다.

## 제품 Write Path 설계

## 핵심 판단

제품 생성/수정/삭제의 오케스트레이션은 serializer가 아니라 service가 가진다.

즉 흐름은 아래로 고정한다.

1. `View`
2. `Request Serializer`
3. `Command Service`
4. `Response Serializer`

### 왜 serializer.create/update 로 몰지 않는가

장점:

- 처음엔 빠르게 만든다.
- DRF 기본 패턴처럼 보인다.

단점:

- `Drink + Product + Image + Bundle + Policy` 생성이 serializer 안에서 섞인다.
- transaction 경계가 숨는다.
- 예외 정책과 운영 로그를 일관되게 넣기 어렵다.
- 향후 패키지 정책과 시음 옵션이 붙을수록 serializer가 비대해진다.

판단:

- 채택하지 않는다.

### 왜 view가 직접 오케스트레이션하지 않는가

장점:

- 흐름이 눈에 바로 보인다.

단점:

- view가 컨트롤러를 넘어서 비즈니스 로직을 가지게 된다.
- admin/public 경로가 늘수록 중복이 생긴다.

판단:

- 채택하지 않는다.

### 왜 Command Service 로 모으는가

장점:

- transaction, 검증 이후 분기, cross-model write를 한 곳에서 관리할 수 있다.
- view는 얇게 유지되고 serializer는 검증에 집중한다.
- 이후 정책, 로깅, 감사 이력, soft delete 기준을 붙이기 쉽다.

단점:

- 서비스 클래스 수가 늘어난다.
- 초반에는 파일 분리가 다소 많아 보인다.

판단:

- 채택한다.

## 권장 서비스 구조

`products` 내부 write 서비스는 아래처럼 나눈다.

- `ProductCommandService`
- `BundleProductCommandService`
- `PackagePolicyCommandService`

초기에는 `ProductCommandService` 하나로 시작해도 된다. 다만 파일 안 메서드는 유스케이스별로 분리한다.

예:

- `create_single_product(...)`
- `create_bundle_product(...)`
- `update_product(...)`
- `deactivate_product(...)`
- `change_product_status(...)`

## 역할 분리 기준

### View

해야 할 일:

- 권한 확인
- request serializer 호출
- command service 호출
- response serializer 반환

하지 말아야 할 일:

- `Drink`, `Package`, `ProductImage` 를 직접 생성
- 패키지 중복 허용 정책을 직접 판단
- 삭제 가능 여부를 모델 관계 전체를 순회하며 직접 계산

### Request Serializer

해야 할 일:

- 필드 타입 검증
- 필수값 검증
- 중복 ID, 비어 있는 이름, 범위값 같은 입력 검증
- ID 목록 형태 정리

하지 말아야 할 일:

- 여러 모델 생성
- 파일 업로드
- transaction 처리
- cross-domain side effect

### Command Service

해야 할 일:

- `transaction.atomic` 경계
- `Drink`, `Product`, `BundleProduct`, `BundleProductItem`, `ProductImage` 생성/수정 orchestration
- 정책 검증 이후 실제 write 수행
- soft delete / 상태 전이 처리
- 필요한 도메인 예외 발생

## 유스케이스별 기준

### 1. 단일 상품 생성

흐름:

1. request serializer가 `drink_info`, `product_info`, `images` 를 검증
2. `ProductCommandService.create_single_product` 호출
3. service가 `Drink` 생성
4. service가 `Product` 생성
5. service가 이미지 생성
6. response serializer 반환

원칙:

- serializer가 `Drink.objects.create()` 를 직접 호출하지 않는다.
- 이미지 생성 실패까지 포함해 한 transaction 으로 본다.

### 2. 고정 패키지 생성

흐름:

1. request serializer가 패키지명, 구성 상품 ID, 정책 ID, 이미지, 공통 상품 정보를 검증
2. `BundleProductCommandService.create_bundle_product` 호출
3. service가 패키지 상세 엔티티와 구성품 생성
4. service가 `Product` 공통 정보 생성
5. service가 이미지 저장
6. response serializer 반환

원칙:

- 중복 허용/금지 판단은 policy 기준으로 service에서 최종 검증
- serializer는 ID 목록 형식만 검증

### 3. 상품 수정

수정은 둘로 나눈다.

- 공통 판매 정보 수정
- 상세 정보 수정

공통 판매 정보:

- 이름
- 가격
- 설명
- 노출 플래그
- 상태
- 시음 가능 여부

상세 정보:

- 단일 상품의 원본 술 정보
- 고정 패키지의 구성품
- 고정 패키지의 연결 policy

원칙:

- 한 endpoint 에서 모든 경우를 무리하게 처리하지 않는다.
- 공통 수정과 상세 수정 endpoint 를 분리할 수 있으면 분리하는 편이 낫다.

현재 코드 적용 기준:

- 기존 관리자 endpoint 제약 때문에 `PATCH /products/{id}/manage/` 에서 공통 판매 정보와 상세 정보를 함께 받는다.
- request serializer는 `images`, `drink_info`, `package_info` 입력을 검증한다.
- command service는 `Product`, `ProductImage`, `Drink`, `Package`, `PackageItem` 변경을 한 transaction 안에서 오케스트레이션한다.
- view는 검증된 serializer와 command service 호출, response serializer 반환만 담당한다.

현재 한계:

- 현 스키마의 `PackageItem` 은 아직 `Drink` 기준이다.
- 같은 술 중복은 `quantity` 로 표현할 수 있지만, 패키지 안에 다른 패키지 상품을 담는 구조는 아직 아니다.
- 고객 커스텀 패키지의 product 기준 구성은 draft item 모델 추가 이후 구현한다.

이 방식의 장점:

- 기존 API를 크게 깨지 않고 write 책임을 service로 이동할 수 있다.
- 생성/수정/삭제가 같은 command service 기준을 사용한다.
- 이미지 교체와 패키지 구성 교체가 부분 실패하지 않도록 transaction 경계를 명확히 둘 수 있다.

단점:

- request body가 커지면 `ProductUpdateSerializer` 가 공통 수정과 상세 수정을 동시에 알아야 한다.
- 장기적으로는 공통 판매 정보 수정과 상세 정보 수정 endpoint를 분리하는 편이 더 명확하다.

### 4. 상품 삭제

핵심 판단:

- 기본 삭제는 `hard delete` 가 아니라 `soft delete` 로 본다.

추천:

- `Product.status = INACTIVE`

이유:

- 주문/좋아요/리뷰/관리 이력 관점에서 안전하다.
- 운영 중 실수 복구가 쉽다.
- 참조 관계가 많은 상품 도메인에 더 자연스럽다.

단점:

- 목록 조회에서 상태 필터가 더 중요해진다.
- 완전 삭제가 필요하면 별도 정리 작업이 필요하다.

채택 이유:

- 운영 관점에서 hard delete 기본값은 너무 공격적이다.

예외:

- 테스트 데이터 정리
- 아직 외부 참조가 전혀 없는 임시 데이터 정리

## 제품 Write Path 에서 필요한 예외

예:

- `ProductAlreadyExists`
- `ProductDeletionNotAllowed`
- `InvalidBundleComposition`
- `PackagePolicyViolation`
- `ProductStatusTransitionError`

원칙:

- `ValidationError` 하나로 모든 실패를 퉁치지 않는다.
- 비즈니스 규칙 실패는 명시적인 도메인 예외 이름을 가진다.

## 지금 코드에서 바꿔야 할 부분

현재 문제:

- 고객 커스텀 패키지와 정책 모델은 아직 실제 스키마로 내려오지 않았다.
- 수량형 패키지를 표현할 수 있는 item 구조가 아직 없다.
- 상품 수정 endpoint가 아직 공통 정보와 상세 정보로 분리되어 있지는 않다.

다음 코드 리팩터링 기준:

1. `PackageItem` 또는 새 번들 item에 `quantity`, `sort_order` 개념 도입
2. `PackagePolicy` 및 허용 상품 범위 모델 추가
3. 고객 커스텀 패키지 draft/snapshot 모델 추가
4. 상품 수정 endpoint 를 공통 정보와 상세 정보 기준으로 나눌지 검토

## 커스텀 패키지 가격 규칙

결론:

- `최종 가격 = 선택한 상품 합산가 - 정책 할인`

세부 흐름:

1. 구성품 가격 합산
2. 정책 규칙 검증
3. 할인 적용
4. draft 가격 저장
5. 주문 시 snapshot 으로 고정

### 할인 정책

초기 지원안:

- `NONE`
- `FIXED_AMOUNT`
- `PERCENTAGE`

### 왜 개별 상품이 아니라 전체 패키지 할인인가

장점:

- 이벤트 운영이 쉽다.
- 계산 로직이 단순하다.
- 관리자 정책과 자연스럽게 맞는다.

단점:

- 상품별 할인 분배가 필요한 고급 정산에는 추가 계산이 필요하다.

채택 이유:

- 현재 서비스 요구사항에는 전체 번들 할인 모델이 가장 적합하다.

## 주문 snapshot 초안

주문 생성 시에는 당시 구성을 반드시 고정 저장한다.

### 1. OrderCustomPackage

예상 필드:

- `order`
- `package_policy_name`
- `display_name`
- `base_price`
- `discount_amount`
- `final_price`
- `pickup_store`
- `pickup_day`
- `pickup_status`
- `is_tasting_selected`

### 2. OrderCustomPackageItem

예상 필드:

- `order_custom_package`
- `product`
- `product_name`
- `price`
- `quantity`
- `sort_order`

원칙:

- 주문 시점 이후 원본 drink/product/template 이 바뀌어도 주문 데이터는 보존되어야 한다.

현재 코드 적용:

- `orders.OrderCustomPackage` 와 `orders.OrderCustomPackageItem` 으로 구현한다.
- 주문 생성 시 일반 상품 `OrderItem` 과 커스텀 패키지 snapshot을 같은 transaction 안에서 생성한다.
- 주문 총액은 일반 장바구니 상품 합계와 draft 최종가를 함께 합산한다.
- 주문 이후 원본 draft는 `ORDERED` 상태로 남겨 추적 가능하게 둔다.

## 책임 분리 기준

### products 가 소유하는 것

- 카탈로그 상품
- 고정 번들
- 패키지 정책
- 패키지 정책 허용 상품
- 시음 정책

### cart 가 소유하는 것

- 장바구니
- 장바구니 일반 상품 항목
- 패키지 draft
- 패키지 draft item

### orders 가 소유하는 것

- 주문
- 주문 상품 항목
- 커스텀 패키지 snapshot
- 커스텀 패키지 snapshot item
- 시음 선택 snapshot

## 운영 시나리오 정리

### 관리자

- 단일 상품 등록
- 고정 패키지 등록
- 패키지 정책 생성/수정/비활성화
- 패키지별 정책 고정 관리
- 상품/패키지의 시음 가능 여부 설정
- 정책에서 draft 시음 허용 여부 설정

### 고객

- 카탈로그 상품 조회
- policy 를 선택해 패키지 draft 생성
- 같은 상품을 다시 담으면 row 추가가 아니라 `quantity` 증가
- 정책에 따라 중복 허용/금지 적용
- 장바구니 안에서 여러 개 draft 동시 보유
- 단일 제품, 고정 패키지, 고객 draft 모두 시음 선택 가능
- 주문 시 snapshot 으로 고정

## 지금 구조에서 바꿔야 할 핵심

현재 구조의 핵심 문제:

- `Product` 가 `drink` 와 `package` 를 직접 참조한다.
- 시음을 상품 타입으로 표현하려 하면 구조가 더 쉽게 꼬인다.

권장 변경:

- `Product.drink` 제거 방향
- `Product.package` 제거 방향
- `SingleProduct`, `BundleProduct` 로 상세 분리
- 패키지 정책과 시음 옵션 설정 정리

장점:

- 제품 타입별 책임이 명확해진다.
- serializer/service 분기가 줄어든다.
- 시음을 간단한 옵션으로 붙이기 쉬워진다.

단점:

- 마이그레이션 비용이 있다.
- 기존 API 응답과 serializer를 손봐야 한다.

## 보류 항목

아직 확정하지 않은 것:

- `PackagePolicy` 를 products 앱 안에 둘지 별도 앱으로 둘지
- `is_tasting_available` 를 `Product` 에만 둘지, 상세 모델에서 override 를 둘지
- 주문 snapshot 에 시음 관련 값을 어디까지 저장할지
- 패키지 draft 에 별도 이미지/대표명 자동 생성이 필요한지
- 카테고리 제한 템플릿에서 허용 조건을 어떤 수준까지 일반화할지
- 재고/판매 가능 여부를 어떤 시점에 검증할지

## 현재 추천

지금 단계의 추천은 아래와 같다.

1. 카탈로그는 `Product + SingleProduct + BundleProduct + BundleProductItem`
2. 패키지 조합은 `PackagePolicy + Draft + Snapshot`
3. 같은 술은 `1 row + quantity`
4. 가격은 `합산 후 할인`
5. 시음은 별도 모델이 아니라 필드 + 정책 설정으로 시작
6. 관리자는 고정 패키지와 패키지 정책, 시음 가능 여부를 모두 관리
7. 고객은 정책 기반으로 패키지를 여러 개 생성 및 관리하고, 제품/패키지 모두 시음 선택 가능

이 문서는 현재 대화 기준 제품 모델 설계 초안이며, 이후 서비스/장바구니/주문 흐름 문서의 기준점으로 사용한다.
