---
name: render-django
description: >
  Deploy a Django app to Render with SQLite on a persistent disk, WhiteNoise static files,
  media uploads, GitHub auto-deploy, simple auth, and Google OAuth via django-allauth.
  TRIGGER: user says "deploy to render", "render django", "set up render",
  "create render service", "render deployment", "google login django", or "django allauth".
---

# Render + Django Deployment Skill

Deploy a Django app to Render with SQLite on a persistent disk, WhiteNoise static files, media file uploads, GitHub auto-deploy, simple auth, and Google OAuth.

**TRIGGER**: user says "deploy to render", "render django", "set up render", "create render service", "render deployment", "google login django", or "django allauth".

---

## Stack

- Django + Gunicorn + WhiteNoise
- SQLite on Render persistent disk at `/var/data`
- Media files (ImageField) on same disk at `/var/data/media`
- GitHub → Render auto-deploy via `render.yaml` Blueprint
- `django-allauth` for Google OAuth
- Cost: ~$7.25/month (Starter service $7 + 1GB disk $0.25)

---

## Package rule

**Always** maintain `requirements.txt`. Never auto-install. When a new package is needed, add it to `requirements.txt` and ask the user to run:
```powershell
.\env\Scripts\pip.exe install -r requirements.txt
```

---

## Dev flow — MANDATORY

**Local = dev. Render = production. Never mix them.**

1. **Develop locally** — all code changes, new features, bug fixes happen in `c:\Projects\Render` with `python manage.py runserver`
2. **Test locally** — verify everything works at `http://127.0.0.1:8000` before even thinking about deploy
3. **Commit** — `git add` + `git commit` as often as needed, but **DO NOT `git push`** without the user's explicit permission
4. **Deploy = push** — `git push` triggers auto-deploy to production. **Only push when the user says "deploy"**, "push", or "go live"
5. **Never** push to test something. Never push "just to see if it works on Render". If it doesn't work locally, it won't work in production.

**If in doubt, ask: "Ready to deploy?"**

---

## Step 1: Local project setup

```powershell
.\env\Scripts\python.exe -m django startproject mysite .
.\env\Scripts\python.exe manage.py startapp app
```

`requirements.txt`:
```txt
Django>=5.0,<6.1
gunicorn>=22,<24
whitenoise>=6.7,<7
django-allauth[socialaccount]>=65.0,<66
requests>=2.31,<3
Pillow>=10.0,<12
```

---

## Step 2: production settings.py

Replace the generated `settings.py` entirely with this pattern:

```python
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key")
DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]
CSRF_TRUSTED_ORIGINS = [u.strip() for u in os.environ.get("CSRF_TRUSTED_ORIGINS", "http://127.0.0.1:8000,http://localhost:8000").split(",") if u.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # must be second
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "mysite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "mysite.wsgi.application"

# Persistent disk — read-only during build, mounted at runtime
PERSISTENT_ROOT = Path(os.environ.get("PERSISTENT_ROOT", BASE_DIR))
DATA_DIR = PERSISTENT_ROOT / "data"
MEDIA_DIR = PERSISTENT_ROOT / "media"

try:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    pass  # Disk not mounted during build phase — safe to skip

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(DATA_DIR / "db.sqlite3"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

MEDIA_URL = "/media/"
MEDIA_ROOT = MEDIA_DIR

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 0 if DEBUG else 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# django-allauth
SITE_ID = 1
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
            "secret": os.environ.get("GOOGLE_CLIENT_SECRET", ""),
        },
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    }
}
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
ACCOUNT_LOGIN_METHODS = {"email"}          # allauth 65.x syntax
ACCOUNT_SIGNUP_FIELDS = ["email*"]         # allauth 65.x syntax
ACCOUNT_EMAIL_VERIFICATION = "none"
```

---

## Step 3: urls.py — CRITICAL media serving fix

**DO NOT use `django.conf.urls.static.static()` for media in production.**
It has a hidden `if not settings.DEBUG: return []` inside — silently returns nothing when `DEBUG=False`.

Use `re_path` + `django.views.static.serve` directly:

```python
from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("app.urls")),
]

# Serve media files in all environments.
# static() returns [] when DEBUG=False — use re_path+serve instead.
# Acceptable for small sites; use object storage for high traffic.
urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
```

---

## Step 4: App code (models, views, urls, templates)

