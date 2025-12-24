+++
date = '2025-12-21T10:00:00+01:00'
draft = false
title = 'TEI for Production: Embeddings and Cross-Encoder Reranking'
tags = ["AI", "agents", "memory", "hindsight", "embeddings", "reranking", "production", "infrastructure"]
+++

**TL;DR**: Hindsight uses two inference-heavy operations: embeddings for vector search and cross-encoder for reranking. Both default to local SentenceTransformers, both can be offloaded to TEI (Text Embeddings Inference) for production. Two separate TEI instances, two separate configurations.

---

## Two Inference Bottlenecks

Hindsight uses two model inference operations:

1. **Embeddings** (`bge-small-en-v1.5`): Generated during `retain()` for every extracted fact. Also used on `recall()` for the query vector, but that's a single embedding per query.
2. **Cross-encoder reranking** (`ms-marco-MiniLM-L-6-v2`): Runs on `recall()` to rerank candidates after RRF fusion.

The heavy embedding load is on `retain()` - if you're storing a conversation with 20 extracted facts, that's 20 embeddings generated. On `recall()`, you only embed the query once.

Both default to local SentenceTransformers. Both become bottlenecks at scale.

## Why Local Inference Doesn't Scale

Hindsight defaults to local inference using SentenceTransformers. This works fine for development - no external dependencies, quick setup, runs on CPU.

The problems start at scale:

- **Resource contention**: Embedding computation competes with your API for CPU/memory
- **No batching optimization**: Each request processes independently
- **Can't scale independently**: Need more embedding throughput? You have to scale the entire Hindsight instance
- **No GPU utilization**: Local provider runs on CPU only

In my experience, local embeddings start showing latency issues around 100+ concurrent users, especially during `retain()` operations that process multiple text chunks.

## Enter TEI

