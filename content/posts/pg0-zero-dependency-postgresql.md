+++
date = '2025-11-26T15:00:00+01:00'
draft = false
title = 'pg0: zero-dependency PostgreSQL for development'
tags = ["database", "postgresql", "tools", "developer-experience"]
+++

**TL;DR**: pg0 is a single-binary CLI that downloads and runs PostgreSQL 16 + pgvector locally with zero installation friction. No brew, apt, or Docker-just a binary that handles everything.

---

At Vectorize, we just released [pg0](https://github.com/vectorize-io/pg0). Here's why it exists.

## The Problem

If you run PostgreSQL in production, you have two options for local development:

**Option 1: Use SQLite locally, PostgreSQL in production**

This is the common pattern. SQLite is zero-setup, but now you're managing two different databases. The problems:
- Different SQL dialects (SQLite's `AUTOINCREMENT` vs Postgres's `SERIAL`)
- Different performance characteristics (what's fast in SQLite might be slow in Postgres)
- Different query planners (optimization strategies diverge)
- Different type systems (Postgres has arrays, JSONB, custom types)
- Production bugs that don't reproduce locally

You end up with workarounds, abstraction layers, and "this works in SQLite but breaks in Postgres" surprises.

**Option 2: Install PostgreSQL locally**

Setting up PostgreSQL for local development has too much friction:

**Traditional installation** (Homebrew, apt, etc.):
```bash
brew install postgresql@16
brew services start postgresql@16
psql postgres -c "CREATE EXTENSION vector;"
# Wait, pgvector isn't installed
brew install pgvector
# Now configure paths, restart services...
```

**Docker approach**:
```bash
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres ankane/pgvector
# Works, but now you're managing containers for a simple dev database
# Data persistence requires volume mounts
# Multiple instances need port juggling
```

For AI/vector workloads, you also need pgvector. That's another dependency to install, configure, and keep compatible with your PostgreSQL version.

This is too much overhead for "I just want to test a query" or "I need a local Postgres for development."

## The Solution

pg0 is a single binary that downloads and manages PostgreSQL for you:

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/vectorize-io/pg0/main/install.sh | bash

# Start PostgreSQL
pg0 start

# Use psql (bundled, no separate install)
pg0 psql -c "CREATE EXTENSION vector;"
```

That's it. No system dependencies, no Docker, no configuration files. The binary downloads PostgreSQL 16 and pgvector on first run, caches them in `~/.pg0/`, and manages everything.

**Multi-instance support** is built-in. Run multiple PostgreSQL instances simultaneously, each with independent data and configuration:

```bash
pg0 start --name dev --port 5432
pg0 start --name test --port 5433
pg0 psql --name dev
```

## How It Works

On first execution, pg0 downloads PostgreSQL 16 binaries and pre-compiled pgvector, caching them in `~/.pg0/installation/`. Each instance stores data in `~/.pg0/instances/<name>/data/`, persisting between restarts.

The defaults are optimized for vector workloads (`shared_buffers=256MB`, `maintenance_work_mem=512MB`), but you can override any PostgreSQL configuration via the `-c` flag.

For detailed usage, configuration options, and advanced features, see the [GitHub repository](https://github.com/vectorize-io/pg0).

## Why This Matters

**SQLite alternative for Postgres users**: If you run PostgreSQL in production, pg0 lets you run the same database locally without installation friction. Same SQL dialect, same query planner, same type system. No workarounds, no abstraction layers, no surprises when you deploy. The SQLite tradeoff (easy local dev vs production compatibility) is gone.

**For vector/AI development**: You need PostgreSQL + pgvector running quickly. pg0 bundles both and optimizes defaults for vector operations. No time spent on installation or configuration.

**For testing**: Spin up isolated instances for test suites without Docker overhead or worrying about port conflicts with your main dev database.

**For CI/CD**: A single binary download in CI is faster and simpler than installing PostgreSQL through package managers or pulling Docker images.

**For onboarding**: New engineers clone the repo, run `pg0 start`, and have a working database. No "install Postgres first" in setup docs.

**Programmatic control**: The CLI is easy to manage from your application code. You can start/stop instances, run queries, and manage lifecycle directly:

```python
import subprocess

# Start instance
subprocess.run(["pg0", "start", "--name", "test", "--port", "5433"])

# Run migrations
subprocess.run(["pg0", "psql", "--name", "test", "-f", "schema.sql"])

# Run tests with isolated database
run_tests()

# Clean up
subprocess.run(["pg0", "stop", "--name", "test"])
```

We'll likely release a PyPI package in the future to make this even cleaner with a native Python API.

## Cross-Platform

Works on:
- macOS (Apple Silicon)
- Linux (x86_64)
- Windows (x64)

The binary downloads the right PostgreSQL build for your platform automatically.

## What It's Not

pg0 is for **development and testing**, not production. It's optimized for:
- Fast setup
- Zero configuration
- Local workflows

For production, use managed PostgreSQL (RDS, Cloud SQL, etc.) or a proper installation with backups, replication, and monitoring.

## Get Started

```bash
curl -fsSL https://raw.githubusercontent.com/vectorize-io/pg0/main/install.sh | bash
pg0 start
pg0 psql -c "CREATE EXTENSION vector;"
```

For more examples, configuration options, and advanced usage, check the [GitHub repository](https://github.com/vectorize-io/pg0).

---

This came out of building [Vectorize.io](https://vectorize.io), where we needed quick PostgreSQL + pgvector instances for testing and development. The friction of traditional installation was slowing us down, so we built pg0.

MIT licensed. Contributions welcome.
