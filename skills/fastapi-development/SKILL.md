---
name: fastapi-development
description: >
  Build REST APIs in Python with FastAPI — async, typed, auto-documented.
  Covers Pydantic models, dependency injection, JWT auth, SQLite/SQLAlchemy,
  background tasks, and deployment. TRIGGER: user says "fastapi", "build an
  API", "REST API in Python", "FastAPI endpoint", "Pydantic model", or
  "async API".
---

# FastAPI Development

> **Purpose**: Build production-quality REST APIs in Python with automatic
> OpenAPI docs, type validation, and async support. 3-10x less boilerplate
> than Django REST Framework for pure API work.

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Setup](#setup)
3. [First App](#first-app)
4. [Path & Query Parameters](#path--query-parameters)
5. [Request Body — Pydantic Models](#request-body--pydantic-models)
6. [Response Models](#response-models)
7. [Dependency Injection](#dependency-injection)
8. [Database with SQLAlchemy](#database-with-sqlalchemy)
9. [Authentication — JWT](#authentication--jwt)
10. [Background Tasks](#background-tasks)
11. [File Upload](#file-upload)
12. [CORS](#cors)
13. [Testing](#testing)
14. [Running & Deployment](#running--deployment)
15. [Lessons Learned](#lessons-learned)

---

## Quick Reference

```bash
pip install fastapi uvicorn[standard]

# Run dev server
uvicorn main:app --reload --port 8000

# Auto-generated docs:
# http://localhost:8000/docs      (Swagger UI)
# http://localhost:8000/redoc     (ReDoc)
# http://localhost:8000/openapi.json
```

---

## Setup

```bash
pip install fastapi uvicorn[standard] pydantic python-dotenv

# With database support
pip install sqlalchemy aiosqlite

# With JWT auth
pip install python-jose[cryptography] passlib[bcrypt]
```

---

## First App

```python
# main.py
from fastapi import FastAPI

app = FastAPI(title="My API", version="1.0.0")

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/health")
def health():
    return {"status": "ok"}
```

```bash
uvicorn main:app --reload
# Visit http://localhost:8000/docs for interactive Swagger UI
```

---

## Path & Query Parameters

```python
from fastapi import FastAPI, HTTPException, Query
from typing import Optional

app = FastAPI()

# Path parameter — type-validated automatically
@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"item_id": item_id}

# Query parameters (optional with default)
@app.get("/search")
def search(
    q: str,
    skip: int = 0,
    limit: int = Query(default=10, ge=1, le=100),  # validated range
    active: Optional[bool] = None,
):
    return {"q": q, "skip": skip, "limit": limit, "active": active}

# 404 example
@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id > 1000:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user_id}
```

---

## Request Body — Pydantic Models

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

app = FastAPI()

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str
    age: int = Field(..., ge=0, le=150)
    role: str = "user"          # default value

class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None

@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    # user.name, user.email, user.age etc. are typed and validated
    return {"id": 42, **user.model_dump()}

@app.patch("/users/{user_id}")
def update_user(user_id: int, user: UserUpdate):
    # Only fields that were provided (exclude_unset)
    updates = user.model_dump(exclude_unset=True)
    return {"user_id": user_id, "updated": updates}
```

### Nested models

```python
class Address(BaseModel):
    street: str
    city: str
    country: str = "IL"

class Employee(BaseModel):
    name: str
    address: Address
    tags: list[str] = []
```

---

## Response Models

```python
from pydantic import BaseModel

class UserPublic(BaseModel):
    id: int
    name: str
    email: str
    # NOTE: password, internal_notes NOT here — never leaked

class UserCreate(BaseModel):
    name: str
    email: str
    password: str    # only for input

# response_model strips fields not in UserPublic
@app.post("/users", response_model=UserPublic, status_code=201)
def create_user(user: UserCreate):
    # password never appears in response even if you return it
    return {"id": 1, "name": user.name, "email": user.email, "password": user.password}
```

---

## Dependency Injection

```python
from fastapi import Depends, Header, HTTPException

# Simple dependency
def get_db():
    db = connect_db()
    try:
        yield db
    finally:
        db.close()

# Auth dependency
def require_auth(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")
    token = authorization.removeprefix("Bearer ")
    # validate token...
    return token

# Use in endpoints
@app.get("/items")
def list_items(db=Depends(get_db), token=Depends(require_auth)):
    return db.query("SELECT * FROM items")

# Reusable paginator dependency
from pydantic import BaseModel

class Pagination(BaseModel):
    skip: int = 0
    limit: int = 20

def paginate(skip: int = 0, limit: int = 20) -> Pagination:
    return Pagination(skip=skip, limit=limit)

@app.get("/products")
def list_products(page: Pagination = Depends(paginate)):
    return {"skip": page.skip, "limit": page.limit}
```

---

## Database with SQLAlchemy

```python
# database.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

```python
# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, Item
from pydantic import BaseModel

app = FastAPI()

class ItemCreate(BaseModel):
    name: str

class ItemOut(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}

@app.get("/items", response_model=list[ItemOut])
def list_items(db: Session = Depends(get_db)):
    return db.query(Item).all()

@app.post("/items", response_model=ItemOut, status_code=201)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item(name=item.name)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(item)
    db.commit()
```

---

## Authentication — JWT

```python
pip install python-jose[cryptography] passlib[bcrypt]
```

```python
# auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

SECRET_KEY = "your-secret-key-from-env"  # use os.environ in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise ValueError
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid token")
    return username

# Usage
@app.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends()):
    # validate form.username / form.password against DB
    token = create_access_token({"sub": form.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me")
def me(user: str = Depends(get_current_user)):
    return {"username": user}
```

---

## Background Tasks

```python
from fastapi import BackgroundTasks
import time

def send_email(to: str, subject: str):
    # runs after response is sent — non-blocking
    time.sleep(2)
    print(f"Email sent to {to}: {subject}")

@app.post("/register")
def register(email: str, background_tasks: BackgroundTasks):
    # ... create user in DB ...
    background_tasks.add_task(send_email, email, "Welcome!")
    return {"message": "Registered — welcome email is sending"}
```

---

## File Upload

```python
from fastapi import UploadFile, File
import shutil

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    save_path = f"uploads/{file.filename}"
    with open(save_path, "wb") as out:
        shutil.copyfileobj(file.file, out)
    return {"filename": file.filename, "size": file.size}

# Multiple files
@app.post("/upload-many")
async def upload_many(files: list[UploadFile] = File(...)):
    return [{"filename": f.filename} for f in files]
```

---

## CORS

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://myapp.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Testing

```bash
pip install httpx pytest
```

```python
# test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"message": "Hello World"}

def test_create_item():
    r = client.post("/items", json={"name": "Widget"})
    assert r.status_code == 201
    assert r.json()["name"] == "Widget"

def test_get_item_not_found():
    r = client.get("/items/99999")
    assert r.status_code == 404
```

```bash
pytest test_main.py -v
```

---

## Running & Deployment

### Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production (gunicorn + uvicorn workers)
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment variables pattern
```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str
    database_url: str = "sqlite:///./app.db"
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Lessons Learned

- **`response_model` is security**: Always declare it to prevent leaking
  internal fields like passwords or tokens.
- **`Depends(get_db)` with `yield`**: The `finally` block runs after the
  response — this is how session cleanup works.
- **Pydantic v2**: Use `model_dump()` not `dict()`, `model_config` not
  `class Config`. FastAPI 0.100+ uses Pydantic v2.
- **`from_attributes = True`**: Required on response models when returning
  SQLAlchemy ORM objects (previously `orm_mode = True`).
- **`async def` vs `def`**: Use `async def` only if your function awaits
  something. Plain `def` endpoints run in a thread pool — fine for sync code.
- **Auto docs**: Visit `/docs` during development — it gives you a full
  interactive test UI with no extra work.
- **Status codes**: Use `status_code=201` on POST, `204` on DELETE.
  FastAPI defaults to 200 for everything.
