+++
date = '2025-12-12T10:00:00+01:00'
draft = false
title = 'Drop SQLite: zero-dependency quick starts with pg0'
description = "Stop maintaining SQLite fallbacks for local dev. pg0 gives you real PostgreSQL via pip install with zero setup, pgvector included."
tags = ["database", "postgresql", "python", "asyncpg", "developer-experience"]
+++

**TL;DR**: Your users can clone your project, run `pip install`, and have Postgres running automatically. No "install Postgres first" in your README, no Docker, no SQLite fallbacks. pg0-embedded bundles Postgres for zero-friction onboarding.

---

## The Problem

Your Python app probably looks like this:

```python
if os.getenv("ENV") == "production":
    DATABASE_URL = os.getenv("DATABASE_URL")  # Postgres
else:
    DATABASE_URL = "sqlite:///dev.db"  # SQLite for "convenience"
```

You're paying a hidden tax:
- Can't use asyncpg (3-5x faster than psycopg2)
- No JSONB, arrays, or Postgres-native types
- Bugs that only appear in production
- ORM generates lowest-common-denominator SQL

Then there's the **complexity tax**. Your codebase accumulates `if sqlite: ... else: ...` branches. You write abstraction layers to paper over dialect differences. You test against both databases (or worse, you don't, and production breaks). Every new feature requires asking "does this work in SQLite too?" - and often the answer shapes your architecture in ways that make the Postgres version worse.

I've seen codebases where 20% of the database layer was just compatibility glue. That's code you maintain, debug, and reason about - for a database you don't even run in production.

### The Vector Search Problem

If you're building anything with embeddings or semantic search, the gap widens. pgvector is battle-tested, well-documented, and ships with managed Postgres everywhere (RDS, Cloud SQL, Supabase, Neon).

SQLite? You have two options:
- **sqlite-vss**: No longer in active development. Had C++ dependencies that only worked reliably on Linux and macOS.
- **sqlite-vec**: Newer and better, but still has friction. No ARM release on PyPI. Windows installation issues. Manual extension loading that some environments don't support. Different query syntax (`k = ?` instead of `LIMIT`).

Both require you to compile or load extensions manually. Neither matches pgvector's ecosystem maturity. And you'll still need pgvector in production anyway - so why maintain two vector implementations?

The reason SQLite sticks around? Installing Postgres locally is annoying. Docker works but adds overhead. Homebrew/apt means managing system services.

And if you maintain an OSS project, you've seen this: "install Postgres" in your README is a contributor barrier. So you keep SQLite support "for convenience" and pay the complexity tax forever.

## pg0-embedded: Zero-Dependency Postgres

pg0-embedded is a Python package that downloads and runs Postgres for you. No Docker. No system packages. Just `pip install`:

```bash
pip install pg0-embedded
```

```python
from pg0 import Pg0

# Context manager handles start/stop
with Pg0() as pg:
    print(pg.uri)  # postgresql://postgres:postgres@localhost:5432/postgres
    pg.execute("CREATE EXTENSION IF NOT EXISTS vector")
```

First run downloads Postgres 18 **with pgvector included**. No extension compilation, no manual loading. Subsequent runs use the cached binaries.

**Cross-platform**: Works on macOS (Intel + Apple Silicon), Linux (x86_64), and Windows. The binary auto-detects your platform and downloads the right build.

**Stateful**: Data persists in `~/.pg0/instances/<name>/`. Stop and restart your app - your data is still there. No volume mounts, no data loss surprises. Delete the directory if you want a fresh start.

## Migration: Before and After

**Before** (SQLite compatibility hell):

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dev.db")
engine = create_engine(DATABASE_URL)

# Stuck with sync driver, can't use Postgres features
```

**After** (pg0-embedded + asyncpg):

```python
import asyncpg
from pg0 import Pg0

# Dev: start local Postgres
if os.getenv("ENV") != "production":
    pg = Pg0()
    pg.start()
    DATABASE_URL = pg.uri
else:
    DATABASE_URL = os.getenv("DATABASE_URL")

