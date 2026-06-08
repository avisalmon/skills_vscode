---
name: docker-basics
description: >
  Run, build, and manage Docker containers. Write Dockerfiles for Python/Django
  apps. Use docker-compose for multi-service local dev stacks (web + db + redis).
  Push/pull images from Docker Hub. Manage volumes, networks, and environment
  variables. TRIGGER: user says "docker", "container", "dockerfile", "docker-compose",
  "docker run", "docker build", "containerize", "spin up a container", or
  "docker image".
---

# Docker Basics — Containers, Images & Compose

> **Purpose**: Package, run, and ship applications using Docker containers.
> Works on Windows (Docker Desktop), Linux, and macOS.

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Core Concepts](#core-concepts)
3. [Docker CLI Essentials](#docker-cli-essentials)
4. [Writing Dockerfiles](#writing-dockerfiles)
5. [Docker Compose](#docker-compose)
6. [Volumes & Persistence](#volumes--persistence)
7. [Networking](#networking)
8. [Environment Variables & Secrets](#environment-variables--secrets)
9. [Common App Recipes](#common-app-recipes)
10. [Intel Proxy Setup](#intel-proxy-setup)
11. [Troubleshooting](#troubleshooting)
12. [Lessons Learned](#lessons-learned)

---

## Quick Reference

```powershell
# Run a container (download + start)
docker run hello-world
docker run -it ubuntu bash          # interactive terminal
docker run -d -p 8080:80 nginx      # detached, port mapping

# Build an image from Dockerfile in current dir
docker build -t myapp:latest .

# List running containers
docker ps
docker ps -a                        # including stopped

# Stop / remove
docker stop <container_id>
docker rm <container_id>

# List images
docker images

# Remove image
docker rmi myapp:latest

# Logs
docker logs <container_id>
docker logs -f <container_id>       # follow (like tail -f)

# Exec into running container
docker exec -it <container_id> bash

# Docker Compose
docker compose up -d                # start all services, detached
docker compose down                 # stop and remove containers
docker compose logs -f              # follow all service logs
docker compose ps                   # service status
```

---

## Core Concepts

| Term | Meaning |
|------|---------|
| **Image** | Read-only template (like a snapshot). Built from a `Dockerfile`. |
| **Container** | A running instance of an image. Isolated process. |
| **Dockerfile** | Recipe for building an image — layer by layer. |
| **Registry** | Image storage: Docker Hub (public), or private registries. |
| **Volume** | Persistent storage attached to a container (survives restarts). |
| **Network** | Virtual network connecting containers to each other or the host. |
| **Compose** | Tool to run multi-container apps defined in `docker-compose.yml`. |

---

## Docker CLI Essentials

### Pull & run images
```bash
docker pull python:3.12-slim          # download only
docker run python:3.12-slim python --version
docker run -it python:3.12-slim bash  # interactive shell
```

### Port mapping (`-p host:container`)
```bash
docker run -d -p 8080:80 nginx
# now http://localhost:8080 → container port 80
```

### Named containers
```bash
docker run -d --name my-nginx -p 8080:80 nginx
docker stop my-nginx
docker start my-nginx
docker restart my-nginx
```

### Volume mount (`-v host_path:container_path`)
```bash
docker run -v C:\Projects\myapp:/app python:3.12-slim bash
```

### Environment variables
```bash
docker run -e DEBUG=true -e PORT=8000 myapp:latest
```

### Inspect / stats
```bash
docker inspect <container_id>
docker stats                          # live CPU/RAM usage
docker top <container_id>             # running processes
```

### Cleanup
```bash
docker system prune                   # remove stopped containers + dangling images
docker system prune -a                # also remove unused images (frees lots of space)
docker volume prune                   # remove unused volumes
```

---

## Writing Dockerfiles

### Minimal Python app
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "app.py"]
```

### Django app (production-ready)
```dockerfile
FROM python:3.12-slim

# System deps
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (layer caching — only re-runs if requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
```

### Multi-stage build (smaller final image)
```dockerfile
# Stage 1: Build
FROM python:3.12 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime (slim)
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
CMD ["python", "app.py"]
```

### Key Dockerfile rules
- **`COPY requirements.txt` before `COPY .`** — layer caching means pip only
  re-runs when requirements change, not on every code edit.
- **Use slim base images** — `python:3.12-slim` is ~50MB vs `python:3.12` at ~1GB.
- **`--no-cache-dir`** on pip — saves ~50MB per install.
- **One `CMD`** — last CMD wins. Use `ENTRYPOINT` for fixed binary + `CMD` for default args.
- **`.dockerignore`** — always add to skip `__pycache__`, `.git`, `*.pyc`, `env/`.

### .dockerignore template
```
__pycache__/
*.py[cod]
*.egg-info/
.git/
.gitignore
env/
venv/
.env
*.sqlite3
*.log
node_modules/
```

---

## Docker Compose

Define multi-service apps in one `docker-compose.yml`:

### Django + PostgreSQL + Redis
```yaml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/myapp
      - REDIS_URL=redis://redis:6379/0
      - DEBUG=true
    volumes:
      - .:/app               # live code reload in dev
    depends_on:
      - db
      - redis
    command: python manage.py runserver 0.0.0.0:8000

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Compose commands
```bash
docker compose up               # start (foreground, see logs)
docker compose up -d            # start detached
docker compose up --build       # rebuild images before starting
docker compose down             # stop + remove containers/networks
docker compose down -v          # also remove volumes
docker compose restart web      # restart single service
docker compose exec web bash    # shell into running service
docker compose run web python manage.py migrate  # one-off command
docker compose logs web -f      # follow logs for one service
docker compose pull             # pull latest versions of all images
```

### Simple Nginx + static files
```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./static:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
```

### Override for development vs production
```yaml
# docker-compose.yml (base)
services:
  web:
    build: .
    environment:
      - SECRET_KEY=changeme

# docker-compose.override.yml (auto-loaded in dev)
services:
  web:
    volumes:
      - .:/app
    environment:
      - DEBUG=true
    command: python manage.py runserver 0.0.0.0:8000
```

---

## Volumes & Persistence

```bash
# Named volume (Docker manages location)
docker run -v mydata:/data myapp

# Bind mount (maps host folder into container)
docker run -v C:\Projects\data:/data myapp

# Read-only bind mount
docker run -v C:\Projects\config:/config:ro myapp

# List volumes
docker volume ls

# Inspect volume
docker volume inspect mydata

# Remove volume
docker volume rm mydata
```

**When to use what:**
- **Named volumes** — databases, uploads, persistent app data
- **Bind mounts** — development (live code reload), configs

---

## Networking

```bash
# List networks
docker network ls

# Create a custom network
docker network create mynet

# Run container on custom network
docker run -d --network mynet --name app1 myapp
docker run -d --network mynet --name app2 myapp
# app1 can reach app2 via http://app2:8000

# Containers on the same Compose network auto-discover each other by service name
```

In Compose, all services are on the same default network automatically. Services
reach each other by their **service name** as the hostname:
```python
# In Django settings.py — connect to "db" service in Compose
DATABASES = {
    "default": {
        "HOST": "db",    # ← service name, not "localhost"
        "PORT": "5432",
    }
}
```

---

## Environment Variables & Secrets

### `.env` file (auto-loaded by Compose)
```bash
# .env
DEBUG=true
SECRET_KEY=dev-only-key-change-in-production
DATABASE_URL=postgresql://postgres:postgres@db:5432/myapp
```

### Reference in docker-compose.yml
```yaml
services:
  web:
    environment:
      - DEBUG=${DEBUG}
      - SECRET_KEY=${SECRET_KEY}
    env_file:
      - .env          # load all vars from file
```

> **Never commit `.env` to git.** Add it to `.gitignore`.

---

## Common App Recipes

### Run a one-off Django command
```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py shell
```

### Copy file to/from container
```bash
docker cp mycontainer:/app/logs/error.log ./error.log    # container → host
docker cp ./config.json mycontainer:/app/config.json     # host → container
```

### Quick PostgreSQL with pgAdmin
```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"

  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@admin.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
```

### Quick Redis + RedisInsight
```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  redisinsight:
    image: redislabs/redisinsight
    ports:
      - "8001:8001"
```

---

## Intel Proxy Setup

Docker needs the proxy to pull images on Intel corporate network.

### Docker Desktop — GUI settings
1. Open Docker Desktop → Settings → Resources → Proxies
2. Set HTTP and HTTPS proxy to `http://proxy-iil.intel.com:912`
3. Apply & Restart

### For builds (proxy inside Dockerfile)
```dockerfile
# Pass at build time
ARG HTTP_PROXY
ARG HTTPS_PROXY
RUN pip install ...
```
```bash
docker build \
  --build-arg HTTP_PROXY=http://proxy-iil.intel.com:912 \
  --build-arg HTTPS_PROXY=http://proxy-iil.intel.com:912 \
  -t myapp .
```

---

## Troubleshooting

### "port is already allocated"
```bash
# Find what's using the port
netstat -ano | findstr :8000
# Kill it, or change the host port mapping in docker-compose.yml
```

### "Cannot connect to the Docker daemon"
```powershell
# Docker Desktop not running — start it
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

### Container exits immediately
```bash
docker logs <container_id>      # check what error occurred
docker run -it myapp bash       # run interactive to debug
```

### Build slow — not using cache
- Ensure `COPY requirements.txt .` is before `COPY . .`
- Don't change frequently-changing files early in the Dockerfile

### Volume data not persisting
- Named volumes persist across `docker compose down`
- `docker compose down -v` **deletes volumes** — don't use `-v` if you want data

### "No space left on device"
```bash
docker system prune -a          # remove all unused images, containers, networks
docker volume prune             # remove unused volumes
```

---

## Lessons Learned

- **Layer order matters**: Put slow-changing steps (`pip install`) before
  fast-changing ones (`COPY . .`) to maximize cache hits.
- **`depends_on` does not wait for ready**: It only waits for the container to
  *start*, not for Postgres to accept connections. Use `wait-for-it.sh` or
  retry logic in your app.
- **Bind mounts on Windows**: Use forward slashes in paths or Docker-style
  paths (`/c/Users/...`). Windows paths with backslashes can fail.
- **Don't run as root**: Add `USER appuser` in production Dockerfiles.
- **`.dockerignore` is critical**: Without it, `COPY . .` copies `.git`,
  `node_modules`, and all test data — making images huge.
- **Compose network**: Services talk to each other via service name as hostname.
  `db:5432` not `localhost:5432`.
- **`docker compose up --build`**: Always use `--build` when testing Dockerfile
  changes — otherwise Compose uses the cached image.
