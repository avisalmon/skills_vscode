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

i Docker Basics — Containers, Images & Compose

> **Purpose**: Package, run, and ship applications using Docker containers.
> Works on Windows (Docker Desktop), Linux, and macOS.

---

ii Table of Contents

1. [Quick Reference](iquick-reference)
2. [Core Concepts](icore-concepts)
3. [Docker CLI Essentials](idocker-cli-essentials)
4. [Writing Dockerfiles](iwriting-dockerfiles)
5. [Docker Compose](idocker-compose)
6. [Volumes & Persistence](ivolumes--persistence)
7. [Networking](inetworking)
8. [Environment Variables & Secrets](ienvironment-variables--secrets)
9. [Common App Recipes](icommon-app-recipes)
10. [Corporate Proxy Setup](iintel-proxy-setup)
11. [Troubleshooting](itroubleshooting)
12. [Lessons Learned](ilessons-learned)

---

ii Quick Reference

```powershell
i Run a container (download + start)
docker run hello-world
docker run -it ubuntu bash          i interactive terminal
docker run -d -p 8080:80 nginx      i detached, port mapping

i Build an image from Dockerfile in current dir
docker build -t myapp:latest .

i List running containers
docker ps
docker ps -a                        i including stopped

i Stop / remove
docker stop <container_id>
docker rm <container_id>

i List images
docker images

i Remove image
docker rmi myapp:latest

i Logs
docker logs <container_id>
docker logs -f <container_id>       i follow (like tail -f)

i Exec into running container
docker exec -it <container_id> bash

i Docker Compose
docker compose up -d                i start all services, detached
docker compose down                 i stop and remove containers
docker compose logs -f              i follow all service logs
docker compose ps                   i service status
```

---

ii Core Concepts

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

ii Docker CLI Essentials

iii Pull & run images
```bash
docker pull python:3.12-slim          i download only
docker run python:3.12-slim python --version
docker run -it python:3.12-slim bash  i interactive shell
```

iii Port mapping (`-p host:container`)
```bash
docker run -d -p 8080:80 nginx
i now http://localhost:8080 → container port 80
```

iii Named containers
```bash
docker run -d --name my-nginx -p 8080:80 nginx
docker stop my-nginx
docker start my-nginx
docker restart my-nginx
```

iii Volume mount (`-v host_path:container_path`)
```bash
docker run -v C:\Projects\myapp:/app python:3.12-slim bash
```

iii Environment variables
```bash
docker run -e DEBUG=true -e PORT=8000 myapp:latest
```

iii Inspect / stats
```bash
docker inspect <container_id>
docker stats                          i live CPU/RAM usage
docker top <container_id>             i running processes
```

iii Cleanup
```bash
docker system prune                   i remove stopped containers + dangling images
docker system prune -a                i also remove unused images (frees lots of space)
docker volume prune                   i remove unused volumes
```

---

ii Writing Dockerfiles

iii Minimal Python app
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "app.py"]
```

iii Django app (production-ready)
```dockerfile
FROM python:3.12-slim

i System deps
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

