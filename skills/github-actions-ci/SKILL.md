---
name: github-actions-ci
description: >
  Automate tests, builds, and deployments on GitHub push/PR using GitHub
  Actions. Write YAML workflows for Python testing, Docker builds, linting,
  and deploy-on-merge. TRIGGER: user says "github actions", "CI/CD",
  "workflow yaml", "automate tests on push", "continuous integration",
  "deploy on merge", or ".github/workflows".
---

# GitHub Actions CI/CD

> **Purpose**: Automate testing, building, and deploying code every time you
> push to GitHub. Zero infrastructure needed — runs on GitHub's servers.

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Workflow File Structure](#workflow-file-structure)
3. [Triggers](#triggers)
4. [Jobs & Steps](#jobs--steps)
5. [Python Testing Workflow](#python-testing-workflow)
6. [Django CI Workflow](#django-ci-workflow)
7. [Docker Build & Push](#docker-build--push)
8. [Linting & Code Quality](#linting--code-quality)
9. [Environment Variables & Secrets](#environment-variables--secrets)
10. [Matrix Builds](#matrix-builds)
11. [Caching Dependencies](#caching-dependencies)
12. [Deploy on Merge](#deploy-on-merge)
13. [Manual Trigger (workflow_dispatch)](#manual-trigger-workflow_dispatch)
14. [Useful Actions Catalog](#useful-actions-catalog)
15. [Lessons Learned](#lessons-learned)

---

## Quick Reference

```
.github/
  workflows/
    ci.yml          # runs on push/PR
    deploy.yml      # runs on merge to main
    nightly.yml     # scheduled
```

```yaml
# Minimal working CI
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r requirements.txt
      - run: pytest
```

---

## Workflow File Structure

```yaml
name: My Workflow          # displayed in GitHub Actions tab

on:                        # TRIGGERS — when this runs
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]

env:                       # workflow-level env vars
  PYTHONUNBUFFERED: "1"

jobs:
  my-job:                  # job ID (used for depends-on)
    runs-on: ubuntu-latest # runner OS
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run a command
        run: echo "Hello from Actions"

      - name: Multi-line command
        run: |
          echo "Line 1"
          echo "Line 2"
```

---

## Triggers

```yaml
on:
  # Push to specific branches
  push:
    branches: [main, "release/*"]
    paths: ["src/**", "tests/**"]  # only when these paths change

  # PR to main
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]

  # Scheduled (cron — UTC)
  schedule:
    - cron: "0 2 * * 1"   # every Monday at 2am UTC

  # Manual trigger from GitHub UI
  workflow_dispatch:
    inputs:
      environment:
        description: "Deploy target"
        required: true
        default: "staging"
        type: choice
        options: [staging, production]

  # When another workflow completes
  workflow_run:
    workflows: ["CI"]
    types: [completed]
    branches: [main]
```

---

## Jobs & Steps

```yaml
jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      # Checkout
      - uses: actions/checkout@v4

      # Conditional step
      - name: Only on main
        if: github.ref == 'refs/heads/main'
        run: echo "This is main branch"

      # Step with outputs
      - name: Get version
        id: version
        run: echo "version=$(cat VERSION)" >> $GITHUB_OUTPUT

      - name: Use version
        run: echo "Version is ${{ steps.version.outputs.version }}"

      # Fail fast
      - name: Check required file
        run: test -f requirements.txt || (echo "Missing requirements.txt" && exit 1)

  deploy:
    needs: build          # only runs if build succeeds
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - run: echo "Deploying..."
```

---

## Python Testing Workflow

```yaml
# .github/workflows/ci.yml
name: Python CI

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
          restore-keys: ${{ runner.os }}-pip-

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest tests/ -v --tb=short

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: pytest-results.xml
```

---

## Django CI Workflow

```yaml
# .github/workflows/django-ci.yml
name: Django CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    env:
      DJANGO_SETTINGS_MODULE: myproject.settings
      SECRET_KEY: ci-test-secret-key-not-real
      DEBUG: "true"

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: pip-${{ hashFiles('requirements.txt') }}

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run migrations
        run: python manage.py migrate --noinput

      - name: Run tests
        run: python manage.py test --verbosity=2

      - name: Check for missing migrations
        run: python manage.py makemigrations --check --dry-run
```

---

## Docker Build & Push

```yaml
# .github/workflows/docker.yml
name: Docker Build & Push

on:
  push:
    branches: [main]
    tags: ["v*"]

jobs:
  docker:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: myuser/myapp
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=sha,prefix=sha-

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

---

## Linting & Code Quality

```yaml
# .github/workflows/lint.yml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install linters
        run: pip install ruff black mypy

      - name: Ruff (fast linter)
        run: ruff check .

      - name: Black (format check)
        run: black --check .

      - name: MyPy (type check)
        run: mypy src/ --ignore-missing-imports

  # Security scan
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install bandit safety
      - name: Bandit (security linter)
        run: bandit -r src/ -ll
      - name: Safety (dependency vulnerabilities)
        run: safety check
```

---

## Environment Variables & Secrets

### Setting secrets
GitHub repo → Settings → Secrets and variables → Actions → New repository secret

```yaml
jobs:
  deploy:
    steps:
      # Access secrets
      - run: echo "Deploying with key ${{ secrets.DEPLOY_KEY }}"
        env:
          API_KEY: ${{ secrets.API_KEY }}

      # Pass to Docker
      - uses: docker/login-action@v3
        with:
          password: ${{ secrets.DOCKERHUB_TOKEN }}
```

### Environment-scoped secrets (staging vs production)
```yaml
jobs:
  deploy-staging:
    environment: staging         # uses "staging" environment secrets
    steps:
      - run: deploy.sh
        env:
          DB_URL: ${{ secrets.DB_URL }}   # staging DB_URL from "staging" env

  deploy-prod:
    environment: production      # uses "production" environment secrets
    needs: deploy-staging
```

---

## Matrix Builds

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ["3.11", "3.12", "3.13"]
        exclude:
          - os: windows-latest
            python-version: "3.11"   # skip this combination

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pytest
```

---

## Caching Dependencies

```yaml
# Pip cache (fastest approach)
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-

# Node modules
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}

# Docker layer cache (in build-push-action)
cache-from: type=gha
cache-to: type=gha,mode=max
```

---

## Deploy on Merge

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production       # requires approval if configured

    steps:
      - uses: actions/checkout@v4

      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            cd /app
            git pull origin main
            pip install -r requirements.txt
            python manage.py migrate --noinput
            touch web.config   # recycle IIS / restart gunicorn

      # Or: deploy to Render
      - name: Trigger Render Deploy
        run: |
          curl -X POST "${{ secrets.RENDER_DEPLOY_HOOK_URL }}"
```

---

## Manual Trigger (workflow_dispatch)

```yaml
name: Manual Deploy

on:
  workflow_dispatch:
    inputs:
      environment:
        description: "Target environment"
        required: true
        type: choice
        options: [staging, production]
      version:
        description: "Version tag to deploy"
        required: false
        default: "latest"

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: |
          echo "Deploying ${{ inputs.version }} to ${{ inputs.environment }}"
```

Trigger from: GitHub repo → Actions tab → select workflow → Run workflow.

---

## Useful Actions Catalog

| Action | Purpose |
|--------|---------|
| `actions/checkout@v4` | Checkout repo code |
| `actions/setup-python@v5` | Install Python |
| `actions/cache@v4` | Cache pip/npm/etc. |
| `actions/upload-artifact@v4` | Save test results, logs |
| `actions/download-artifact@v4` | Load artifacts from prior job |
| `docker/build-push-action@v5` | Build and push Docker images |
| `docker/login-action@v3` | Log in to Docker Hub or ECR |
| `appleboy/ssh-action@v1` | Run commands on remote server |
| `softprops/action-gh-release@v2` | Create GitHub releases |
| `codecov/codecov-action@v4` | Upload coverage to Codecov |

---

## Lessons Learned

- **`actions/checkout@v4` must be the first step** in every job — without it
  the workspace is empty.
- **Secrets are masked in logs** but DON'T print them explicitly with `echo`.
- **`if: always()`** on upload-artifact ensures logs are saved even when tests fail.
- **Cache key must include a hash of requirements**: `hashFiles('requirements.txt')`.
  Without this, the cache is never invalidated.
- **`needs: build`** creates sequential jobs — the deploy job won't start if
  the build job fails.
- **`environment: production`** enables required reviewers: someone must approve
  before the job runs. Great for production deploys.
- **Matrix strategy**: if one matrix combination fails, the others continue by
  default. Add `fail-fast: false` to ensure all combinations complete.
- **`GITHUB_OUTPUT`**: Modern way to pass values between steps. Old `set-output`
  is deprecated: use `echo "key=value" >> $GITHUB_OUTPUT`.
- **Free tier**: GitHub Actions is free for public repos. Private repos get
  2,000 minutes/month on free plan.
