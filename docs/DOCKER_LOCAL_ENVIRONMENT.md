# Docker Local Environment

## 목적

프론트엔드와 백엔드를 루트 monorepo 기준으로 한 번에 실행하기 위한 로컬 Docker 기준이다.

현재 단계의 목표는 운영 배포가 아니라, 개발자가 같은 환경에서 FE/BE/DB/Redis를 안정적으로 띄우는 것이다. 추후 production에서는 DB 컨테이너를 띄우지 않고 cloud DB를 바라보게 한다.

## 로컬 구성

```text
docker-compose.local.yml

frontend
- ExcellentFE
- Vite dev server
- http://localhost:5173
- VITE_API_URL=http://localhost:8000/api/v1

backend
- EasyBE
- Django dev server
- http://localhost:8000
- DB_HOST=db
- REDIS_HOST=redis

db
- Postgres
- local Docker volume

redis
- Redis
- local Docker volume
```

## 실행 파일

- `docker-compose.local.yml`: 로컬 통합 실행 기준
- `EasyBE/Dockerfile.dev`: 백엔드 개발 컨테이너
- `ExcellentFE/Dockerfile.dev`: 프론트엔드 개발 컨테이너
- `envs/backend.local.env`: 로컬 백엔드 실제 환경 변수, Git 제외
- `envs/frontend.local.env`: 로컬 프론트 실제 환경 변수, Git 제외
- `envs/backend.local.env.example`: 백엔드 env 예시, Git 포함
- `envs/frontend.local.env.example`: 프론트 env 예시, Git 포함

## 실행

```bash
docker compose -f docker-compose.local.yml up --build
```

백그라운드 실행:

```bash
docker compose -f docker-compose.local.yml up --build -d
```

종료:

```bash
docker compose -f docker-compose.local.yml down
```

DB volume까지 제거:

```bash
docker compose -f docker-compose.local.yml down -v
```

## 환경 분리 원칙

로컬 Docker는 항상 local/dev DB만 바라본다.

```text
local Docker -> local Postgres container
dev/staging server -> dev/staging cloud DB
production server -> production cloud DB
```

운영 DB 접속 정보는 `backend.local.env`에 넣지 않는다.

## 추후 production 전환

production compose에서는 아래를 원칙으로 한다.

- `db` service를 두지 않는다.
- `DB_HOST`는 cloud DB endpoint를 사용한다.
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`는 production secret으로 주입한다.
- `frontend`는 Vite dev server가 아니라 build 결과물을 nginx로 서빙한다.
- `backend`는 `runserver`가 아니라 gunicorn/uvicorn worker로 실행한다.

## 주의

- `envs/*.env`는 Git에 올리지 않는다.
- `envs/*.env.example`만 Git에 올린다.
- Docker 실행 전 production DB 주소가 local env에 들어가 있지 않은지 확인한다.
