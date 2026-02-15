"""
Generate lotto sets from history using hot/due scoring + all-time frequency (probability).
Apply rules from rules/LOTTO_RULES.json.
"""
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

from lotto.data import (
    MAIN_POOL,
    STRONG_POOL,
    RECENT_DRAWS,
    DEFAULT_CSV_FILENAME,
    get_rules_dir,
    load_history,
)
from lotto.validate import load_rules


def analyze(draws: list, recent_draws: int = RECENT_DRAWS) -> dict:
    """Compute frequency (all-time and recent) and last-seen for each number."""
    n = len(draws)
    main_freq = defaultdict(int)
    main_recent = defaultdict(int)
    main_last_seen = {i: n for i in MAIN_POOL}
    strong_freq = defaultdict(int)
    strong_recent = defaultdict(int)
    strong_last_seen = {i: n for i in STRONG_POOL}

    for idx, (_, mains, strong) in enumerate(draws):
        for m in mains:
            main_freq[m] += 1
            main_last_seen[m] = n - 1 - idx
            if idx >= n - recent_draws:
                main_recent[m] += 1
        strong_freq[strong] += 1
        strong_last_seen[strong] = n - 1 - idx
        if idx >= n - recent_draws:
            strong_recent[strong] += 1

    return {
        "main_freq": main_freq,
        "main_recent": main_recent,
        "main_last_seen": main_last_seen,
        "strong_freq": strong_freq,
        "strong_recent": strong_recent,
        "strong_last_seen": strong_last_seen,
        "num_draws": n,
    }


def score_main(num: int, stats: dict) -> float:
    recent = stats["main_recent"][num]
    last_seen = stats["main_last_seen"][num]
    freq = stats["main_freq"][num]
    n = stats["num_draws"]
    # All-time probability: freq / expected (expected = n * 6/37 per number)
    expected = n * 6 / 37 if n else 1
    prob_score = (freq / expected) * 15  # boosted: historically frequent numbers favored
    hot_score = recent
    due_score = min(last_seen, 100) * 0.5
    return hot_score + due_score + prob_score


def score_strong(num: int, stats: dict) -> float:
    recent = stats["strong_recent"][num]
    last_seen = stats["strong_last_seen"][num]
    freq = stats["strong_freq"][num]
    n = stats["num_draws"]
    # All-time probability: freq / expected (expected = n * 1/7 per number)
    expected = n / 7 if n else 1
    prob_score = (freq / expected) * 8  # boosted for strong pool
    return recent + min(last_seen, 50) * 0.5 + prob_score


def is_consecutive_with_any(num: int, chosen: list[int]) -> bool:
    return (num - 1) in chosen or (num + 1) in chosen


def pick_main_weights(stats: dict, exclude: list[int], no_consecutive: bool = False) -> int | None:
    candidates = [
        m for m in MAIN_POOL
        if m not in exclude and (not no_consecutive or not is_consecutive_with_any(m, exclude))
    ]
    if not candidates:
        return None
    weights = [max(0.1, score_main(m, stats)) for m in candidates]
    total = sum(weights)
    r = random.uniform(0, total)
    for m, w in zip(candidates, weights):
        r -= w
        if r <= 0:
            return m
    return candidates[-1]


def random_main(no_consecutive: bool = False) -> list[int] | None:
    for _ in range(200):
        chosen = []
        pool = list(MAIN_POOL)
        random.shuffle(pool)
        for m in pool:
            if len(chosen) >= 6:
                break
            if m not in chosen and (not no_consecutive or not is_consecutive_with_any(m, chosen)):
                chosen.append(m)
        if len(chosen) == 6:
            return sorted(chosen)
    return None


def pick_strong_weighted(stats: dict) -> int:
    weights = [max(0.1, score_strong(s, stats)) for s in STRONG_POOL]
    total = sum(weights)
    r = random.uniform(0, total)
    for s, w in zip(STRONG_POOL, weights):
        r -= w
        if r <= 0:
            return s
    return random.choice(STRONG_POOL)


