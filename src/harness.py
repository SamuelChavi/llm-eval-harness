"""Eval harness runner.

Usage:
    python -m src.harness                     # mock provider, ground_truth_v1.json
    python -m src.harness --provider real     # your model (implement RealProvider)
    python -m src.harness --data data/ground_truth_v1.json
"""
import argparse
import csv
import json
import os

from .providers import get_provider
from .scoring import classify, summarize

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(data_path: str, provider_name: str) -> list:
    with open(data_path, encoding="utf-8") as f:
        dataset = json.load(f)
    provider = get_provider(provider_name)

    results = []
    for case in dataset["cases"]:
        output = provider.answer(case)
        verdict = classify(case, output)
        results.append({
            "id": case["id"],
            "category": case.get("category", ""),
            "input": case["input"],
            "expected": case.get("expected", ""),
            "output": output,
            "verdict": verdict["verdict"],
            "root_cause": verdict["root_cause"] or "",
            "reason": verdict["reason"],
        })
    return results


def write_results(results: list, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "results.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)


def print_summary(results: list):
    s = summarize(results)
    c = s["fail_by_cause"]
    print(f"\n{s['total']} cases | {s['passed']} PASS | {s['failed']} FAIL")
    print(f"FAIL by root cause ->  model: {c['model']}   "
          f"ground-truth: {c['ground-truth']}   input: {c['input']}")
    not_model = c["ground-truth"] + c["input"]
    if s["failed"]:
        print(f"Takeaway: {not_model} of {s['failed']} failures were NOT the model "
              f"(ground-truth/input).")


def main():
    ap = argparse.ArgumentParser(description="LLM evaluation harness with root-cause classification.")
    ap.add_argument("--data", default=os.path.join(HERE, "data", "ground_truth_v1.json"))
    ap.add_argument("--provider", default="mock", choices=["mock", "real"])
    ap.add_argument("--out", default=os.path.join(HERE, "results"))
    args = ap.parse_args()

    results = run(args.data, args.provider)
    write_results(results, args.out)
    print_summary(results)
    print(f"\nWrote {len(results)} rows to {args.out}/results.json and results.csv")


if __name__ == "__main__":
    main()
