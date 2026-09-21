"""Pure, unit-tested scoring + root-cause classification for the eval harness.

The point of this module: a wrong answer is NOT automatically the model's fault.
Every failure is classified into one of three root causes so the report tells the
truth about where the problem is.
"""
import re

ROOT_MODEL = "model"
ROOT_GROUND_TRUTH = "ground-truth"
ROOT_INPUT = "input"


def normalize(text) -> str:
    """Lowercase, strip punctuation, collapse whitespace — for lenient matching."""
    if text is None:
        return ""
    t = str(text).lower().strip()
    t = re.sub(r"[^\w\s]", " ", t)          # drop punctuation
    t = re.sub(r"\s+", " ", t).strip()      # collapse spaces
    return t


def is_correct(output, expected) -> bool:
    """A lenient check: the normalized expected answer appears in the normalized output
    (handles 'Paris' vs 'The capital is Paris.'), or they match exactly."""
    o, e = normalize(output), normalize(expected)
    if not e:
        return False
    return e == o or e in o


def classify(case: dict, output: str) -> dict:
    """Return {verdict, root_cause, reason} for one case+output.

    Order matters:
      1. malformed input  -> can't fairly evaluate -> root cause = input
      2. correct          -> PASS
      3. wrong + suspect ground-truth -> root cause = ground-truth
      4. wrong otherwise  -> root cause = model
    """
    if case.get("malformed"):
        return {
            "verdict": "FAIL",
            "root_cause": ROOT_INPUT,
            "reason": case.get("malformed_note", "Test case input is malformed; not evaluable."),
        }

    if is_correct(output, case.get("expected")):
        return {"verdict": "PASS", "root_cause": None, "reason": "Output matches expected."}

    if case.get("gt_suspect"):
        return {
            "verdict": "FAIL",
            "root_cause": ROOT_GROUND_TRUTH,
            "reason": case.get("gt_note", "Ground-truth is suspect; the expected value may be stale/wrong."),
        }

    return {
        "verdict": "FAIL",
        "root_cause": ROOT_MODEL,
        "reason": "Model output does not match a trusted expected answer.",
    }


def summarize(results: list) -> dict:
    """Aggregate a list of per-case result dicts into counts."""
    total = len(results)
    passed = sum(1 for r in results if r["verdict"] == "PASS")
    failed = total - passed
    by_cause = {ROOT_MODEL: 0, ROOT_GROUND_TRUTH: 0, ROOT_INPUT: 0}
    for r in results:
        if r["verdict"] == "FAIL" and r["root_cause"] in by_cause:
            by_cause[r["root_cause"]] += 1
    return {"total": total, "passed": passed, "failed": failed, "fail_by_cause": by_cause}