def generate_one_set(stats: dict, no_consecutive: bool = False) -> tuple[list[int], int] | None:
    chosen = []
    for _ in range(6):
        m = pick_main_weights(stats, chosen, no_consecutive=no_consecutive)
        if m is None:
            return None
        chosen.append(m)
    return sorted(chosen), pick_strong_weighted(stats)


def passes_rules(mains: list[int], strong: int, rules: dict | None) -> bool:
    if not rules:
        return True
    r = rules.get("rules", {})
    if r.get("sum_6_mains", {}).get("enabled"):
        s = sum(mains)
        lo, hi = r["sum_6_mains"].get("min", 0), r["sum_6_mains"].get("max", 999)
        if not (lo <= s <= hi):
            return False
    if r.get("odd_count", {}).get("enabled"):
        odds = sum(1 for m in mains if m % 2 == 1)
        lo, hi = r["odd_count"].get("min", 0), r["odd_count"].get("max", 6)
        if not (lo <= odds <= hi):
            return False
    if r.get("spread", {}).get("enabled"):
        spread = max(mains) - min(mains)
        lo, hi = r["spread"].get("min", 0), r["spread"].get("max", 36)
        if not (lo <= spread <= hi):
            return False
    if r.get("low_high_balance", {}).get("enabled"):
        low = sum(1 for m in mains if m <= 18)
        lo = r["low_high_balance"].get("low_count_min", 0)
        hi = r["low_high_balance"].get("low_count_max", 6)
        if not (lo <= low <= hi):
            return False
    return True


def main(num_sets: int = 8, csv_path: Path | None = None, seed: int | None = 42) -> None:
    from lotto.data import get_default_csv_path

    path = csv_path or get_default_csv_path()
    if not path or not path.is_file():
        print("No history file found. Draws are generated from historical data; without it we cannot run.")
        print(f"Set LOTTO_CSV or place '{DEFAULT_CSV_FILENAME}' in project data/ or ~/Downloads/.")
        print("Aborting.")
        sys.exit(1)

    print("Loading history from", path)
    draws = load_history(path)
    if not draws:
        print("History file is empty or has no valid rows in current format (6 from 1-37, strong 1-7). Aborting.")
        sys.exit(1)
    print(f"Loaded {len(draws)} draws in current format (6 from 1-37, strong 1-7).")

    stats = analyze(draws)
    print(f"Analyzed last {RECENT_DRAWS} draws + all-time frequency (probability).")

    rules = load_rules()
    rules_dir = get_rules_dir()
    if rules:
        print("Using rules from", rules_dir / "LOTTO_RULES.json")

    if seed is not None:
        random.seed(seed)
    no_consecutive = rules.get("rules", {}).get("no_consecutive_main_numbers", False) if rules else False
    print("\n---", num_sets, "sets (6 main + 1 strong) ---\n")
    max_attempts = 200

    for i in range(num_sets):
        mains, strong = None, None
        for _ in range(max_attempts):
            result = generate_one_set(stats, no_consecutive=no_consecutive)
            if result is not None and passes_rules(result[0], result[1], rules):
                mains, strong = result
                break
        if mains is None:
            for _ in range(100):
                cand = random_main(no_consecutive=no_consecutive)
                if cand and passes_rules(cand, 1, rules):
                    mains = cand
                    strong = pick_strong_weighted(stats)
                    break
            if mains is None:
                mains = random_main(no_consecutive=no_consecutive)
            mains = mains if mains else sorted(random.sample(MAIN_POOL, 6))
            strong = strong if strong is not None else pick_strong_weighted(stats)
        print(f"Set {i+1}:  {mains}  |  Strong: {strong}")
    print("\n(Each set: 6 numbers 1-37, then one number 1-7 for the extra/strong number.)")
