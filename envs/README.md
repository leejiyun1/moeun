# Local Environment

Copy the example files when setting up a new machine:

```sh
cp envs/frontend.local.env.example envs/frontend.local.env
cp envs/backend.local.env.example envs/backend.local.env
```

## Frontend

`VITE_API_URL=/api/v1` is the local default. It works through nginx on
`http://localhost` and through the Vite dev proxy on `http://localhost:5173`.

`DEV_PROXY_TARGET=http://backend:8000` is used only by Vite dev server inside
Docker. If you run the frontend directly on the host machine, use:

```env
DEV_PROXY_TARGET=http://localhost:8000
```

OAuth redirect URI values must match the values registered in each provider
console and must also match the backend redirect URI values.

## Backend

Keep provider secret values server-side only:

- `NAVER_CLIENT_SECRET`
- `GOOGLE_CLIENT_SECRET`
- `TOSS_PAYMENTS_SECRET_KEY`
- `EMAIL_APP_PASSWORD`
- `NCLOUD_SECRET_ACCESS_KEY`

Do not add these values to frontend `VITE_` variables.
