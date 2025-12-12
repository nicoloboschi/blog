# Social Media - Drop SQLite: Ship Postgres with Zero External Dependencies

## Twitter/X

### Option 1 (Problem → Solution)
```
"Install PostgreSQL first" in your README = contributor friction

Your Python app uses SQLite in dev, Postgres in prod. The complexity tax:
- if sqlite/else postgres branches everywhere
- Can't use asyncpg (3-5x faster)
- No JSONB, no pgvector
- Bugs that only appear in production

pg0-embedded fixes this. pip install, and Postgres just works.

No Docker. No brew. No system packages.

[link]
```

### Option 2 (Direct)
```
Stop maintaining SQLite compatibility for "convenience"

pg0-embedded = Postgres that ships with your Python package

pip install your-app
python -m your_app
# Postgres starts automatically. pgvector included.

Your users install nothing. Same DB in dev and prod.

[link]
```

### Option 3 (Short)
```
Your Python app shouldn't need "install Postgres" in the README.

pg0-embedded bundles Postgres 18 + pgvector.

pip install → works.

No Docker. No brew. Cross-platform.

[link]
```

---

## LinkedIn

### Option 1 (Story format)
```
I maintained SQLite support in a Python project for 2 years "for convenience."

The cost:
- 20% of the database layer was compatibility glue
- Couldn't use asyncpg (3-5x faster than psycopg2)
- No JSONB, no arrays, no pgvector
- Bugs that only reproduced in production

Why did I keep it? Because "install PostgreSQL" in the README is contributor friction.

Then I found pg0-embedded.

It's a Python package that downloads and runs Postgres for you. No Docker. No system packages. Just pip install.

Your users clone the repo, run pip install, and everything works. Postgres starts automatically. pgvector included.

Same database in dev, test, and prod. Zero external dependencies.

Wrote about the migration path: [link]
```

### Option 2 (Direct value)
```
If you ship a Python package that needs PostgreSQL, your users shouldn't have to install it separately.

pg0-embedded bundles Postgres 16 + pgvector into a pip-installable package.

What changes:

Before:
- README says "install PostgreSQL 16 and pgvector"
- Docker Compose for local dev
- SQLite fallback "for convenience"
- Compatibility branches everywhere

After:
- pip install your-package
- python -m your_package
- Done. Postgres starts automatically.

Cross-platform (macOS, Linux, Windows). Data persists between restarts. Auto port assignment.

Full migration guide: [link]
```
