<div align="center">

# 🎙️ VoiceSplit

![Build](https://img.shields.io/github/actions/workflow/status/your-org/voicesplit/ci.yml?branch=main&style=for-the-badge&label=BUILD&color=06D6CF)
![License](https://img.shields.io/badge/LICENSE-MIT-3B82F6?style=for-the-badge)
![Version](https://img.shields.io/badge/VERSION-1.0.0-06D6CF?style=for-the-badge)
![Python](https://img.shields.io/badge/PYTHON-3.11-3B82F6?style=for-the-badge&logo=python&logoColor=white)
![Next.js](https://img.shields.io/badge/NEXT.JS-14-06D6CF?style=for-the-badge&logo=next.js&logoColor=white)

<img src="frontend/public/logo.png" alt="VoiceSplit Logo" width="180" />

### Choose the voice that matters to you.

AI-powered speaker isolation and diarization platform — extract, separate, and export individual speakers from any audio or video file with production grade accuracy.

</div>

---

## ✨ Features

| Icon | Feature | Description |
|------|---------|-------------|
| 🔊 | **Speaker Isolation** | Cleanly separate up to 8 simultaneous speakers |
| 🧠 | **AI Diarization** | Pyannote 3.1 speaker detection with timestamp precision |
| ⚡ | **Async Processing** | Celery workers handle long jobs without blocking |
| 📤 | **Multi-format Export** | WAV, MP3, FLAC per speaker or merged |
| 🔐 | **OAuth Authentication** | Google SSO via NextAuth.js |
| ☁️ | **S3-compatible Storage** | MinIO for local dev, AWS S3 for production |
| 📊 | **Real-time Updates** | WebSocket progress streaming per job |
| 💳 | **Stripe Billing** | Usage-based billing (opt-in) |

---

## 🏗️ Architecture

```
                        ┌─────────────────────────────────────────────────────┐
                        │                  Docker Network                      │
                        │                 voicesplit_network                   │
                        │                                                       │
   Browser             │  ┌──────────┐    ┌──────────┐    ┌───────────────┐  │
      │                │  │          │    │ FastAPI  │    │ Celery Worker │  │
      │   HTTP/WS      │  │  Nginx   │───▶│  :8000   │───▶│               │  │
      └───────────────▶│  │ :80/:443 │    │          │    │  AI Pipeline  │  │
                        │  │          │    └────┬─────┘    │  ─────────── │  │
                        │  │          │         │           │  1. Demux    │  │
                        │  │          │    ┌────▼─────┐    │  2. Separate │  │
                        │  │          │───▶│ Next.js  │    │  3. Diarize  │  │
                        │  │          │    │  :3000   │    │  4. Export   │  │
                        │  └──────────┘    └──────────┘    └──────┬────── ┘  │
                        │                                          │           │
                        │  ┌──────────┐  ┌──────────┐  ┌─────────▼────────┐  │
                        │  │PostgreSQL│  │  Redis   │  │     MinIO        │  │
                        │  │  :5432   │  │  :6379   │  │  :9000 / :9001   │  │
                        │  └──────────┘  └──────────┘  └──────────────────┘  │
                        └─────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Frontend** | Next.js, TypeScript, Tailwind CSS, NextAuth.js | 14 / 3 / 3.4 |
| **Backend** | FastAPI, SQLAlchemy, Alembic, Pydantic v2 | 0.111 / 2.x |
| **AI / ML** | Pyannote Audio, Demucs, HuggingFace Hub | 3.1 / 4.x |
| **Queue** | Celery, Redis | 5.x / 7 |
| **Database** | PostgreSQL | 15 |
| **Storage** | MinIO (local) / AWS S3 (production) | Latest |
| **Proxy** | Nginx | 1.25 |
| **Containers** | Docker, Docker Compose | v2 |

---

## 📋 Prerequisites

| Requirement | Minimum Version | Notes |
|-------------|----------------|-------|
| Docker Engine | 24.x | [Install Docker](https://docs.docker.com/engine/install/) |
| Docker Compose | v2.20 | Bundled with Docker Desktop |
| Node.js | 20 LTS | Only needed for local frontend dev |
| Python | 3.11 | Only needed for local backend dev |
| FFmpeg | 6.x | Bundled in Docker; needed for local dev |
| HuggingFace account | — | Free; needed for model token |

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-org/voicesplit.git
cd voicesplit
```

### 2. Configure environment

```bash
cp .env.example .env
```

Open `.env` and fill in the required values:

- `SECRET_KEY` — generate with `openssl rand -hex 32`
- `NEXTAUTH_SECRET` — generate with `openssl rand -hex 32`
- `HF_TOKEN` — from [HuggingFace Settings](https://huggingface.co/settings/tokens)
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` — from [Google Cloud Console](https://console.cloud.google.com/)

### 3. Add your logo

```bash
cp /path/to/your/logo.png frontend/public/logo.png
```

### 4. Start all services

```bash
docker compose up -d
```

Wait for all health checks to pass (approximately 60 seconds):

```bash
docker compose ps
```

### 5. Run database migrations

```bash
docker compose exec backend alembic upgrade head
```

### 6. Create the MinIO bucket

Open the MinIO Console at **http://localhost:9001** and log in with the `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` values from your `.env`. Create a bucket named `voicesplit` (or the value you set for `MINIO_BUCKET`).

### 7. Open the application

Navigate to **http://localhost:3000**.

---

## 🔑 Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `ENVIRONMENT` | Runtime environment | No | `development` |
| `SECRET_KEY` | JWT signing secret | **Yes** | — |
| `CORS_ORIGINS` | Allowed CORS origins (JSON array) | No | `["http://localhost:3000"]` |
| `POSTGRES_USER` | PostgreSQL username | **Yes** | — |
| `POSTGRES_PASSWORD` | PostgreSQL password | **Yes** | — |
| `POSTGRES_DB` | PostgreSQL database name | **Yes** | — |
| `DATABASE_URL` | Full SQLAlchemy connection URL | **Yes** | — |
| `REDIS_URL` | Redis connection URL | **Yes** | `redis://redis:6379/0` |
| `STORAGE_BACKEND` | `minio` or `s3` | No | `minio` |
| `MINIO_ENDPOINT` | MinIO host:port | Conditional | `minio:9000` |
| `MINIO_ROOT_USER` | MinIO root username | Conditional | — |
| `MINIO_ROOT_PASSWORD` | MinIO root password | Conditional | — |
| `MINIO_BUCKET` | Storage bucket name | **Yes** | `voicesplit` |
| `HF_TOKEN` | HuggingFace API token | **Yes** | — |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | **Yes** | — |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | **Yes** | — |
| `BILLING_ENABLED` | Enable Stripe billing | No | `false` |
| `STRIPE_SECRET_KEY` | Stripe secret key | Conditional | — |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | Conditional | — |
| `NEXTAUTH_URL` | Public URL of the Next.js app | **Yes** | `http://localhost:3000` |
| `NEXTAUTH_SECRET` | NextAuth.js secret | **Yes** | — |
| `NEXT_PUBLIC_API_URL` | Public REST API base URL | **Yes** | `http://localhost:8000` |
| `NEXT_PUBLIC_WS_URL` | Public WebSocket base URL | **Yes** | `ws://localhost:8000` |

---

## 🧠 AI Pipeline

Each audio job passes through four sequential stages managed by the Celery worker:

```
Upload ──▶ 1. Demux ──▶ 2. Source Separation ──▶ 3. Diarization ──▶ 4. Export
             │                │                        │                  │
          FFmpeg           Demucs 4                Pyannote 3.1       WAV/MP3/
          extract          HTDemucs               speaker labels       FLAC
          audio            model                  + timestamps        per speaker
```

| Stage | Tool | Description |
|-------|------|-------------|
| **1. Demux** | FFmpeg | Extracts audio track from video; converts to 16 kHz mono WAV |
| **2. Source Separation** | Demucs `htdemucs` | Separates stems (vocals, drums, bass, other) |
| **3. Diarization** | Pyannote 3.1 | Identifies and timestamps each unique speaker |
| **4. Export** | FFmpeg | Slices segments per speaker and encodes to requested format |

Progress is streamed to the frontend via WebSocket at `/ws/job/{job_id}`.

---

## 📖 API Documentation

The FastAPI backend auto-generates interactive API docs:

| Interface | URL |
|-----------|-----|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| OpenAPI JSON | http://localhost:8000/openapi.json |

All endpoints under `/api/v1/` require a Bearer token obtained via the `/api/v1/auth/` routes.

---

## 💻 Development

### Backend (FastAPI) — without Docker

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend (Next.js) — without Docker

```bash
cd frontend
npm ci
npm run dev
```

### Run tests

```bash
# Backend
cd backend && pytest --cov=app -q

# Frontend
cd frontend && npm run lint && npm run build
```

### Start Celery worker locally

```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=info --concurrency=2
```

---

## 📁 Folder Structure

```
voicesplit/
├── .github/
│   └── workflows/
│       ├── ci.yml              # Continuous integration
│       └── deploy.yml          # Production deployment
├── backend/
│   ├── alembic/                # Database migrations
│   │   └── versions/
│   ├── app/
│   │   ├── api/                # FastAPI route handlers
│   │   ├── core/               # Config, security, deps
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/           # Business logic
│   │   ├── workers/            # Celery tasks & celery_app
│   │   └── main.py             # FastAPI application entry point
│   ├── tests/
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/
│   ├── public/
│   │   └── logo.png            # Brand logo (add manually)
│   ├── src/
│   │   ├── app/                # Next.js App Router pages
│   │   ├── components/         # Reusable UI components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── lib/                # Utilities, API client
│   │   └── types/              # TypeScript type definitions
│   ├── next.config.js
│   └── package.json
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── worker.Dockerfile
├── nginx/
│   └── nginx.conf
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Commit changes following [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `chore:`
4. Push the branch: `git push origin feat/my-feature`
5. Open a Pull Request targeting `develop`

All PRs must pass CI (tests + lint + Docker build) before merging.

---

## 📜 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---

<div align="center">
Built with ❤️ by the VoiceSplit team · <a href="https://github.com/your-org/voicesplit/issues">Report an Issue</a>
</div>
