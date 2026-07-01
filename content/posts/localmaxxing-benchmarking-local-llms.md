+++
date = '2026-07-01T07:00:00+01:00'
draft = false
title = "Which local LLM actually runs well on my Mac?"
description = "Open-weight models are having a real moment, so I got curious about where they stand on my own hardware. I don't run them in Hindsight or my daily coding agents yet - this is exploration. Other projects already benchmark local models, but I wanted numbers for my exact laptop, so I built my own."
tags = ["AI", "LLM", "local-llm", "open-source", "apple-silicon", "MLX", "benchmark"]
+++

**TL;DR**: Open-weight models are having a real moment - within a few months of the frontier, much cheaper, good enough for a lot of boring work. I got curious about where they land on my own Mac. I don't use them in Hindsight or my daily coding agents yet, this is exploration. Other projects already benchmark local models, but I wanted real numbers for my exact laptop, so I built my own.

---

Open-source AI is having a real moment right now. The open-weight models coming out of Qwen, Kimi, GLM and DeepSeek are landing within a few months of the closed frontier labs, at a fraction of the cost per token, and for a lot of boring work - extraction, triage, code review - they're becoming the obvious default. Qwen alone crossed a billion downloads on Hugging Face earlier this year. Hard to ignore, so I got curious.

To be clear about where I stand: I'm not running any of this in production. Hindsight still runs on frontier models, and my daily coding agents are still Claude. I haven't moved a single real workload onto a local model yet. This is me kicking the tires, not announcing a switch.

But if I ever want to trust one of these for real work, the first thing I need to know is which model, and how fast it runs on my hardware. Vendors publish quality scores - GSM8K, IFEval, MMLU - and none of that tells you how many tokens per second a model does on an M3 Max, at 4-bit, with four requests in flight, on a 5k-token prompt. That last number is what decides whether a local model is actually usable when an agent is sitting there waiting for it.

There are projects that already collect this - [localmaxxing.com](https://localmaxxing.com/), for one, aggregates tokens-per-second across all kinds of hardware and inference engines, and it's genuinely useful. But I've never been good at trusting a number someone else measured on a setup that isn't mine. I wanted to get my hands dirty and see what actually holds up on my machine, with my quantization, my concurrency, my prompt sizes. So I wrote my own small benchmark, tuned to exactly my laptop - an M3 Max with 36GB.

It ranks models on the things that would matter if I did move work over:

- decode speed at 1 / 2 / 4 / 8 concurrent requests
- prefill and time-to-first-token across input sizes, from ~100 up to 10k tokens
- JSON-schema following, native, no constrained decoding
- quality (IFEval + GSM8K), graded on the actual 4-bit artifact and not the full-precision reference - quantization moves the numbers, and I want the score for the thing I'd actually run

17 models in so far, all 4-bit MLX on the M3 Max. A few things surprised me.

Small is faster than I expected, and holds up. LFM2.5-1.2B does around 235 tok/s single-stream, ~460 at four concurrent requests, and follows JSON schema perfectly. For bulk extraction that would be a great deal.

The MoE sweet spot is real. Qwen3.6-35B-A3B is a 35B model with only ~3B parameters active per token. It lands GSM8K 0.95 at 41 tok/s and still fits in 36GB at 4-bit. That's surprisingly close to big-model reasoning at a speed I could sit in front of.

Top quality still costs you. The dense Qwen3.6-27B scored a perfect GSM8K but crawls at 13.5 tok/s. Fine for a background job, painful interactively.

Here's the dense 27B against the 35B MoE, side by side on the M3 Max - the speed difference is obvious once you watch the tokens land:

<div style="display:flex; justify-content:center; margin:1rem 0;">
  <iframe width="315" height="560" src="https://www.youtube.com/embed/vKrg8YzuYqU" title="Qwen3.5-27B vs Qwen3.6-35B on Apple M3 Max (MLX)" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen style="border-radius:8px; max-width:100%;"></iframe>
</div>

<p style="text-align:center; margin-top:-0.5rem;"><a href="https://www.youtube.com/shorts/vKrg8YzuYqU">▶ Watch the comparison on YouTube</a></p>

Playing with the numbers, the boring 80% of agent work looks very runnable locally. But I still haven't moved anything over, and I want to be honest about why: for the parts I actually depend on - the long agentic loops in Hindsight, the coding I do every day - frontier models are still clearly ahead, and the switching cost isn't worth it to save latency I'm not really paying for. So it stays exploration for now.

In my opinion open models got close enough that this is worth watching seriously, and my own little benchmark is just how I keep track of where they stand on my own machine. When a local model is finally good enough for a real slice of Hindsight, I'd rather know it from the numbers than from the hype. Not yet, though.