i Install Python deps first (layer caching — only re-runs if requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

i Copy app code
COPY . .

i Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

i Run with gunicorn
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
```

iii Multi-stage build (smaller final image)
```dockerfile
i Stage 1: Build
FROM python:3.12 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

i Stage 2: Runtime (slim)
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
CMD ["python", "app.py"]
```

iii Key Dockerfile rules
- **`COPY requirements.txt` before `COPY .`** — layer caching means pip only
  re-runs when requirements change, not on every code edit.
- **Use slim base images** — `python:3.12-slim` is ~50MB vs `python:3.12` at ~1GB.
- **`--no-cache-dir`** on pip — saves ~50MB per install.
- **One `CMD`** — last CMD wins. Use `ENTRYPOINT` for fixed binary + `CMD` for default args.
- **`.dockerignore`** — always add to skip `__pycache__`, `.git`, `*.pyc`, `env/`.

iii .dockerignore template
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

ii Docker Compose

Define multi-service apps in one `docker-compose.yml`:

iii Django + PostgreSQL + Redis
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
      - .:/app               i live code reload in dev
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

iii Compose commands
```bash
docker compose up               i start (foreground, see logs)
docker compose up -d            i start detached
docker compose up --build       i rebuild images before starting
docker compose down             i stop + remove containers/networks
docker compose down -v          i also remove volumes
docker compose restart web      i restart single service
docker compose exec web bash    i shell into running service
docker compose run web python manage.py migrate  i one-off command
docker compose logs web -f      i follow logs for one service
docker compose pull             i pull latest versions of all images
```

iii Simple Nginx + static files
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

iii Override for development vs production
```yaml
i docker-compose.yml (base)
services:
  web:
    build: .
    environment:
      - SECRET_KEY=changeme

i docker-compose.override.yml (auto-loaded in dev)
services:
  web:
    volumes:
      - .:/app
    environment:
      - DEBUG=true
    command: python manage.py runserver 0.0.0.0:8000
```

---

ii Volumes & Persistence

```bash
i Named volume (Docker manages location)
docker run -v mydata:/data myapp

i Bind mount (maps host folder into container)
docker run -v C:\Projects\data:/data myapp

i Read-only bind mount
docker run -v C:\Projects\config:/config:ro myapp

i List volumes
docker volume ls

i Inspect volume
docker volume inspect mydata

i Remove volume
docker volume rm mydata
```

**When to use what:**
- **Named volumes** — databases, uploads, persistent app data
- **Bind mounts** — development (live code reload), configs

---

ii Networking

```bash
i List networks
docker network ls

i Create a custom network
docker network create mynet

i Run container on custom network
docker run -d --network mynet --name app1 myapp
docker run -d --network mynet --name app2 myapp
i app1 can reach app2 via http://app2:8000

i Containers on the same Compose network auto-discover each other by service name
```

In Compose, all services are on the same default network automatically. Services
reach each other by their **service name** as the hostname:
```python
i In Django settings.py — connect to "db" service in Compose
DATABASES = {
    "default": {
        "HOST": "db",    i ← service name, not "localhost"
        "PORT": "5432",
    }
}
```

---

ii Environment Variables & Secrets

iii `.env` file (auto-loaded by Compose)
```bash
i .env
DEBUG=true
SECRET_KEY=dev-only-key-change-in-production
DATABASE_URL=postgresql://postgres:postgres@db:5432/myapp
```

iii Reference in docker-compose.yml
```yaml
services:
  web:
    environment:
      - DEBUG=${DEBUG}
      - SECRET_KEY=${SECRET_KEY}
    env_file:
      - .env          i load all vars from file
```

> **Never commit `.env` to git.** Add it to `.gitignore`.

---

ii Common App Recipes

iii Run a one-off Django command
```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py shell
```

iii Copy file to/from container
```bash
docker cp mycontainer:/app/logs/error.log ./error.log    i container → host
docker cp ./config.json mycontainer:/app/config.json     i host → container
```

iii Quick PostgreSQL with pgAdmin
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

iii Quick Redis + RedisInsight
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

ii Corporate Proxy Setup

Docker needs the proxy to pull images on a corporate network.

iii Docker Desktop — GUI settings
1. Open Docker Desktop → Settings → Resources → Proxies
2. Set HTTP and HTTPS proxy to `http://proxy.example.com:8080`
3. Apply & Restart

iii For builds (proxy inside Dockerfile)
```dockerfile
i Pass at build time
ARG HTTP_PROXY
ARG HTTPS_PROXY
RUN pip install ...
```
```bash
docker build \
  --build-arg HTTP_PROXY=http://proxy.example.com:8080 \
  --build-arg HTTPS_PROXY=http://proxy.example.com:8080 \
  -t myapp .
```

---

ii Troubleshooting

iii "port is already allocated"
```bash
i Find what's using the port
netstat -ano | findstr :8000
i Kill it, or change the host port mapping in docker-compose.yml
```

iii "Cannot connect to the Docker daemon"
```powershell
i Docker Desktop not running — start it
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

iii Container exits immediately
```bash
docker logs <container_id>      i check what error occurred
docker run -it myapp bash       i run interactive to debug
```

iii Build slow — not using cache
- Ensure `COPY requirements.txt .` is before `COPY . .`
- Don't change frequently-changing files early in the Dockerfile

iii Volume data not persisting
- Named volumes persist across `docker compose down`
- `docker compose down -v` **deletes volumes** — don't use `-v` if you want data

iii "No space left on device"
```bash
docker system prune -a          i remove all unused images, containers, networks
docker volume prune             i remove unused volumes
```

---

ii Lessons Learned

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
