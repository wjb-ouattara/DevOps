# 🐳 Todo API — Containerized DevOps Project

> A production-ready REST API built with Flask and PostgreSQL, fully containerized with Docker and orchestrated with Docker Compose.

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0.3-000000?style=for-the-badge&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white)

---

## 📋 Table of Contents

- [Description](#-description)
- [Architecture](#-architecture)
- [Technologies](#-technologies)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Environment Variables](#-environment-variables)
- [Running the Project](#-running-the-project)
- [API Documentation](#-api-documentation)
- [Docker Internals](#-docker-internals)
- [Useful Docker Commands](#-useful-docker-commands)
- [Best Practices Applied](#-best-practices-applied)
- [Troubleshooting](#-troubleshooting)
- [What I Learned](#-what-i-learned)

---

## 📌 Description

This project is a complete DevOps exercise demonstrating real-world containerization skills. It implements a Task Management REST API (To-Do List) using:

- **Flask** as a lightweight backend API
- **PostgreSQL 15** as a persistent relational database
- **Docker** to containerize each service independently
- **Docker Compose** to orchestrate and connect all services

The primary goal of this project is not the application itself, but the **infrastructure around it** — demonstrating how to think about containers, networking, data persistence, and security in a professional DevOps context.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                    HOST MACHINE                      │
│                                                      │
│   localhost:5000                                     │
│        │                                             │
│        ▼                                             │
│ ┌──────────────────────────────────────────────┐    │
│ │              Docker Network                  │    │
│ │              (app-network)                   │    │
│ │                                              │    │
│ │  ┌─────────────────┐   ┌─────────────────┐  │    │
│ │  │    backend      │   │       db        │  │    │
│ │  │  (Flask/Gunicorn│──▶│  (PostgreSQL 15)│  │    │
│ │  │   port 5000)    │   │   port 5432)    │  │    │
│ │  └─────────────────┘   └────────┬────────┘  │    │
│ │                                  │           │    │
│ └──────────────────────────────────┼───────────┘    │
│                                    │                 │
│                           ┌────────▼────────┐       │
│                           │  postgres_data  │       │
│                           │    (volume)     │       │
│                           └─────────────────┘       │
└─────────────────────────────────────────────────────┘
```

**Service communication:** The backend connects to PostgreSQL using the service name `db` as hostname — Docker's internal DNS resolves this automatically within the shared network.

---

## 🛠️ Technologies

| Technology | Version | Role |
|---|---|---|
| Python | 3.11-slim | Backend runtime |
| Flask | 3.0.3 | REST API framework |
| Gunicorn | 21.2.0 | Production WSGI server |
| psycopg2-binary | 2.9.11 | PostgreSQL adapter |
| PostgreSQL | 15 | Relational database |
| Docker | Latest | Containerization |
| Docker Compose | v2 | Multi-container orchestration |

---

## 📁 Project Structure

```
todo-app/
├── .dockerignore          # Excludes unnecessary files from build context
├── .env                   # Environment variables (not committed to Git)
├── .env.example           # Template for environment variables
├── .gitignore             # Excludes sensitive files from Git
├── docker-compose.yml     # Orchestrates all services
└── backend/
    ├── .dockerignore      # Backend-specific build exclusions
    ├── Dockerfile         # Backend image build instructions
    ├── app.py             # Flask application
    └── requirements.txt   # Python dependencies (pinned versions)
```

---

## ✅ Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- [Git](https://git-scm.com/) installed
- No Python or PostgreSQL installation required — everything runs inside containers

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/todo-app.git
cd todo-app
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_USER=admin
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=todo_db
```

> ⚠️ Never commit `.env` to Git. It is listed in `.gitignore`.

---

## 🔐 Environment Variables

| Variable | Description | Example |
|---|---|---|
| `POSTGRES_HOST` | Database hostname (Docker service name) | `db` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_USER` | Database user | `admin` |
| `POSTGRES_PASSWORD` | Database password | `secret` |
| `POSTGRES_DB` | Database name | `todo_db` |

**Why `POSTGRES_HOST=db`?**
Docker Compose creates an internal DNS for each service. The backend container resolves `db` directly to the PostgreSQL container's IP — no hardcoded IPs needed.

---

## ▶️ Running the Project

### Start all services

```bash
docker compose up --build
```

### Start in background (detached mode)

```bash
docker compose up -d --build
```

### Stop all services (preserves data)

```bash
docker compose down
```

### Stop all services and delete data

```bash
docker compose down -v
```

Once running, the API is available at: `http://localhost:5000`

---

## 📡 API Documentation

### `GET /health`

Health check endpoint. Verifies the backend is running.

```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "ok"
}
```

---

### `GET /tasks`

Retrieves all tasks from the database.

```bash
curl http://localhost:5000/tasks
```

**Response:**
```json
[
  { "id": 1, "title": "Learn Docker" },
  { "id": 2, "title": "Deploy to production" }
]
```

---

### `POST /tasks`

Creates a new task. Requires a JSON body with a `title` field.

```bash
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn Docker Compose"}'
```

**Response (`201 Created`):**
```json
{
  "id": 1,
  "title": "Learn Docker Compose"
}
```

**Error response (`400 Bad Request`):**
```json
{
  "error": "Task must have a title"
}
```

---

## 🐳 Docker Internals

### Image Layers & Cache Optimization

The Dockerfile is structured to maximize Docker's layer cache:

```dockerfile
# Step 1: Dependencies (rarely change) → cached
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 2: Application code (changes often) → rebuilt only when needed
COPY . .
```

This means when only `app.py` changes, pip does **not** reinstall all packages — saving minutes per build.

### Internal Network & DNS

```yaml
networks:
  app-network:
```

All services share `app-network`. Docker provides automatic DNS resolution — `db` resolves to the PostgreSQL container's internal IP. No manual IP configuration needed.

### Volume & Data Persistence

```yaml
volumes:
  postgres_data:
    /var/lib/postgresql/data
```

PostgreSQL stores data in `/var/lib/postgresql/data` inside its container. By mounting a named volume here, data survives container restarts and `docker compose down`. Only `docker compose down -v` will delete it.

### Healthcheck & Dependency Management

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U admin -d todo_db"]
  interval: 5s
  timeout: 5s
  retries: 5
```

`depends_on` alone only waits for the container to **start**, not for PostgreSQL to be **ready**. The healthcheck ensures the backend starts only when the database is genuinely accepting connections.

---

## 💻 Useful Docker Commands

```bash
# Build and start all services
docker compose up --build

# Start in background
docker compose up -d

# View logs for all services
docker compose logs

# View logs for a specific service (live)
docker compose logs -f backend

# View last 20 log lines
docker compose logs backend --tail=20

# Check container status
docker compose ps

# Enter a running container
docker exec -it todo-backend bash

# Restart a specific service
docker compose restart backend

# Stop without deleting volumes
docker compose down

# Stop and delete all data
docker compose down -v

# Check Docker images
docker images

# Remove unused images
docker image prune
```

---

## 🔒 Best Practices Applied

### 1. Stateless Backend
The Flask API holds no application state in memory. All data is persisted in PostgreSQL. This means the backend container can be restarted, scaled, or replaced with zero data loss.

### 2. Environment Variable Separation
No credentials are hardcoded in source code or Docker images. All sensitive values live in `.env`, which is excluded from both Git (`.gitignore`) and Docker build context (`.dockerignore`).

### 3. Optimized Docker Image
- Uses `python:3.11-slim` instead of full Python image (~50MB vs ~1GB)
- `--no-cache-dir` removes pip's download cache from the image layer
- `.dockerignore` excludes `.venv`, `__pycache__`, `.idea` from build context

### 4. Production WSGI Server
The app runs with **Gunicorn** instead of Flask's development server (`python app.py`). Gunicorn handles multiple concurrent workers, automatic worker restarts, and production-grade request handling.

### 5. Resilient Database Connection
The backend implements a retry mechanism with a maximum attempt limit:

```python
def get_db_connection(max_retries=10):
    for attempt in range(max_retries):
        try:
            return psycopg2.connect(...)
        except Exception:
            time.sleep(2)
    raise Exception("Database unreachable after max retries")
```

### 6. Per-Request Database Connections
Each API request opens and closes its own database connection — avoiding shared state across Gunicorn workers and preventing stale connection issues.

---

## 🔧 Troubleshooting

### Backend can't connect to database

**Symptom:** `psycopg2.OperationalError: could not connect to server`

**Cause:** Backend started before PostgreSQL was ready.

**Solution:** The healthcheck + `condition: service_healthy` handles this automatically. If it still occurs:
```bash
docker compose logs db
docker compose restart backend
```

---

### Port 5000 already in use

**Symptom:** `Error: bind: address already in use`

**Solution:**
```bash
# Find and kill the process using port 5000
lsof -i :5000
kill -9 <PID>
```

---

### Data not persisting after restart

**Symptom:** Database is empty after `docker compose down` + `docker compose up`

**Cause:** You may have used `docker compose down -v` which deletes volumes.

**Solution:** Use `docker compose down` (without `-v`) to preserve data.

---

### `version` attribute warning in Docker Compose

**Symptom:**
```
the attribute `version` is obsolete, it will be ignored
```

**Solution:** Remove the `version: "3.9"` line from `docker-compose.yml`. It is no longer required in Compose V2.

---

## 🧠 What I Learned

This project was built as part of an intensive DevOps learning path. Key takeaways:

**Containers vs VMs**
Containers share the host kernel — they are not mini virtual machines. This makes them lightweight and fast, but it means a Linux container cannot run natively on a Windows kernel without a virtualization layer.

**Docker Layer Cache**
The order of instructions in a Dockerfile directly impacts build performance. Dependencies that change rarely must be installed before copying application code, so Docker can cache the expensive `pip install` step.

**Ephemeral Containers + Persistent Volumes**
Containers are disposable by design. Any data written to a container's filesystem is lost when the container is removed. Volumes decouple data lifecycle from container lifecycle — critical for databases.

**Internal DNS in Docker Networks**
Docker Compose creates a private network for each project. Service names act as hostnames within that network. The backend reaches PostgreSQL at `db:5432` — no IP addresses, no manual configuration.

**`depends_on` is not enough**
Defining service start order does not guarantee service readiness. A PostgreSQL container can be "started" but not yet accepting connections. Healthchecks + `condition: service_healthy` solve this correctly.

**Security starts at development**
`.env` files must never enter Git history. Even after deletion, secrets remain recoverable from Git history. A `.env.example` file communicates required variables without exposing values.

---

## 👤 Author

**Wahon**
DevOps Engineer in Training
[GitHub](https://github.com/your-username) · [LinkedIn](https://linkedin.com/in/your-profile)

---

*Built as part of an intensive hands-on DevOps curriculum — every decision in this project was made intentionally and documented above.*
