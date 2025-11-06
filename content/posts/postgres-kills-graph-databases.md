+++
date = '2025-11-06T09:00:00+01:00'
draft = false
title = 'Why PostgreSQL + pg_vector is Going to Kill Graph Databases'
tags = ["postgres", "databases", "graph-databases", "vector-search", "architecture"]
+++

**TL;DR**: Graph databases solved relationship queries at the cost of operational complexity. PostgreSQL with pg_vector and recursive CTEs now handles the same use cases with vector similarity search and SQL, while keeping the operational simplicity and ecosystem maturity of Postgres. Graph databases are becoming a solution looking for a problem.

---

Graph databases had their moment. Neo4j, ArangoDB, TigerGraph—they promised to solve the relationship problem that relational databases supposedly couldn't handle. "Joins are slow," they said. "You need native graph storage for traversals," they preached.

I bought into this for years. Built recommendation engines on Neo4j. Ran fraud detection pipelines on graph databases. Dealt with Cypher queries, graph-specific ORMs, and the operational nightmare of running yet another specialized database.

Then pg_vector landed in PostgreSQL, and I started questioning everything.

## The Graph Database Promise

Graph databases sold themselves on three core use cases:

1. **Relationship traversals** - Finding paths between entities (friends-of-friends, product recommendations)
2. **Pattern matching** - Detecting fraud rings, social clusters, dependency chains
3. **Real-time recommendations** - "People who bought X also bought Y"

The pitch was convincing: relational databases with joins can't handle deep traversals efficiently. You need native graph storage with index-free adjacency for sub-millisecond traversals across millions of relationships.

Here's what that looked like:

```typescript
// Neo4j Cypher query for friend recommendations
const query = `
  MATCH (user:User {id: $userId})-[:FRIENDS_WITH]->(friend)-[:FRIENDS_WITH]->(foaf)
  WHERE NOT (user)-[:FRIENDS_WITH]->(foaf) AND user <> foaf
  RETURN foaf.id, foaf.name, count(*) as mutual_friends
  ORDER BY mutual_friends DESC
  LIMIT 10
`;
```

This worked. But it came with costs nobody talks about:

- **New query language** - Cypher, Gremlin, or whatever proprietary DSL the vendor picked
- **Operational complexity** - Another database to backup, monitor, tune, scale
- **Limited tooling** - No mature ORMs, migration tools, or admin interfaces
- **Data duplication** - Graph DB becomes a secondary store, syncing from primary relational DB
- **Vendor lock-in** - Switching graph databases means rewriting all queries

I spent more time operating graph databases than I saved on query performance.

## What Actually Changed: Vector Similarity Search

The breakthrough wasn't about graphs. It was about **similarity search**.

Most "graph" problems are actually similarity problems in disguise:

- Friend recommendations = finding users similar to your friends
- Product recommendations = finding products similar to purchase history
- Fraud detection = finding transactions similar to known fraud patterns
- Content discovery = finding documents similar to user interests

Traditional graph databases solve this through traversals. Walk the graph, count relationships, find connected nodes. This works, but it's solving similarity through the proxy of explicit relationships.

pg_vector solves it directly: represent entities as embeddings, search by cosine similarity.

Here's the same friend recommendation in PostgreSQL with pg_vector:

```python
import psycopg2
from pgvector.psycopg2 import register_vector

conn = psycopg2.connect(database="myapp")
register_vector(conn)

# Store user embeddings (generated from profile data, interests, behavior)
# embedding = model.encode(user_profile)

# Find similar users
cursor = conn.cursor()
cursor.execute("""
    SELECT id, name, 1 - (embedding <=> %s) as similarity
    FROM users
    WHERE id != %s
    ORDER BY embedding <=> %s
    LIMIT 10
""", (user_embedding, user_id, user_embedding))

recommendations = cursor.fetchall()
```

This does the same job—finds similar users for recommendations—but:

