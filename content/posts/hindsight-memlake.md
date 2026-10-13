+++
date = '2026-10-13T07:00:00+01:00'
draft = false
title = "Hindsight Memlake: agent memory on object storage"
description = "Hindsight Memlake is out today, a Rust storage engine that keeps agent memory in S3 or GCS instead of Postgres. 100M memories, under 100ms p99. Here is why we built it at Vectorize and what it looks like."
tags = ["AI", "agent-memory", "hindsight", "object-storage", "rust", "distributed-systems"]
+++

**TL;DR**: Hindsight Memlake is out today, a new storage engine that keeps agent memory in object storage instead of Postgres. In our tests it serves 100M memories at under 100ms p99, with the bucket as the only source of truth. Open-source Hindsight is now 1.0 and stays on Postgres.

---

Agent memory has a weird shape. Records are tiny, they only grow, and every recall runs four searches at once over the same data: by meaning, by keyword, through links and through time. Postgres handled this well for a long time. In Hindsight Cloud it stopped handling it well once banks got big.

We measured it before deciding anything. On a 4-vCPU primary, recall went from 7 queries per second at 33k memories to 1.9 at 164k. Each memory wrote about 190 KB of WAL across the vector, link and full-text indexes, so ingest topped out at 55-80 memories per second. The table of links between memories was 65% of the database, and three quarters of that was index. Postgres isn't doing anything wrong. It just pays for every memory twice, once on write and once on every query, and a workload that only grows means a bigger primary forever.

So at Vectorize, we built a store for this shape of data. Here's the announcement video:

<div style="display:flex; justify-content:center; margin:1rem 0;">
  <iframe width="560" height="315" src="https://www.youtube.com/embed/B-nAmMq3LB8" title="Introducing Hindsight Memlake: Agent Memory on Object Storage, Built for Billions of Memories" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen style="border-radius:8px; max-width:100%;"></iframe>
</div>

<p style="text-align:center; margin-top:-0.5rem;"><a href="https://www.youtube.com/watch?v=B-nAmMq3LB8">▶ Watch the announcement on YouTube</a></p>

Memlake is written in Rust and plugs into Hindsight's database layer, so agents, SDKs and API calls don't change. It moves only the memory itself to the bucket: memories, links, indexes, documents, mental models. Banks, settings, the job queue and the audit log stay in Postgres, because they are small and relational and that's what Postgres is good at.

The part I like most is how little coordination there is. Each bank is a prefix in the bucket with three kinds of objects:

- an append-only log, one immutable file per write
- segments, small self-contained indexes written once and never touched again
- a manifest and a head pointer, the only two objects that ever change

Those two mutable objects are only replaced with conditional writes. The bucket accepts the new version only if nobody changed it first. That's the whole coordination story: no consensus cluster, no lock service, no leader, and servers never talk to each other. A write lands in the log, the head pointer moves, and only then Hindsight acknowledges it. Indexers turn the log into segments later and publish them by swapping the manifest. Servers are just caches, so losing one costs latency, never data.

Because the safety of everything depends on a few conditional writes racing each other, we didn't trust tests alone. The write, indexing and garbage-collection protocols are specified in TLA+ and model-checked across interleavings. For distributed code like this, I think that's the only way to sleep well.

Some numbers from the benchmarks:

- 100M memories across 20 banks on 4 servers, p99 recall around 73-80ms
- one bank sustains 1,200-1,500 writes per second
- retrieval quality on BEIR within 0.3% of an established vector database
- about two orders of magnitude faster than Postgres on large banks

The tradeoff is cold starts. Opening a bank that isn't cached can take seconds, so servers now preload in the background. And under ~50k memories per bank, Postgres is still a fine choice. That's why open-source Hindsight, now 1.0, keeps running on it.

Memlake is part of Hindsight Enterprise, and most of Hindsight Cloud already runs on it. The full write-up, with the architecture, the cost model and all the charts, is on the [Hindsight blog](https://hindsight.vectorize.io/blog/2026/10/13/memlake).

In my opinion object storage is the right home for memory that never stops growing. It took us a year of watching Postgres strain to get here, and I'm happy with where it landed.
