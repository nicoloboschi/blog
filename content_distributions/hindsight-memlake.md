# Hindsight Memlake: agent memory on object storage

Video: https://www.youtube.com/watch?v=B-nAmMq3LB8
Full write-up: https://hindsight.vectorize.io/blog/2026/10/13/memlake

## Twitter / X

**Tweet 1 (hook)**
Agent memory only grows. Postgres pays for every memory twice: once on write, once on every query.

So at Vectorize, we moved Hindsight's memory to S3. 100M memories, <100ms p99.

**Tweet 2 (pain)**
What we measured on Postgres in Hindsight Cloud:
- recall: 7 qps at 33k memories → 1.9 qps at 164k
- ~190 KB of WAL per memory
- ingest capped at 55-80 memories/s
- 65% of the DB was links between memories, mostly index

**Tweet 3 (Memlake)**
Hindsight Memlake: a Rust engine where the bucket is the only source of truth.
- append-only log + immutable segments
- 2 mutable objects, replaced only with conditional writes
- no consensus cluster, no leader, servers are just caches

**Tweet 4 (numbers)**
- 100M memories, 4 servers: p99 73-80ms
- 1,200-1,500 writes/s per bank
- BEIR within 0.3% of a dedicated vector DB
- protocols model-checked in TLA+

**Tweet 5 (link)**
Open-source Hindsight is 1.0 and stays on Postgres. Memlake is in Hindsight Enterprise.
https://hindsight.vectorize.io/blog/2026/10/13/memlake

## LinkedIn

For a year Hindsight stored agent memory in Postgres, and it was the right call. Simple, familiar, good enough.

Then banks got big. On a 4-vCPU primary, recall dropped from 7 queries per second at 33k memories to 1.9 at 164k. Every memory wrote ~190 KB of WAL. Ingest capped at 55-80 memories per second.

The WTF moment: 65% of the database was the table linking memories to each other. Three quarters of that was index, not data.

Agent memory has a strange shape. Tiny records, they only grow, and every recall runs four searches (vector, keyword, graph, time) over the same data. A relational store pays for each memory on write and again on every query.

So at Vectorize, we built Hindsight Memlake. Memory lives in S3 or GCS. Each bank is an append-only log plus immutable segments. Only two objects ever change, and only through conditional writes. No consensus cluster, no lock service. Servers are disposable caches. The protocols are model-checked in TLA+.

Result: 100M memories at 73-80ms p99 on 4 servers, 1,200+ writes/s per bank, retrieval within 0.3% of a dedicated vector DB.

Open-source Hindsight is now 1.0 and stays on Postgres. Memlake is part of Hindsight Enterprise.

https://hindsight.vectorize.io/blog/2026/10/13/memlake