### app/models.py — example with ImageField
```python
from django.db import models
from django.contrib.auth.models import User

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    image = models.ImageField(upload_to="notes/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
```

### app/views.py
```python
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Note

def home(request):
    notes = Note.objects.filter(user=request.user) if request.user.is_authenticated else []
    return render(request, "app/home.html", {"notes": notes})

@login_required
def add_note(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        body = request.POST.get("body", "").strip()
        image = request.FILES.get("image")
        if title:
            Note.objects.create(user=request.user, title=title, body=body, image=image)
    return redirect("home")

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("home")
```

### app/urls.py
```python
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("notes/add/", views.add_note, name="add_note"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
]
```

### app/admin.py
```python
from django.contrib import admin
from .models import Note

admin.site.register(Note)
```

### templates/app/home.html — with static CSS, file upload, image display, Google login
```html
{% load static %}
<!DOCTYPE html>
<html>
<head>
  <title>My Site</title>
  <link rel="stylesheet" href="{% static 'style.css' %}">
</head>
<body>
  <h1>My Site</h1>

  {% if user.is_authenticated %}
    <p>Hello, {{ user.username }}.
      <a href="{% url 'logout' %}">Logout</a> |
      <a href="/admin/">Admin</a>
    </p>

    <h2>Add Note</h2>
    <form method="post" action="{% url 'add_note' %}" enctype="multipart/form-data">
      {% csrf_token %}
      <input name="title" placeholder="Title" required><br>
      <textarea name="body" placeholder="Body"></textarea><br>
      <input type="file" name="image" accept="image/*"><br>
      <button type="submit">Save</button>
    </form>

    <h2>Your Notes</h2>
    {% for note in notes %}
      <div class="note">
        <strong>{{ note.title }}</strong> — {{ note.body }}
        {% if note.image %}
          <br><img src="{{ note.image.url }}" style="max-width:300px;">
        {% endif %}
        <br><small>{{ note.created_at }}</small>
      </div>
    {% empty %}
      <p>No notes yet.</p>
    {% endfor %}

  {% else %}
    <p>
      <a href="{% url 'login' %}">Login</a> |
      <a href="{% url 'register' %}">Register</a> |
      <a href="/accounts/google/login/?next=/">Login with Google</a>
    </p>
  {% endif %}
</body>
</html>
```

### templates/registration/login.html
```html
<h1>Login</h1>
<form method="post">{% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Login</button>
</form>
<p><a href="{% url 'register' %}">Register</a> |
   <a href="/accounts/google/login/?next=/">Login with Google</a></p>
```

### templates/registration/register.html
```html
<h1>Register</h1>
<form method="post">{% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Register</button>
</form>
<p><a href="{% url 'login' %}">Login</a></p>
```

---

## Step 5: build.sh

**CRITICAL**: Do NOT run `migrate` in build.sh — disk is read-only during build.

```bash
#!/usr/bin/env bash
set -o errexit

python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --no-input
```

