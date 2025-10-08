# Distributed Shop – Cloud‑Native Microservices Demo (2025)

**Stack:** FastAPI, PostgreSQL, SQLAlchemy, Redis, Celery, Docker Compose, REST

This repository demonstrates a production‑style microservices system with:
- **API Gateway** (FastAPI) routing requests to **User Service** and **Order Service**
- **User Service** (FastAPI + SQLAlchemy + PostgreSQL)
- **Order Service** (FastAPI + SQLAlchemy + PostgreSQL + Celery background worker via Redis)
- **Asynchronous order processing** with Celery/Redis (non‑blocking API)
- **Docker Compose one‑command** local deployment
- Health checks (`/healthz`) and simple **horizontal scaling** examples

> ⚡️ TL;DR: `docker compose up --build` then open:  
> - Gateway docs: http://localhost:8080/docs  
> - User service (direct): http://localhost:8001/docs  
> - Order service (direct): http://localhost:8002/docs  
> - Flower (Celery dashboard): http://localhost:5555

---

## Architecture

```
             ┌────────────────────────┐
             │      API Gateway       │  ← FastAPI reverse proxy / router
             │ http://localhost:8080  │
             └──────────┬─────────────┘
                        │
        ┌───────────────┼───────────────┐
        │                               │
┌───────▼────────┐               ┌──────▼────────┐
│  User Service  │               │ Order Service │
│  :8001         │               │  :8002        │
│ PostgreSQL     │               │ PostgreSQL    │
└───────┬────────┘               └──────┬────────┘
        │                                 │
        └────────►   Redis ◄──────────────┘
                     (Celery broker/backend)
```

- **User Service** owns user data.  
- **Order Service** owns order data. `POST /orders` enqueues a Celery task that simulates payment/fulfillment and marks the order `processed` asynchronously.

Each service has its own schema (separate ownership) in a single PostgreSQL instance for simplicity. You can split databases per service later if desired.

---

## Quick Start

1) **Prereqs:** Docker & Docker Compose installed.

2) **Launch:**
```bash
docker compose up --build
```
First run will create DB schemas/tables and start Celery worker & Flower.

3) **Explore:**
- Gateway OpenAPI: http://localhost:8080/docs
- User service OpenAPI: http://localhost:8001/docs
- Order service OpenAPI: http://localhost:8002/docs
- Flower (Celery UI): http://localhost:5555

4) **Smoke Test via Gateway:**

Create a user:
```bash
curl -s -X POST http://localhost:8080/users \
  -H 'Content-Type: application/json' \
  -d '{"email":"alice@example.com","full_name":"Alice"}'
```

List users:
```bash
curl -s http://localhost:8080/users
```

Create an order (async processing):
```bash
curl -s -X POST http://localhost:8080/orders \
  -H 'Content-Type: application/json' \
  -d '{"user_id":1,"item":"Pro Keyboard","quantity":2}'
```

Check order status:
```bash
curl -s http://localhost:8080/orders/1
```

See Celery task progress in Flower: http://localhost:5555

---

## Horizontal Scaling (local)

- Scale **Order Service** API replicas:
```bash
docker compose up --build --scale order-service=2
```
- Scale **Celery workers**:
```bash
docker compose up --build --scale order-worker=4
```

> The gateway uses simple round‑robin via Docker DNS across replicas (best‑effort in dev). For production consider a dedicated API gateway/reverse proxy (e.g. Envoy, Nginx, Traefik) with proper load‑balancing, retries, timeouts, and auth.

---

## Services & Endpoints

### Gateway (port 8080)
- `GET /healthz`
- Proxies:
  - `/users*` → User Service
  - `/orders*` → Order Service

### User Service (port 8001)
- `GET /healthz`
- `POST /users` — create user
- `GET /users` — list users
- `GET /users/{id}` — get user by id

### Order Service (port 8002)
- `GET /healthz`
- `POST /orders` — create order (enqueues Celery task, returns pending order)
- `GET /orders` — list orders
- `GET /orders/{id}` — get order by id

---

## Local Development

- Hot‑reload enabled via `uvicorn --reload` in dev config.
- SQLAlchemy auto‑creates tables on startup (demo). For real projects, add Alembic migrations.
- Environment variables are set via `docker-compose.yml` and `.env` (optional).

---

## Project Layout

```
.
├─ api-gateway/
│  ├─ app.py
│  ├─ requirements.txt
│  └─ Dockerfile
├─ user-service/
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ db.py
│  │  ├─ models.py
│  │  ├─ schemas.py
│  │  └─ crud.py
│  ├─ requirements.txt
│  └─ Dockerfile
├─ order-service/
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ db.py
│  │  ├─ models.py
│  │  ├─ schemas.py
│  │  ├─ crud.py
│  │  ├─ celery_app.py
│  │  └─ tasks.py
│  ├─ requirements.txt
│  └─ Dockerfile
├─ docker-compose.yml
├─ db/
│  └─ init.sql   # creates service-owned schemas
└─ .env.example
```

---

## Notes & Best Practices

- Each service owns its data model; APIs are the only integration surface.
- Use **health checks** and **readiness** probes in real orchestration (K8s).
- Replace the simple Gateway with a production API gateway for auth/rate‑limit.
- Add tracing/metrics (OpenTelemetry, Prometheus) for observability.
- Use Alembic migrations for schema evolution.

---

## License

MIT
