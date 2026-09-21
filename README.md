# llm-eval-harness

A small, runnable **LLM evaluation harness** that scores a model's answers against a
versioned ground-truth set and — the important part — classifies every failure by its
**root cause: model / ground-truth / input**. It also includes a tiny
**prompt-injection resistance** battery.

Built to demonstrate a real practice: *most "failures" in an LLM eval are not the model.*
When I audited results this way at a previous role, a large share of the "wrong" answers
were actually **stale or wrong ground-truth**, not the model — so the team stopped tuning
the wrong thing. This repo reproduces that workflow on open, public data.

## Why it exists
"The model is wrong X% of the time" is almost always misleading until you separate:
- **model** — the model genuinely produced a wrong/hallucinated answer,
- **ground-truth** — the expected answer in your dataset is stale/wrong,
- **input** — the test case itself is malformed (bad prompt, missing context).

Reporting a single accuracy number without this split hides the real work.

## Run it (no API key needed)
```bash
pip install -r requirements.txt
python -m src.harness            # runs against the built-in mock model
pytest                           # unit tests for the scoring + root-cause logic
```
The default provider is a **deterministic mock** so the harness runs and the tests are
green out of the box. To evaluate a real model, implement `RealProvider` in
`src/providers.py` (OpenAI-compatible or local Ollama — a stub is included).

## What it outputs
- `results/results.json` and `results/results.csv` — per-case verdict + root cause + reason.
- A console summary: pass rate **and** a breakdown of failures by root cause.

Example summary:
```
20 cases · 14 PASS · 6 FAIL
FAIL by root cause →  model: 3   ground-truth: 2   input: 1
Takeaway: 3 of 6 failures were NOT the model (ground-truth/input).
```

## Structure
- `data/ground_truth_v1.json` — versioned eval set (v1 → v2 shows GT curation over time).
- `src/scoring.py` — pure, unit-tested scoring + root-cause classification.
- `src/providers.py` — mock provider (default) + a real-provider stub.
- `src/harness.py` — the runner.
- `tests/` — pytest tests for the scoring logic.

## Methodology (short)
1. Load a versioned ground-truth set.
2. Get the model's answer per case (mock or real provider).
3. Score correctness (normalized match) → PASS/FAIL.
4. For each FAIL, classify root cause using case metadata + heuristics.
5. Report pass rate **and** the root-cause split — never a bare accuracy number.

Versioning the ground-truth (`v1` → `v2`) is deliberate: an eval set is a living asset;
auditing and correcting it is part of the job, not an afterthought.