[Text Embeddings Inference](https://github.com/huggingface/text-embeddings-inference) is HuggingFace's production embedding server. It's written in Rust and designed specifically for high-throughput inference.

Key features:

- **Dynamic batching**: Groups incoming requests by token count, not request count. Better hardware utilization.
- **Flash Attention + cuBLAS**: Optimized transformer kernels for NVIDIA GPUs
- **gRPC API**: Lower latency than HTTP for high-frequency calls
- **Prometheus metrics + OpenTelemetry**: Production observability out of the box

The deployment model is simple: TEI runs as a separate service, Hindsight calls it over HTTP.

## Setting Up TEI for Embeddings

### Docker (GPU)

```bash
docker run --gpus all -p 8080:80 \
  -v $PWD/data:/data \
  ghcr.io/huggingface/text-embeddings-inference:1.8 \
  --model-id BAAI/bge-small-en-v1.5
```

The `-v` flag mounts a local directory for model caching - avoids re-downloading weights on every restart.

### Docker (CPU)

```bash
docker run -p 8080:80 \
  -v $PWD/data:/data \
  ghcr.io/huggingface/text-embeddings-inference:cpu-1.6 \
  --model-id BAAI/bge-small-en-v1.5
```

CPU version is slower but useful for environments without GPU access.

### Connecting Hindsight

Two environment variables:

```bash
HINDSIGHT_API_EMBEDDINGS_PROVIDER=tei
HINDSIGHT_API_EMBEDDINGS_TEI_URL=http://localhost:8080
```

Hindsight will now route all embedding calls to TEI.

## Setting Up TEI for Cross-Encoder Reranking

The cross-encoder runs after RRF fusion to rerank candidates. It's a separate model, separate TEI instance.

### Docker

```bash
docker run --gpus all -p 8081:80 \
  -v $PWD/data:/data \
  ghcr.io/huggingface/text-embeddings-inference:1.8 \
  --model-id cross-encoder/ms-marco-MiniLM-L-6-v2
```

Note the different port (8081) - you need both instances running.

### Connecting Hindsight

```bash
HINDSIGHT_API_RERANKER_PROVIDER=tei
HINDSIGHT_API_RERANKER_TEI_URL=http://localhost:8081
```

### Alternative Models

The default `ms-marco-MiniLM-L-6-v2` is optimized for speed. For better accuracy at the cost of latency:

- `cross-encoder/ms-marco-MiniLM-L-12-v2` - deeper model, better ranking
- `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` - multilingual support

Unlike embeddings, cross-encoders don't have a dimension constraint - they output relevance scores, not vectors.

## The 384-Dimension Constraint

This is critical: **Hindsight requires exactly 384-dimensional vectors**. The database schema is fixed to this size.

`bge-small-en-v1.5` outputs 384 dimensions, which is why it's the default. If you want a different model, verify dimensions first:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("your-model-name")
test_embedding = model.encode("test")
print(len(test_embedding))  # Must be 384
```

Models that work:
- `BAAI/bge-small-en-v1.5` (384d)
- `sentence-transformers/all-MiniLM-L6-v2` (384d)

Models that don't work without modification:
- `BAAI/bge-large-en-v1.5` (1024d)
- `text-embedding-3-small` (1536d)

Trying to use a non-384d model will fail at database insertion.

## Performance Tuning

TEI exposes several parameters for tuning throughput:

### Batch Size

```bash
--max-batch-tokens 16384
```

Controls total tokens per batch. Higher values = better GPU utilization but more memory. Start with the default and increase if you have GPU headroom.

### Concurrent Requests

```bash
--max-concurrent-requests 512
```

How many requests TEI queues before rejecting. Set based on expected peak load.

### Tokenization Workers

```bash
--tokenization-workers 4
```

CPU cores dedicated to tokenization. Defaults to auto-detect, but explicit setting helps in containerized environments where core detection can be wrong.

## Production Configuration Example

Here's what I run in production - two TEI instances, one for embeddings, one for reranking:

```bash
# Embeddings TEI
docker run --gpus all -p 8080:80 \
  -v /var/lib/tei/embeddings:/data \
  --restart unless-stopped \
  --name tei-embeddings \
  ghcr.io/huggingface/text-embeddings-inference:1.8 \
  --model-id BAAI/bge-small-en-v1.5 \
  --max-batch-tokens 32768 \
  --max-concurrent-requests 1024 \
  --json-output \
  --prometheus-port 9000

# Reranker TEI
docker run --gpus all -p 8081:80 \
  -v /var/lib/tei/reranker:/data \
  --restart unless-stopped \
  --name tei-reranker \
  ghcr.io/huggingface/text-embeddings-inference:1.8 \
  --model-id cross-encoder/ms-marco-MiniLM-L-6-v2 \
  --max-batch-tokens 16384 \
  --max-concurrent-requests 512 \
  --json-output \
  --prometheus-port 9001
```

Then configure Hindsight:

```bash
# Embeddings
HINDSIGHT_API_EMBEDDINGS_PROVIDER=tei
HINDSIGHT_API_EMBEDDINGS_TEI_URL=http://localhost:8080

# Reranker
HINDSIGHT_API_RERANKER_PROVIDER=tei
HINDSIGHT_API_RERANKER_TEI_URL=http://localhost:8081
```

Key choices:
- Separate Prometheus ports (9000, 9001) for independent monitoring
- Lower batch tokens for reranker - cross-encoder pairs are larger than single embeddings
- `--json-output`: Structured logs for log aggregators

### Health Check

TEI exposes `/health` for liveness probes:

```bash
curl http://localhost:8080/health
```

Returns `200` when ready to serve.

## Kubernetes Deployment

For Kubernetes, deploy both TEI instances as separate Deployments:

```yaml
# Embeddings TEI
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tei-embeddings
spec:
  replicas: 2
  selector:
    matchLabels:
      app: tei-embeddings
  template:
    metadata:
      labels:
        app: tei-embeddings
    spec:
      containers:
      - name: tei
        image: ghcr.io/huggingface/text-embeddings-inference:1.8
        args: ["--model-id", "BAAI/bge-small-en-v1.5", "--port", "80"]
        ports:
        - containerPort: 80
        resources:
          limits:
            nvidia.com/gpu: 1
        readinessProbe:
          httpGet:
            path: /health
            port: 80
---
apiVersion: v1
kind: Service
metadata:
  name: tei-embeddings
spec:
  selector:
    app: tei-embeddings
  ports:
  - port: 8080
    targetPort: 80
---
# Reranker TEI
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tei-reranker
spec:
  replicas: 2
  selector:
    matchLabels:
      app: tei-reranker
  template:
    metadata:
      labels:
        app: tei-reranker
    spec:
      containers:
      - name: tei
        image: ghcr.io/huggingface/text-embeddings-inference:1.8
        args: ["--model-id", "cross-encoder/ms-marco-MiniLM-L-6-v2", "--port", "80"]
        ports:
        - containerPort: 80
        resources:
          limits:
            nvidia.com/gpu: 1
        readinessProbe:
          httpGet:
            path: /health
            port: 80
---
apiVersion: v1
kind: Service
metadata:
  name: tei-reranker
spec:
  selector:
    app: tei-reranker
  ports:
  - port: 8080
    targetPort: 80
```

Then configure Hindsight:

```bash
HINDSIGHT_API_EMBEDDINGS_TEI_URL=http://tei-embeddings:8080
HINDSIGHT_API_RERANKER_TEI_URL=http://tei-reranker:8080
```

Scale each independently based on load patterns - embeddings are called heavily on `retain()` (multiple per call), reranking only on `recall()`.

## Monitoring

TEI exports Prometheus metrics on port 9000 by default. Key metrics to watch:

- `te_request_duration_seconds`: Embedding latency histogram
- `te_batch_size`: Actual batch sizes being processed
- `te_queue_size`: Pending requests in queue

If queue size grows while batch size stays low, you're likely CPU-bound on tokenization. If batch size is high but latency is too, you need more GPU memory or replicas.

## When to Switch

I think local inference is fine for:
- Development and testing
- Single-user applications
- Low-frequency `recall()` calls (< 10/second)

Switch to TEI when:
- Latency matters at scale
- You have multiple Hindsight instances sharing inference
- You want GPU acceleration
- You need independent scaling of embedding/reranking throughput

---

TEI adds operational complexity - two extra services to manage. But it removes both inference bottlenecks. For production workloads, the separation of concerns is worth it: Hindsight handles memory logic, TEI handles the model inference.

[Hindsight documentation](https://hindsight.vectorize.io) | [GitHub](https://github.com/vectorize-io/hindsight)
