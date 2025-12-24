# Social Media - TEI for Production: Embeddings and Cross-Encoder

## Twitter/X

### Option 1 - Single (Problem → Solution)
```
Hindsight runs two model inferences:

• Embeddings on retain() - every extracted fact gets embedded
• Cross-encoder on recall() - reranks candidates

Both default to local SentenceTransformers. Both bottleneck at scale.

Solution: TEI (Text Embeddings Inference)
Two instances, two models, independent scaling.

[link]
```

### Option 2 - Single (Quick setup)
```
Production Hindsight needs two TEI instances:

# Embeddings
docker run --gpus all -p 8080:80 \
  ghcr.io/huggingface/text-embeddings-inference:1.8 \
  --model-id BAAI/bge-small-en-v1.5

# Cross-encoder reranking
docker run --gpus all -p 8081:80 \
  ghcr.io/huggingface/text-embeddings-inference:1.8 \
  --model-id cross-encoder/ms-marco-MiniLM-L-6-v2

Point Hindsight at both. Done.

[link]
```

### Option 3 - Thread (Deep dive)
```
1/4
Hindsight runs two model inferences:

1. Embeddings on retain() - every extracted fact gets a vector
2. Cross-encoder on recall() - reranks candidates after RRF fusion

Both default to local CPU inference. Both become bottlenecks.

2/4
At ~100 concurrent users, I saw latency spike on retain() operations.

Root cause: SentenceTransformers running locally, no batching, no GPU, competing with API for CPU.

3/4
Solution: offload both to TEI (Text Embeddings Inference).

Two instances:
• Port 8080: bge-small-en-v1.5 for embeddings
• Port 8081: ms-marco-MiniLM-L-6-v2 for reranking

TEI gives you dynamic batching, GPU acceleration, Prometheus metrics.

4/4
Config:

HINDSIGHT_API_EMBEDDINGS_PROVIDER=tei
HINDSIGHT_API_EMBEDDINGS_TEI_URL=http://localhost:8080

HINDSIGHT_API_RERANKER_PROVIDER=tei
HINDSIGHT_API_RERANKER_TEI_URL=http://localhost:8081

Scale each independently based on load.

[link]
```

### Option 4 - Thread (Practical)
```
1/4
Profiling my Hindsight deployment. retain() was taking 2-3x longer than expected.

Found the culprit: local embedding inference. Every extracted fact needs an embedding.

2/4
A single retain() call can extract 10-20 facts from a conversation. That's 10-20 embedding operations.

SentenceTransformers handles it locally. No GPU. No batching. CPU-bound.

3/4
Deployed two TEI instances:

Embeddings (bge-small-en-v1.5) on port 8080
Reranker (ms-marco-MiniLM-L-6-v2) on port 8081

Same TEI image, different models, different scaling needs.

4/4
Key insight: embeddings are heavy on retain() (many per call). Reranker only on recall().

Scale them independently. Monitor them separately.

retain() latency dropped back to expected range.

[link]
```

---

## LinkedIn

### Option 1 (Technical story)
```
Running Hindsight in production revealed two inference bottlenecks I didn't anticipate.

Two model inferences happen at different stages:
1. Embeddings on retain() - every extracted fact gets a vector (10-20 per call)
2. Cross-encoder on recall() - reranks candidates after RRF fusion

Both default to local SentenceTransformers. For development, this is fine. At scale (~100 concurrent users), latency spiked - especially on retain().

The fix: TEI (Text Embeddings Inference) for both.

TEI is HuggingFace's production inference server. Rust-based, GPU-accelerated, dynamic batching by token count.

You need two instances:

# Embeddings
docker run --gpus all -p 8080:80 \
  ghcr.io/huggingface/text-embeddings-inference:1.8 \
  --model-id BAAI/bge-small-en-v1.5

# Cross-encoder
docker run --gpus all -p 8081:80 \
  ghcr.io/huggingface/text-embeddings-inference:1.8 \
  --model-id cross-encoder/ms-marco-MiniLM-L-6-v2

Then configure Hindsight:

HINDSIGHT_API_EMBEDDINGS_PROVIDER=tei
HINDSIGHT_API_EMBEDDINGS_TEI_URL=http://localhost:8080

HINDSIGHT_API_RERANKER_PROVIDER=tei
HINDSIGHT_API_RERANKER_TEI_URL=http://localhost:8081

Key constraint for embeddings: must output 384 dimensions (schema is fixed). bge-small-en-v1.5 works. Cross-encoders output scores, no dimension constraint.

In my opinion, two extra services is worth it. Hindsight handles memory logic, TEI handles model inference. Scale each independently based on actual load patterns.

Technical breakdown: [link]
```

### Option 2 (Problem-focused)
```
Local model inference doesn't scale for agent memory.

Hindsight runs two inferences at different stages:
→ Embeddings on retain() - every fact extracted gets a vector
→ Cross-encoder on recall() - reranks search candidates

Both default to SentenceTransformers on CPU. At scale:
• CPU contention with API
• No batching optimization
• Can't scale inference independently
• No GPU utilization

Solution: offload both to TEI (Text Embeddings Inference).

Two instances, two models:
• Port 8080: bge-small-en-v1.5 (embeddings, 384d)
• Port 8081: ms-marco-MiniLM-L-6-v2 (reranking)

What you get:
• Dynamic batching by token count
• GPU acceleration (Flash Attention, cuBLAS)
• Independent scaling per model
• Prometheus metrics for monitoring

Key insight: embeddings are heavy on retain() (many per call). Reranker only on recall(). Different load patterns → different scaling needs.

[link]
```