- No graph traversals
- No specialized query language
- No second database to sync
- Same Postgres instance handling transactions, analytics, everything

The key insight: **embeddings capture relationships implicitly**. Two users don't need an explicit "FRIENDS_WITH" edge to be similar. Their embeddings encode behavioral patterns, interests, demographics. Similarity search finds related entities without maintaining explicit relationship graphs.

## Recursive CTEs: When You Actually Need Traversals

"But what about actual graph traversals?" Fair question.

PostgreSQL has had recursive CTEs for years. They handle hierarchical and graph queries just fine:

```sql
-- Find all transitive dependencies in a package manager
WITH RECURSIVE dep_tree AS (
    -- Start with direct dependencies
    SELECT package_id, dependency_id, 1 as depth
    FROM dependencies
    WHERE package_id = 'my-package'

    UNION ALL

    -- Recursively find dependencies of dependencies
    SELECT d.package_id, d.dependency_id, dt.depth + 1
    FROM dependencies d
    JOIN dep_tree dt ON d.package_id = dt.dependency_id
    WHERE dt.depth < 10  -- Prevent infinite loops
)
SELECT DISTINCT dependency_id, depth
FROM dep_tree
ORDER BY depth;
```

This isn't as fast as Neo4j for deep traversals on pure graph workloads. But here's the thing: **most applications don't do deep traversals**. They do 1-2 hop queries at most:

- "Find friends-of-friends" (2 hops)
- "Show related products" (1-2 hops)
- "Detect fraudulent transaction rings" (2-3 hops)

Recursive CTEs handle these fine. Performance difference in practice? Negligible for most workloads when you have proper indexes.

And when you combine recursive CTEs with vector search, you get powerful hybrid queries:

```sql
-- Find similar users who are within 2 degrees of connection
WITH RECURSIVE connections AS (
    SELECT friend_id as user_id, 1 as depth
    FROM friendships
    WHERE user_id = $1

    UNION

    SELECT f.friend_id, c.depth + 1
    FROM friendships f
    JOIN connections c ON f.user_id = c.user_id
    WHERE c.depth < 2
)
SELECT u.id, u.name, 1 - (u.embedding <=> $2) as similarity
FROM users u
JOIN connections c ON u.id = c.user_id
ORDER BY u.embedding <=> $2
LIMIT 10;
```

This combines explicit relationships (social graph) with implicit similarity (embeddings). Try doing that in a graph database without complex multi-model setup.

## The pg_lake Angle: Analytics on Graph Data

Most graph database pitches ignore a critical reality: graphs don't live in isolation. You need analytics.

"How many users joined through friend referrals last month?"
"What's the average cluster size in our fraud detection graph?"
"Which product categories have the strongest cross-purchase relationships?"

These are analytical queries. Graph databases are terrible at them. You end up exporting data to a data warehouse, running Spark jobs, maintaining another sync pipeline.

PostgreSQL with analytical extensions (whether it's pg_lake, DuckDB integration, or just PostgreSQL's built-in aggregates) handles this natively:

```sql
-- Analyze relationship patterns
SELECT
    u1.cohort,
    u2.cohort,
    COUNT(*) as connection_count,
    AVG(1 - (u1.embedding <=> u2.embedding)) as avg_similarity
FROM friendships f
JOIN users u1 ON f.user_id = u1.id
JOIN users u2 ON f.friend_id = u2.id
WHERE f.created_at > NOW() - INTERVAL '30 days'
GROUP BY u1.cohort, u2.cohort
ORDER BY connection_count DESC;
```

Same database. Same SQL. No ETL pipeline. This matters more than people realize.

I've seen teams spend months building data pipelines to export Neo4j data to Snowflake for analytics. With Postgres, it's just another query.

## The Operational Reality Check

Here's what nobody tells you about graph databases: they're expensive to run.

Not just licensing costs (though Neo4j Enterprise pricing is brutal). The hidden costs:

**Team knowledge**: Every new engineer needs to learn Cypher/Gremlin. Documentation is sparse. Stack Overflow has 100x fewer answers than SQL questions.

**Tooling gaps**: No pgAdmin equivalent. No mature schema migration tools. Backup/restore is vendor-specific. Monitoring requires custom instrumentation.

**Data duplication**: Graph DB is rarely your source of truth. It's a read model, synced from Postgres. Now you're maintaining two databases for one use case.

**Scaling complexity**: Sharding graphs is hard. Most workloads don't need it, but when you do, it's exponentially more complex than sharding relational data.

Compare to PostgreSQL:

- Every engineer already knows SQL
- Mature ecosystem: ORMs, migration tools, admin interfaces, monitoring
- Single database for transactional, analytical, and "graph" workloads
- Battle-tested scaling patterns (read replicas, partitioning, sharding)
- Cloud providers have managed Postgres everywhere

In my experience, teams spend 10x more time operating graph databases than they save on query optimization.

## When Graph Databases Still Win (Barely)

I'm not saying graph databases are useless. There are narrow cases where they're still better:

**Deep traversal workloads**: If you're doing 5+ hop traversals regularly (rare), native graph storage wins. Think academic research on social network topology, knowledge graphs with complex reasoning.

**Pure graph algorithms**: PageRank, community detection, shortest path across massive graphs. Specialized graph databases have optimized implementations.

But even these are shrinking:

- DuckDB can run graph algorithms on Postgres data via foreign tables
- Apache AGE adds graph capabilities directly to Postgres
- Most "deep" graph problems are actually batch analytics (run Spark/DuckDB offline)

For 90% of applications claiming they need a graph database, Postgres + pg_vector is enough.

## The Migration Path I'm Taking

I'm actively migrating graph database workloads to Postgres. The pattern:

1. **Generate embeddings** for entities from their features/behavior
2. **Store embeddings** in Postgres with pg_vector indexes
3. **Replace traversal queries** with similarity search
4. **Keep explicit edges** in relational tables when needed, query with recursive CTEs
5. **Run analytics** directly in Postgres

Results so far:
- 40% reduction in infrastructure costs (no separate graph DB cluster)
- 50% faster development (no context switching between SQL and Cypher)
- Same or better query performance for our use cases (recommendation, fraud detection)

Example migration for product recommendations:

**Before (Neo4j):**
```typescript
MATCH (u:User {id: $userId})-[:PURCHASED]->(p1:Product)<-[:PURCHASED]-(other:User)-[:PURCHASED]->(p2:Product)
WHERE NOT (u)-[:PURCHASED]->(p2)
RETURN p2.id, p2.name, count(other) as social_proof
ORDER BY social_proof DESC
LIMIT 10
```

**After (Postgres + pg_vector):**
```sql
-- Purchase history embedding captures behavioral patterns
SELECT p.id, p.name, 1 - (p.embedding <=> u.purchase_embedding) as relevance
FROM products p, users u
WHERE u.id = $1
  AND p.id NOT IN (SELECT product_id FROM purchases WHERE user_id = $1)
ORDER BY p.embedding <=> u.purchase_embedding
LIMIT 10;
```

Simpler. Faster. No second database.

## Conclusion

Graph databases solved a real problem a decade ago when Postgres lacked vector search and embedded analytics was painful. That's no longer true.

In my opinion, the graph database market is heading toward irrelevance. Not because graphs aren't useful—they are. But because PostgreSQL absorbed the capability without the operational overhead.

Vector similarity search handles most "relationship" problems better than explicit graphs. Recursive CTEs handle the rest. Analytical queries work natively. The tooling ecosystem is mature. The operational burden is minimal.

Graph databases are becoming specialized tools for edge cases, not the default choice for relationship-heavy workloads. For most engineering teams, Postgres + pg_vector is the pragmatic answer.

The question isn't whether Postgres can replace graph databases. It already has for most use cases. The question is when teams will realize they don't need the complexity anymore.