# Now use asyncpg directly
pool = await asyncpg.create_pool(DATABASE_URL)
```

## Practical SDK Usage

### Auto port assignment

```python
from pg0 import Pg0

pg = Pg0()
pg.start()

# Port is auto-assigned to a free one if not specified
print(pg.uri)
# postgresql://postgres:postgres@localhost:54832/postgres
```

No port conflicts. Spin up multiple instances without worrying about what's already running on 5432.

### Named instances for isolation

```python
from pg0 import Pg0

# Run dev and test databases simultaneously
pg_dev = Pg0(name="dev")
pg_test = Pg0(name="test")

pg_dev.start()
pg_test.start()

# Each instance gets its own port and data directory
print(pg_dev.uri)
print(pg_test.uri)
```

### Custom configuration

```python
from pg0 import Pg0

pg = Pg0(
    name="myapp",
    port=5433,
    username="myuser",
    password="mypass",
    database="mydb",
    config={"shared_buffers": "512MB"}
)
pg.start()
```

### Pytest fixture

```python
import pytest
import asyncpg
from pg0 import Pg0

@pytest.fixture
async def db():
    pg = Pg0(name="test")
    pg.start()

    pool = await asyncpg.create_pool(pg.uri)
    yield pool

    await pool.close()
    pg.stop()
```

### FastAPI lifespan

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pg0 import Pg0

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start Postgres on app startup
    pg = Pg0()
    pg.start()

    app.state.pool = await asyncpg.create_pool(pg.uri)
    yield

    await app.state.pool.close()
    pg.stop()

app = FastAPI(lifespan=lifespan)
```

### Run SQL directly

```python
from pg0 import Pg0

with Pg0() as pg:
    pg.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, name TEXT)")
    pg.execute("INSERT INTO users (name) VALUES ('test')")
```

## What You Unlock

Once you drop SQLite compatibility:

```python
# JSONB with indexing
await conn.execute("""
    CREATE TABLE events (
        id SERIAL PRIMARY KEY,
        data JSONB NOT NULL
    );
    CREATE INDEX idx_events_type ON events ((data->>'type'));
""")

# Query JSON directly
events = await conn.fetch("""
    SELECT * FROM events WHERE data->>'type' = 'purchase'
""")

# Arrays
await conn.execute("""
    INSERT INTO users (name, tags) VALUES ($1, $2)
""", "John", ["admin", "active"])

# pgvector for embeddings (included with pg0)
await conn.execute("""
    CREATE EXTENSION vector;
    CREATE TABLE items (
        id SERIAL PRIMARY KEY,
        embedding vector(1536)
    );
""")
```

## Zero-Setup Quick Starts for Your Users

If you maintain an OSS project, this is in my opinion the killer feature. Your users clone the repo, run `pip install`, and everything works:

```python
# your_package/db.py
from pg0 import Pg0
import os

_pg = None

def get_database_url():
    global _pg
    if url := os.getenv("DATABASE_URL"):
        return url  # Production: use provided URL

    # Development: start embedded Postgres
    if _pg is None:
        _pg = Pg0(name="myapp")
        _pg.start()
    return _pg.uri
```

Your README goes from:
```
## Prerequisites
- PostgreSQL 18
- pgvector extension
```

To:
```
pip install your-package
python -m your_package
# That's it. Postgres starts automatically.
```

No Docker Compose files. No "works on my machine." No contributor friction.

## Quick Reference

| Task | Code |
|------|------|
| Start (auto port) | `Pg0().start()` |
| Context manager | `with Pg0() as pg:` |
| Fixed port | `Pg0(port=5433).start()` |
| Named instance | `Pg0(name="test").start()` |
| Get URI | `pg.uri` |
| Run SQL | `pg.execute("SELECT 1")` |
| Stop | `pg.stop()` |
| Stop and delete data | `pg.drop()` |

---

Same database in dev, test, and prod. No Docker. No brew. No SQLite compromises.

[pg0-embedded on PyPI](https://pypi.org/project/pg0-embedded/) | [pg0 CLI](https://github.com/vectorize-io/pg0)
