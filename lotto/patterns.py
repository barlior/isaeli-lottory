"""
Learn patterns from Israeli Lotto history CSV; used to build/refresh rule files.
"""
from collections import defaultdict
from pathlib import Path

from lotto.data import MAIN_POOL, STRONG_POOL, DEFAULT_CSV_FILENAME, load_history, get_default_csv_path


def has_consecutive(mains: list[int]) -> bool:
    s = set(mains)
    for m in mains:
        if (m - 1) in s or (m + 1) in s:
            return True
    return False


def analyze_patterns(draws: list) -> dict:
    n = len(draws)
    if n == 0:
        return {}

    main_freq = defaultdict(int)
    strong_freq = defaultdict(int)
    sums = []
    odd_counts = []
    low_counts = []
    spreads = []
    consecutive_count = 0
    gap_counts = defaultdict(int)

    for _, mains, strong in draws:
        for m in mains:
            main_freq[m] += 1
        strong_freq[strong] += 1
        sums.append(sum(mains))
        odd_counts.append(sum(1 for m in mains if m % 2 == 1))
        low_counts.append(sum(1 for m in mains if m <= 18))
        spreads.append(mains[-1] - mains[0])
        if has_consecutive(mains):
            consecutive_count += 1
        for i in range(len(mains) - 1):
            gap_counts[mains[i + 1] - mains[i]] += 1

    sums_sorted = sorted(sums)
    spread_sorted = sorted(spreads)
    odd_dist = defaultdict(int)
    for o in odd_counts:
        odd_dist[o] += 1
    low_dist = defaultdict(int)
    for l in low_counts:
        low_dist[l] += 1

    def pct(s: list, p: float):
        idx = max(0, int(len(s) * p / 100) - 1)
        return s[min(idx, len(s) - 1)]

    return {
        "num_draws": n,
        "consecutive": {
            "draws_with_at_least_one_consecutive_pair": consecutive_count,
            "pct": round(100.0 * consecutive_count / n, 1),
        },
        "sum_6_mains": {
            "min": min(sums),
            "max": max(sums),
            "mean": round(sum(sums) / n, 1),
            "p5": pct(sums_sorted, 5),
            "p25": pct(sums_sorted, 25),
            "p50": pct(sums_sorted, 50),
            "p75": pct(sums_sorted, 75),
            "p95": pct(sums_sorted, 95),
        },
        "odd_count_per_draw": {
            "distribution": dict(sorted(odd_dist.items())),
            "most_common": max(odd_dist.items(), key=lambda x: x[1])[0],
        },
        "low_count_per_draw": {
            "typical_range": [min(low_counts), max(low_counts)],
            "distribution": dict(sorted(low_dist.items())),
        },
        "spread": {
            "min": min(spreads),
            "max": max(spreads),
            "mean": round(sum(spreads) / n, 1),
            "p10": pct(spread_sorted, 10),
            "p90": pct(spread_sorted, 90),
        },
        "gap_between_adjacent_numbers": {
            "distribution": dict(sorted(gap_counts.items())),
            "consecutive_gaps_count": gap_counts.get(1, 0),
        },
        "main_frequency": {k: main_freq[k] for k in sorted(main_freq) if 1 <= k <= 37},
        "strong_frequency": {k: strong_freq[k] for k in sorted(strong_freq) if 1 <= k <= 7},
    }


def main(csv_path: Path | None = None) -> dict | None:
    path = csv_path or get_default_csv_path()
    if not path or not path.is_file():
        print(f"No CSV found. Set LOTTO_CSV or place '{DEFAULT_CSV_FILENAME}' in project data/ or ~/Downloads/")
        return None
    print("Loading", path)
    draws = load_history(path)
    print(f"Loaded {len(draws)} draws.")
    p = analyze_patterns(draws)
    if not p:
        print("No data.")
        return None
    print("\n--- Pattern summary ---")
    print("Consecutive: {:.1f}% of draws have at least one consecutive pair".format(p["consecutive"]["pct"]))
    print("Sum of 6 mains: min={} max={} mean={} (p5={} p95={})".format(
        p["sum_6_mains"]["min"], p["sum_6_mains"]["max"], p["sum_6_mains"]["mean"],
        p["sum_6_mains"]["p5"], p["sum_6_mains"]["p95"]))
    print("Odd count per draw: most_common={} distribution={}".format(
        p["odd_count_per_draw"]["most_common"], p["odd_count_per_draw"]["distribution"]))
    print("Low (1-18) per draw: typical range={}".format(p["low_count_per_draw"]["typical_range"]))
    print("Spread (max-min): min={} max={} mean={} (p10={} p90={})".format(
        p["spread"]["min"], p["spread"]["max"], p["spread"]["mean"],
        p["spread"]["p10"], p["spread"]["p90"]))
    print("Gap distribution (adjacent sorted):", dict(sorted(p["gap_between_adjacent_numbers"]["distribution"].items())))
    return p
