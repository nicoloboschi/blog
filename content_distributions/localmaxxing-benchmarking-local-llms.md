# Content distribution: Which local LLM actually runs well on my Mac?

## Twitter

### Tweet (main)

Open-weight models are having a real moment. Qwen, Kimi, GLM, DeepSeek landing within months of the frontier, at a fraction of the cost. Qwen crossed a billion HF downloads this year.

So I got curious. To be clear: I don't run any of this in production. Hindsight is still frontier models, my coding agents are still Claude. This is me kicking the tires.

But before I'd trust a local model, I need to know: which one, and how fast on MY hardware? Vendors publish quality scores. Nobody publishes tokens/sec on an M3 Max, at 4-bit, 4 requests in flight, on a 5k-token prompt.

Projects like localmaxxing.com already aggregate this across hardware, and it's useful. But I don't love trusting a number measured on a setup that isn't mine, so I wrote my own benchmark tuned to my exact laptop. It measures:
- decode speed at 1/2/4/8 concurrent requests
- prefill + time-to-first-token by input size
- JSON-schema following, no constrained decoding
- quality (IFEval + GSM8K) on the real 4-bit artifact, not the full-precision one

17 models in, all 4-bit MLX. Surprises:
- LFM2.5-1.2B: ~235 tok/s solo, ~460 at 4 concurrent, perfect JSON schema
- Qwen3.6-35B-A3B (MoE, ~3B active): GSM8K 0.95 at 41 tok/s, fits 36GB
- Dense Qwen3.6-27B: perfect GSM8K but 13.5 tok/s

Boring 80% of agent work looks runnable locally. Haven't moved anything over yet - frontier is still clearly ahead where I depend on it.

[link]

### Alt shorter hook variants
- "Open models are within months of the frontier now. I still don't run them in prod. But I got curious enough to benchmark all of them on my Mac."
- "Vendors tell you how smart a model is. Not how many tokens/sec it does on YOUR laptop. That's the number I needed, so I measured it."
- "A 35B MoE with 3B active doing GSM8K 0.95 at 41 tok/s on a MacBook. Open models are further along than I expected - not far enough for me to switch yet."

## Twitter (thread version)

1/ Open-source AI is having a real moment. Qwen, Kimi, GLM, DeepSeek are landing within months of the closed frontier labs, way cheaper per token. Qwen passed a billion HF downloads this year. Got me curious.

2/ Caveat up front: I don't run any of this in production. Hindsight is still frontier models. My daily coding agents are still Claude. I haven't moved a single real workload to a local model. This is exploration.

3/ But before trusting one, I need to know which model and how fast on my hardware. Vendors publish GSM8K/MMLU/IFEval. None of it tells you tokens/sec on an M3 Max at 4-bit with 4 requests in flight. That's what decides if it's usable.

4/ Projects like localmaxxing.com already aggregate this across hardware. Useful, but I don't love trusting numbers from a setup that isn't mine. So I wrote my own benchmark tuned to my laptop: decode speed at 1/2/4/8 concurrency, prefill/TTFT by input size, schema following, quality on the actual 4-bit artifact.

5/ Surprises (17 models, 4-bit MLX):
- LFM2.5-1.2B: ~235 tok/s, ~460 at 4 concurrent, perfect schema
- Qwen3.6-35B-A3B MoE: GSM8K 0.95 at 41 tok/s, fits 36GB
- Dense 27B: perfect GSM8K but 13.5 tok/s

6/ The boring 80% of agent work looks runnable locally. But I haven't switched - frontier is still clearly ahead in the long agentic loops I depend on. localmaxxing is just how I'll know when that changes. [link]

## LinkedIn

**Story → Problem → WTF moment → Solution → Link**

Open-source AI is having a real moment right now. The open-weight models coming out of Qwen, Kimi, GLM and DeepSeek are landing within a few months of the closed frontier labs, at a fraction of the cost per token. Qwen alone crossed a billion downloads on Hugging Face this year. For a lot of boring work - extraction, triage, code review - open models are becoming the obvious default. So I got curious.

Let me be clear about where I stand though: I'm not running any of this in production. Hindsight still runs on frontier models, and my daily coding agents are still Claude. I haven't moved a single real workload onto a local model yet. This is me kicking the tires, not announcing a switch.

But if I ever want to trust one for real work, the first thing I need to know is which model, and how fast it runs on my hardware.

Vendors publish quality scores - GSM8K, IFEval, MMLU - but nobody tells you how many tokens per second a model does on an M3 Max, at 4-bit, with four requests in flight, on a 5k-token prompt. And that's exactly the number that decides whether a local model is usable when an agent is waiting on it.

The WTF moment: projects like localmaxxing.com already aggregate this kind of data across hardware, and it's genuinely useful - but I've never been good at trusting a number someone else measured on a setup that isn't mine. So I wrote my own small benchmark, tuned to my exact laptop. It ranks models on the things that would matter if I moved work over:
- decode speed at 1 / 2 / 4 / 8 concurrent requests
- prefill and time-to-first-token across input sizes, ~100 up to 10k tokens
- JSON-schema following, native, no constrained decoding
- quality (IFEval + GSM8K), graded on the actual 4-bit artifact, not the full-precision reference

A few surprises from the first 17 models:
- LFM2.5-1.2B does ~235 tok/s single-stream, ~460 at four concurrent requests, perfect JSON schema. Bulk extraction would be sorted.
- Qwen3.6-35B-A3B is a 35B MoE with only ~3B active per token. GSM8K 0.95 at 41 tok/s, fits in 36GB. Big-model reasoning at a speed I could sit in front of.
- The dense Qwen3.6-27B scores a perfect GSM8K but crawls at 13.5 tok/s.

The boring 80% of agent work looks very runnable locally. But I haven't moved anything over, and I'll be honest about why: for the parts I depend on - the long agentic loops in Hindsight, the coding I do daily - frontier models are still clearly ahead, and the switching cost isn't worth it right now.

In my opinion open models got close enough that this is worth watching seriously. My own little benchmark is how I'll know when a local model is finally good enough for a real slice of my stack - from the numbers, not the hype. Not yet, though.

[link]
