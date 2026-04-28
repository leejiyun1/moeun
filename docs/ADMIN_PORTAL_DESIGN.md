# Admin Portal Design v1

## 문서 목적

이 문서는 Moeun의 별도 운영자 페이지를 만들기 위한 1차 설계 기준이다.

목표는 Django 기본 admin에 의존하지 않고, 운영자가 상품과 패키지 정책을 직접 관리할 수 있는 웹 화면을 만드는 것이다.

## 배경

기존 페이지는 화면 완성과 사용자 흐름 확인을 우선으로 만들었다. 실제 운영 기준에서는 아래 문제가 남아 있다.

- 운영자가 상품을 직접 등록하고 수정할 화면이 없다.
- 일반 상품과 패키지 상품을 구분해서 관리하기 어렵다.
- 시음 가능 여부, 패키지 구성 수량, 중복 허용 여부 같은 정책을 한 곳에서 보기 어렵다.
- 샘플 데이터를 넣을 수는 있지만, 운영자가 반복적으로 관리하기에는 불편하다.

최근 백엔드에서는 상품/패키지/시음 정책을 운영 기준에 맞게 정리하기 시작했다. 따라서 다음 단계는 그 구조를 사용할 수 있는 별도 관리자 화면이다.

## 1차 목표

1차 어드민은 판매 전체 운영 시스템이 아니라, 상품 운영을 위한 최소 관리자 페이지로 잡는다.

포함 범위:

- 관리자 전용 라우트
- 상품 목록 조회
- 상품 상태 확인 및 비활성화
- 일반 상품 등록
- 패키지 상품 등록
- 패키지 정책 목록 조회
- 패키지 정책 등록/수정/비활성화
- 패키지 구성용 술 목록 조회
- 시음 가능 여부 확인/설정

제외 범위:

- 결제 관리
- 배송 관리
- 픽업 예약 관리
- 주문 운영 대시보드
- 후기 검수/블라인드
- 통계 대시보드
- 권한 세분화
- 이미지 파일 직접 업로드

## 사용자

1차 사용자는 내부 운영자 1명 또는 소수 관리자다.

권한 기준:

- 일반 사용자는 접근 불가
- 관리자 권한 사용자만 접근 가능
- 백엔드 관리 API도 단순 로그인 여부가 아니라 관리자 권한을 확인해야 한다.
- 외부 헤더에는 관리자 메뉴를 노출하지 않는다.
- 로그인한 관리자에게만 마이페이지 내부에서 관리자 메뉴를 노출한다.
- `/admin` 직접 접근도 가능하지만, 관리자 권한이 없으면 차단한다.

현재 주의점:

- 일부 관리 API가 `IsAuthenticated` 또는 `AllowAny` 수준으로 열려 있다.
- 별도 어드민 페이지 구현 전, 관리 API 권한을 관리자 전용으로 보강해야 한다.

## 화면 구조

권장 라우트:

```text
/admin
/admin/products
/admin/products/new
/admin/products/:id
/admin/packages/new
/admin/package-policies
/admin/package-policies/new
/admin/package-policies/:id
```

진입 방식:

- 1차 진입구는 마이페이지 내부 관리자 메뉴다.
- 해당 메뉴는 `user.role === ADMIN` 인 경우에만 노출한다.
- `/admin` URL을 직접 입력해도 보호 라우트에서 관리자 권한을 다시 확인한다.
- 일반 사용자에게는 외부 헤더나 공개 화면에서 관리자 메뉴를 보여주지 않는다.

1차에서는 화면 수를 줄이기 위해 아래처럼 시작해도 된다.

```text
/admin/products
/admin/products/new
/admin/package-policies
```

## 기능 기준

### 상품 목록

목적:

- 운영자가 현재 등록된 상품을 확인한다.

필요 정보:

- 상품명
- 상품 타입
- 가격
- 할인
- 상태
- 시음 가능 여부
- 생성일

필터:

- 상태
- 상품 타입
- 검색어

