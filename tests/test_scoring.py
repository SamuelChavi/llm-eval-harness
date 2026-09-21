"""Unit tests for the scoring + root-cause logic (run: pytest)."""
from src.scoring import (
    normalize, is_correct, classify, summarize,
    ROOT_MODEL, ROOT_GROUND_TRUTH, ROOT_INPUT,
)


def test_normalize_strips_punct_and_case():
    assert normalize("  The Capital, is Paris! ") == "the capital is paris"
    assert normalize(None) == ""


def test_is_correct_contains_and_exact():
    assert is_correct("The capital is Paris.", "Paris")
    assert is_correct("100", "100")
    assert not is_correct("It is Lyon.", "Paris")
    assert not is_correct("", "Paris")


def test_classify_pass():
    case = {"id": "x", "expected": "Paris"}
    r = classify(case, "The capital is Paris.")
    assert r["verdict"] == "PASS" and r["root_cause"] is None


def test_classify_model_failure():
    case = {"id": "x", "expected": "299792"}
    r = classify(case, "About 150000 km/s")
    assert r["verdict"] == "FAIL" and r["root_cause"] == ROOT_MODEL


def test_classify_ground_truth_suspect():
    case = {"id": "everest", "expected": "8848", "gt_suspect": True, "gt_note": "stale"}
    r = classify(case, "8849 meters")           # 'wrong' vs stale expected
    assert r["verdict"] == "FAIL" and r["root_cause"] == ROOT_GROUND_TRUTH


def test_classify_malformed_input_wins_first():
    case = {"id": "t", "expected": "n/a", "malformed": True, "gt_suspect": True}
    r = classify(case, "anything")
    assert r["verdict"] == "FAIL" and r["root_cause"] == ROOT_INPUT


def test_summarize_counts():
    results = [
        {"verdict": "PASS", "root_cause": None},
        {"verdict": "FAIL", "root_cause": ROOT_MODEL},
        {"verdict": "FAIL", "root_cause": ROOT_GROUND_TRUTH},
        {"verdict": "FAIL", "root_cause": ROOT_INPUT},
    ]
    s = summarize(results)
    assert s["total"] == 4 and s["passed"] == 1 and s["failed"] == 3
    assert s["fail_by_cause"] == {ROOT_MODEL: 1, ROOT_GROUND_TRUTH: 1, ROOT_INPUT: 1}
