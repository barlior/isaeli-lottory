"""
Validate a lotto set (6 mains + 1 strong) against LOTTO_RULES.json.
"""
import json
from pathlib import Path

from lotto.data import get_rules_dir


def _rules_path() -> Path:
    return get_rules_dir() / "LOTTO_RULES.json"


def load_rules() -> dict | None:
    """Load rules from rules/LOTTO_RULES.json. Returns None if missing or invalid."""
    path = _rules_path()
    if not path.is_file():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def has_consecutive(mains: list[int]) -> bool:
    s = set(mains)
    for m in mains:
        if (m - 1) in s or (m + 1) in s:
            return True
    return False


def validate_set(
    mains: list[int], strong: int | None, rules: dict | None
) -> tuple[bool, list[str]]:
    """
    Check set against rules.
    Returns (ok: bool, messages: list). rules may be None (then only format checks).
    """
    msg = []
    if len(mains) != 6 or len(set(mains)) != 6 or not all(1 <= m <= 37 for m in mains):
        return False, ["Main numbers must be 6 distinct integers in 1–37."]
    if strong is None or not (1 <= strong <= 7):
        return False, ["Strong number must be in 1–7."]

    r = (rules or {}).get("rules", {})

    if r.get("no_consecutive_main_numbers"):
        if has_consecutive(mains):
            msg.append("FAIL: set has consecutive main numbers (e.g. 10,11).")
        else:
            msg.append("OK: no consecutive main numbers.")

    sum_cfg = r.get("sum_6_mains", {})
    if sum_cfg.get("enabled"):
        s = sum(mains)
        lo, hi = sum_cfg.get("min", 0), sum_cfg.get("max", 999)
        if lo <= s <= hi:
            msg.append(f"OK: sum_6_mains={s} in [{lo}, {hi}].")
        else:
            msg.append(f"FAIL: sum_6_mains={s} outside [{lo}, {hi}].")

    odd_cfg = r.get("odd_count", {})
    if odd_cfg.get("enabled"):
        odds = sum(1 for m in mains if m % 2 == 1)
        lo, hi = odd_cfg.get("min", 0), odd_cfg.get("max", 6)
        if lo <= odds <= hi:
            msg.append(f"OK: odd_count={odds} in [{lo}, {hi}].")
        else:
            msg.append(f"FAIL: odd_count={odds} outside [{lo}, {hi}].")

    spread_cfg = r.get("spread", {})
    if spread_cfg.get("enabled"):
        spread = max(mains) - min(mains)
        lo, hi = spread_cfg.get("min", 0), spread_cfg.get("max", 36)
        if lo <= spread <= hi:
            msg.append(f"OK: spread={spread} in [{lo}, {hi}].")
        else:
            msg.append(f"FAIL: spread={spread} outside [{lo}, {hi}].")

    low_cfg = r.get("low_high_balance", {})
    if low_cfg.get("enabled"):
        low = sum(1 for m in mains if m <= 18)
        lo, hi = low_cfg.get("low_count_min", 0), low_cfg.get("low_count_max", 6)
        if lo <= low <= hi:
            msg.append(f"OK: low_count(1-18)={low} in [{lo}, {hi}].")
        else:
            msg.append(f"FAIL: low_count={low} outside [{lo}, {hi}].")

    fails = [m for m in msg if m.startswith("FAIL")]
    return len(fails) == 0, msg