**CRITICAL**: Mark executable in git (Windows doesn't track permissions):
```powershell
git update-index --chmod=+x build.sh
```

---

## Step 6: render.yaml

```yaml
services:
  - type: web
    name: mysite
    runtime: python
    plan: starter
    branch: main
    buildCommand: ./build.sh
    startCommand: >-
      python manage.py migrate &&
      python manage.py createsuperuser --noinput || true &&
      gunicorn mysite.wsgi:application --bind 0.0.0.0:$PORT
    autoDeploy: true
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.9
      - key: DEBUG
        value: "False"
      - key: PERSISTENT_ROOT
        value: /var/data
      - key: ALLOWED_HOSTS
        value: <service-name>.onrender.com
      - key: CSRF_TRUSTED_ORIGINS
        value: https://<service-name>.onrender.com
      - key: SECRET_KEY
        sync: false
      - key: DJANGO_SUPERUSER_USERNAME
        sync: false
      - key: DJANGO_SUPERUSER_EMAIL
        sync: false
      - key: DJANGO_SUPERUSER_PASSWORD
        sync: false
      - key: GOOGLE_CLIENT_ID
        sync: false
      - key: GOOGLE_CLIENT_SECRET
        sync: false
    disk:
      name: mysite-disk
      mountPath: /var/data
      sizeGB: 1
```

Key notes:
- `migrate` in `startCommand` — disk mounted at runtime only
- `createsuperuser --noinput || true` — skips if user already exists
- `sync: false` — Render prompts for value at deploy time, never committed

---

## Step 7: .gitignore

```gitignore
.venv/
env/
__pycache__/
*.pyc
.env
.env.*
db.sqlite3
media/
staticfiles/
.vscode/
.idea/
.DS_Store
*.log
```

---

## Step 8: Git + GitHub

```powershell
git init
git add .gitignore requirements.txt
git commit -m "Initial: gitignore, requirements"
git add app\ mysite\ manage.py build.sh render.yaml static\ templates\
git commit -m "Scaffold Django project"
git branch -M main
git remote add origin https://github.com/<user>/<repo>.git
git push -u origin main
```

---

## Step 9: Render Blueprint deploy

1. Render dashboard → **New** → **Blueprint**
2. Connect GitHub → select repo
3. Render reads `render.yaml` automatically
4. Fill in **Blueprint name** (any label)
5. Fill in `SECRET_KEY` — generate with:
   ```powershell
   .\env\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(50))"
   ```
6. Fill in `DJANGO_SUPERUSER_*` env vars
7. Fill in `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` (or leave blank for later)
8. Review cost: ~$7.25/month → **Deploy Blueprint**

---

## Step 10: Post-deploy fixes

### Fix ALLOWED_HOSTS
Render assigns unpredictable hostnames (e.g. `mysite-0tu0.onrender.com`).
After first deploy: Render → Environment → update `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`.

### Fix startCommand 
`render.yaml` changes do NOT override a command already set in dashboard.
Must edit manually: Render → **Settings** → **Start Command**.

---

## Step 11: Google OAuth setup

1. **Google Cloud Console** → New project → APIs & Services → OAuth consent screen → External
2. Credentials → **Create OAuth Client ID** → Web application
3. Authorized redirect URI: `https://<service>.onrender.com/accounts/google/login/callback/`
4. Copy `client_id` and `client_secret`
5. Render → Environment → set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
6. **Admin → Sites** → change `example.com` to actual hostname (no `https://`)
7. Deploy

### Google auth behavior (proven)
- **New user, no prior account** → clicks Google → instant login, account auto-created, no form
- **Existing user whose email matches Google** → one-time confirmation form → seamless forever after
- One-time form is a **security feature** — prevents account hijacking

### allauth 65.x settings (breaking change)
Old `ACCOUNT_EMAIL_REQUIRED` + `ACCOUNT_AUTHENTICATION_METHOD` are DEPRECATED. Use:
```python
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*"]
```

---

## Step 12: Media files (ImageField + Pillow)

### Requirements
Add `Pillow>=10.0,<12` to `requirements.txt` for `ImageField`.

### Settings (already in Step 2)
```python
MEDIA_URL = "/media/"
MEDIA_ROOT = MEDIA_DIR      # /var/data/media in production
```

### URLs — the critical fix (already in Step 3)
**DO NOT** use `static(MEDIA_URL, document_root=MEDIA_ROOT)` — it returns `[]` when `DEBUG=False`.
Use `re_path` + `serve` instead.

### Upload form
Must include `enctype="multipart/form-data"` on the form tag.
Access file in view with `request.FILES.get("image")`.

### Persistence
Media files live on the persistent disk at `/var/data/media/notes/`.
They survive redeploys.

---

## Known gotchas — all proven in practice

| # | Gotcha | Fix |
|---|--------|-----|
| 1 | `build.sh` not executable on Linux | `git update-index --chmod=+x build.sh` |
| 2 | `mkdir /var/data` fails during build (read-only) | `try/except OSError: pass` in settings.py |
| 3 | `migrate` fails during build (can't open DB) | Move `migrate` to `startCommand` |
| 4 | 400 Bad Request after deploy | `ALLOWED_HOSTS` has wrong hostname — check actual Render URL |
| 5 | Blueprint parse error | Billing must be set on Render account before Blueprint works |
| 6 | Render sees all GitHub repos | Restrict: GitHub → Settings → Applications → Authorized OAuth Apps |
| 7 | Workspace plan ≠ service plan | Hobby workspace OK; `plan: starter` = service compute tier |
| 8 | `startCommand` not updated by yaml push | Edit manually in Render → Settings → Start Command |
| 9 | `createsuperuser` crashes on redeploy | Add `\|\| true` — harmless if user exists |
| 10 | allauth deprecated settings warnings | Use 65.x API: `ACCOUNT_LOGIN_METHODS`, `ACCOUNT_SIGNUP_FIELDS` |
| 11 | Google login shows signup form for existing user | Expected — one-time link confirmation, seamless after |
| 12 | `Sites` record still says `example.com` | Admin → Sites → update to actual hostname |
| 13 | Media files 404 in production | `static()` returns `[]` when `DEBUG=False` — use `re_path` + `serve` |
| 14 | Auto-deploy not triggering | Render GitHub **App** must be installed (not just OAuth). Go to `github.com/apps/render/installations/new` → install for your account → select repo. Without it, no webhook = no auto-deploy. |
| 15 | SSH blocked by corporate firewall | Port 22 blocked on a corporate network. Use Render API (`api.render.com`) over HTTPS instead, or Render Web Shell in browser. |
| 16 | DNS registrar form appends domain to host | When adding CNAME at Israeli registrar (LiveDNS), enter just `www` not `www.example.co.il` — the form auto-appends the domain. |
| 17 | `django check --deploy` warns about HSTS | Add `SECURE_HSTS_SECONDS`, `SECURE_HSTS_INCLUDE_SUBDOMAINS`, `SECURE_HSTS_PRELOAD` to settings (all gated on `not DEBUG`). |
| 18 | Google login fails on custom domain (`redirect_uri_mismatch`) | Add new domain to Google Cloud Console → OAuth Client → Authorized redirect URIs: `https://domain/accounts/google/login/callback/`. Also update Django Admin → Sites → change hostname to new domain. |
| 19 | `.co.il` `serverHold` lasts up to 3 days | ISOC-IL updates 4x/day (07:00, 13:00, 17:00, 21:00 IL time). New `.co.il` domains can take up to 72h. Not a misconfiguration — just wait. Contact LiveDNS support if >48h. |
| 20 | Deploy `update_failed` with no obvious reason | NEVER guess — fetch logs first (see "Debug a failed deploy" below). Build can succeed but runtime crashes (missing pkg, migration error, etc). |
| 21 | `ModuleNotFoundError` at runtime despite pkg in `requirements.txt` | Templatetag library failed to import (e.g. `import markdown`). Django's `manage.py` system check loads all templatetags → ANY import error in any tag module crashes EVERY management command including `migrate`. Add missing pkg to `requirements.txt`. |
| 22 | `InconsistentMigrationHistory: Migration X is applied before its dependency Y` | "Ghost migration" — a higher migration is recorded applied, but a lower one isn't. Happens after manual DB surgery or restoring partial backups. Fix by inserting missing rows into `django_migrations` BEFORE `migrate` runs (see "Schema/migration self-repair" below). Errors chain backwards — fix 0010 → 0009 surfaces → 0008 surfaces, etc. Fake-apply the whole range at once. |
| 23 | `render.yaml` startCommand parens dropped at runtime | Render container restart logs showed `migrate && createsuperuser \|\| true && gunicorn` (no parens) on retry. Operator precedence makes gunicorn boot even when migrate fails. Don't rely on parens for ordering — keep startCommand simple or put complex logic in `AppConfig.ready()`. |
| 24 | PATCH startCommand via API silently no-ops | Wrong field path. Correct: `serviceDetails.envSpecificDetails.startCommand` (NOT `serviceDetails.startCommand`). |

---

## Debug a failed deploy — MANDATORY first step

**Rule: when a deploy fails, FETCH LOGS BEFORE TOUCHING CODE.** No guessing, no "let me try X". Read the actual error first. This session burned 5+ deploys violating this rule.

### Render logs API (works over HTTPS, bypasses SSH firewall)

The logs endpoint is **owner-scoped**, not service-scoped. Both query params required:

```powershell
$key   = $env:RENDER_API_KEY                        # or paste literal
$svc   = "srv-d6ttohq4d50c73chm4tg"                 # service id
$owner = "tea-d6ttfncr85hc73aapmhg"                 # team/owner id (from service detail)
$end   = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
$start = [DateTime]::UtcNow.AddMinutes(-15).ToString("yyyy-MM-ddTHH:mm:ssZ")
$url   = "https://api.render.com/v1/logs?ownerId=$owner&resource=$svc&startTime=$start&endTime=$end&limit=200"
$j     = (Invoke-WebRequest -Uri $url -Headers @{Authorization="Bearer $key"} -UseBasicParsing).Content | ConvertFrom-Json
$j.logs | Sort-Object timestamp | ForEach-Object { "$($_.timestamp.Substring(11,8)) $($_.message)" } | Select-Object -Last 60
```

To find the owner id: `Invoke-RestMethod "https://api.render.com/v1/services/$svc" -Headers @{Authorization="Bearer $key"}` → `ownerId` field.

Useful filter — show only deploy lifecycle markers:
```powershell
$j.logs | Sort-Object timestamp | Where-Object { $_.message -match "Running |Exited|Traceback|Error|restarted|==>" } | ForEach-Object { "$($_.timestamp.Substring(11,8)) $($_.message)" }
```

### Note
- `/deploys/{id}/logs` endpoint returns 404 — does not exist.
- Build phase logs and runtime logs are both in the same `/v1/logs` stream, filterable by timestamp.
- One-off jobs (`/services/{id}/jobs` POST) let you test commands in isolation; their output also lands in the same log stream.

### Patch startCommand via API (when dashboard edit isn't practical)
```powershell
$body = @{ serviceDetails = @{ envSpecificDetails = @{ startCommand = "python manage.py migrate && gunicorn mysite.wsgi:application --bind 0.0.0.0:`$PORT" } } } | ConvertTo-Json -Depth 5
Invoke-RestMethod -Uri "https://api.render.com/v1/services/$svc" -Method Patch -Headers @{Authorization="Bearer $key"; "Content-Type"="application/json"} -Body $body
```

---

## Schema / migration self-repair on boot

If prod DB has missing columns/tables OR ghost migration history rows (often after restoring backups or manual surgery), you can't reach a Django shell to fix it because every `manage.py` command crashes on `check_consistent_history`. The fix runs **before** Django's checks: in `AppConfig.ready()` using raw `sqlite3`.

### Pattern (proven on babook.co.il)

`app/apps.py`:
```python
import sqlite3
from django.apps import AppConfig as DjangoAppConfig


def _repair_schema(db_path: str) -> None:
    """Patch missing schema and fake-apply ghost migrations BEFORE migrate runs."""
    try:
        conn = sqlite3.connect(db_path, timeout=10)
        c = conn.cursor()
        # bail if django_migrations table doesn't exist yet (first ever deploy)
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_migrations'")
        if not c.fetchone():
            conn.close()
            return

        # Idempotent ALTER TABLE for missing columns
        c.execute("PRAGMA table_info(app_course)")
        cols = {row[1] for row in c.fetchall()}
        if "title_en" not in cols:
            c.execute("ALTER TABLE app_course ADD COLUMN title_en varchar(200) NOT NULL DEFAULT ''")
        # ... repeat for each known missing column

        # Idempotent CREATE TABLE for missing tables
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='app_newslettersubscriber'")
        if not c.fetchone():
            c.execute("""CREATE TABLE app_newslettersubscriber ( ... )""")

        # Fake-apply ghost migrations so migrate's check_consistent_history passes.
        # IMPORTANT: errors chain backwards — list every migration from the lowest
        # missing one up to HEAD, not just the one in today's error message.
        for mig in [
            "0005_copilot_seats", "0006_ai_chat", "0007_billing_entitlement",
            "0008_corporate_lead", "0009_newslettersubscriber",
            "0010_course_video_enrollment_enhancements",
            "0011_lesson_quiz_certificate", "0012_quiz_passed_field",
            "0013_coursematerial",
        ]:
            c.execute("SELECT id FROM django_migrations WHERE app='app' AND name=?", [mig])
            if not c.fetchone():
                c.execute(
                    "INSERT INTO django_migrations (app, name, applied) VALUES (?,?,?)",
                    ["app", mig, "2024-01-01 00:00:00+00:00"],
                )
        conn.commit()
        conn.close()
    except Exception:
        pass  # never break startup — let migrate surface the real error


class AppConfig(DjangoAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"

    def ready(self):
        from django.conf import settings
        db_path = settings.DATABASES.get("default", {}).get("NAME", "")
        if db_path and db_path != ":memory:":
            _repair_schema(db_path)
```

### Why this works
- `ready()` runs for **every** `manage.py` invocation, including `migrate` itself, BEFORE the consistency check.
- Raw `sqlite3` — no Django ORM, so it works even when models don't match schema yet.
- Idempotent — safe to leave in code permanently; subsequent boots no-op cleanly.
- `try/except Exception: pass` — never break startup; if something's off, let the real `migrate` surface the error.

### When to remove this code
Leave it in. The cost is negligible (a few `SELECT`s on each boot) and it's a safety net for future schema drift / restores.

---

## Iterative debug discipline (lessons from babook.co.il outage)

When chasing a deploy failure, follow this loop strictly:

1. **Fetch logs** for the failed deploy id. Do NOT skip.
2. **Read the actual last error** — not the commit message, not the notification banner. The notification often quotes the OLD error.
3. **Make ONE targeted fix** for that exact error.
4. **Commit + push + poll deploy status**.
5. **Fetch logs again** — go to step 1.

Anti-patterns observed and to avoid:
- Adding unrelated "improvements" while fixing one bug.
- Pushing a "let's see if this works" speculative fix.
- Assuming the error from the failure notification is current — re-fetch logs.
- Cherry-picking only the migration mentioned in the error when there's clearly a backwards chain — fake-apply the whole range at once.

---

## Domain setup (after site is working)

1. Render → **mysite** → **Settings** → **Custom Domains** → Add both `example.com` and `www.example.com`
2. Render shows required DNS records. At your registrar:
   - **Root domain** (`@`): Add **A record** → `216.24.57.1` (CNAME not allowed on root by most providers)
   - **www subdomain**: Add **CNAME** → `<service>.onrender.com` (enter just `www` — registrar appends domain)
3. Update env vars **on Render dashboard** (yaml push won't override existing values — gotcha #8):
   - `ALLOWED_HOSTS`: `<service>.onrender.com,example.com,www.example.com`
   - `CSRF_TRUSTED_ORIGINS`: all three with `https://`
4. For `.co.il` domains: ISOC-IL updates DNS 4x/day (07:00, 13:00, 17:00, 21:00 Israel time). New domains can have `serverHold` for **up to 72h** — not a mistake, just wait.
5. Render auto-provisions HTTPS via Let's Encrypt after DNS resolves.
6. **Update Google OAuth** for new domain: Google Cloud Console → Credentials → OAuth Client → add `https://<domain>/accounts/google/login/callback/` to Authorized redirect URIs.
7. **Update Django Admin → Sites** → change hostname from `.onrender.com` to new domain.

---

## Smoke test checklist

- [ ] Homepage loads
- [ ] `/admin/` loads and login works
- [ ] CSS loads (WhiteNoise working)
- [ ] Register new user → login works
- [ ] Google login works (new user — no form)
- [ ] Add a note with an image → image displays
- [ ] Data and images survive a redeploy (persistent disk)
- [ ] No errors in Render logs

---

## Render API (remote operations from local terminal)

When SSH is blocked (corporate firewall), use the Render REST API over HTTPS.

### Setup
1. Render → Account Settings → **API Keys** → Create API Key
2. Store as user env var: `[System.Environment]::SetEnvironmentVariable('RENDER_API_KEY', '<key>', 'User')`

### List services
```powershell
Invoke-RestMethod -Uri "https://api.render.com/v1/services?limit=10" -Headers @{Authorization="Bearer $env:RENDER_API_KEY"}
```

### Run one-off job (e.g. django check --deploy)
```powershell
$body = @{startCommand="python manage.py check --deploy"; planOverride="starter"} | ConvertTo-Json
Invoke-RestMethod -Uri "https://api.render.com/v1/services/<service-id>/jobs" -Method Post -Headers @{Authorization="Bearer $env:RENDER_API_KEY"; "Content-Type"="application/json"} -Body $body
```

### Poll job status
```powershell
Invoke-RestMethod -Uri "https://api.render.com/v1/services/<service-id>/jobs/<job-id>" -Headers @{Authorization="Bearer $env:RENDER_API_KEY"}
```

Note: Job logs are not available via API — use Render Web Shell to see output.

---

## Django shell (via Render Web Shell)

For direct DB operations, use the Web Shell in the Render dashboard:

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from app.models import Note

User.objects.values_list('id', 'username')          # list users
u = User.objects.get(username='admin')
Note.objects.create(user=u, title='Test', body='From shell')  # create record
Note.objects.all().values('id', 'title', 'user__username')    # verify
```

---

## DevOps loop

```powershell
git add <files>
git commit -m "description"
git push
# Render auto-deploys from main
```

Rollback: `git revert <bad-commit>` → push → Render deploys the revert.