### 일반 상품 등록

목적:

- 하나의 술을 판매 상품으로 등록한다.

필요 정보:

- 술 기본 정보
- 양조장
- 가격/할인
- 설명
- 이미지 URL
- 상품 특성
- 시음 가능 여부

### 패키지 상품 등록

목적:

- 여러 술을 묶은 고정 패키지를 등록한다.

필요 정보:

- 패키지명
- 패키지 구성 술
- 구성별 수량
- 패키지 정책
- 가격/할인
- 설명
- 이미지 URL
- 시음 가능 여부

### 패키지 정책 관리

목적:

- 패키지 구성 규칙을 운영자가 관리한다.

필요 정보:

- 정책명
- 최소 구성 수량
- 최대 구성 수량
- 중복 허용 여부
- 허용 상품 범위
- 허용 상품 목록
- 할인 방식
- 할인 값
- 상태

## API 계약

현재 사용할 수 있는 백엔드 API:

```text
GET  /api/v1/products/manage/
GET  /api/v1/products/{id}/manage/
PATCH /api/v1/products/{id}/manage/
DELETE /api/v1/products/{id}/manage/

POST /api/v1/products/individual/create/
POST /api/v1/products/package/create/

GET  /api/v1/drinks/for-package/

GET  /api/v1/package-policies/manage/
POST /api/v1/package-policies/manage/
GET  /api/v1/package-policies/{id}/manage/
PATCH /api/v1/package-policies/{id}/manage/
DELETE /api/v1/package-policies/{id}/manage/
```

보강 필요:

- 관리 API 권한을 관리자 전용으로 제한
- 일반 상품 생성 API가 `AllowAny` 인 부분 수정
- 양조장/술 등록 흐름이 실제 어드민 화면에서 충분한지 확인
- 이미지 URL 입력 방식과 향후 파일 업로드 전환 계획 정리

## 프론트 구조

권장 구조:

```text
src/pages/admin/
src/components/admin/
src/hooks/admin/
src/api/admin/
src/types/admin/
```

규칙:

- `pages/admin` 은 화면 조합만 담당한다.
- API 호출은 `src/api/admin` 으로 모은다.
- React Query query key는 admin 도메인 기준으로 중앙화한다.
- 폼 기본값과 선택지는 상수로 분리한다.
- 상품 등록 폼은 일반 상품과 패키지 상품의 공통 필드를 공유하되, 타입별 상세 필드는 분리한다.

## 백엔드 구조

1차에서는 기존 products 관리 API를 사용한다.

다만 운영 공개 전에는 아래를 먼저 보강한다.

- 관리자 권한 permission 추가
- 관리 API 권한 통일
- schema 경고 정리
- request/response serializer 분리 검토
- 상품 생성/수정 API의 에러 응답 형식 정리

## 구현 순서

1. 관리 API 권한 보강
2. 프론트 admin 보호 라우트 추가
3. 관리자에게만 마이페이지 내부 관리자 메뉴 노출
4. admin 레이아웃 추가
5. admin API client와 타입 정의
6. 상품 목록 화면
7. 패키지 정책 목록/생성 화면
8. 일반 상품 등록 화면
9. 패키지 상품 등록 화면
10. 검증 및 문서 갱신

## 완료 기준

- 일반 사용자가 admin 화면과 관리 API에 접근할 수 없다.
- 운영자가 상품 목록을 볼 수 있다.
- 운영자가 일반 상품을 등록할 수 있다.
- 운영자가 패키지 정책을 등록/수정할 수 있다.
- 운영자가 패키지 상품을 등록할 수 있다.
- 등록된 상품이 일반 사용자 페이지에서 조회된다.
- `lint`, `build`, 관련 백엔드 테스트가 통과한다.

## 보류 항목

- 이미지 파일 업로드
- 주문/배송/픽업 운영 관리
- 후기 검수
- 상세 통계
- 다중 관리자 권한 체계
- 운영 감사 로그
