"""
Load and parse Israeli Lotto history CSV (current format: 6 from 1–37, strong 1–7).
"""
import csv
import os
from pathlib import Path

# Package root: directory containing the 'lotto' package (parent of this file's parent)
_PACKAGE_ROOT = Path(__file__).resolve().parent.parent

MAIN_POOL = list(range(1, 38))   # 1-37
STRONG_POOL = list(range(1, 8))  # 1-7
NUM_MAINS = 6
NUM_STRONG = 1
RECENT_DRAWS = 500  # default window for "recent" frequency


def get_rules_dir() -> Path:
    """Directory containing LOTTO_RULES.yaml and LOTTO_RULES.json."""
    return _PACKAGE_ROOT / "rules"


DEFAULT_CSV_FILENAME = "lotto-history.csv"


def get_default_csv_path() -> Path | None:
    """Default CSV path: env LOTTO_CSV, or project data/lotto-history.csv, or ~/Downloads/lotto-history.csv."""
    env = os.environ.get("LOTTO_CSV")
    if env:
        p = Path(env)
        if p.is_file():
            return p
    for candidate in (
        _PACKAGE_ROOT / "data" / DEFAULT_CSV_FILENAME,
        Path.home() / "Downloads" / DEFAULT_CSV_FILENAME,
    ):
        if candidate.is_file():
            return candidate
    return None


def parse_row(row: list) -> tuple[int, list[int], int] | None:
    """Parse a CSV row. Return (draw_id, [6 mains], strong) or None if invalid."""
    if len(row) < 9:
        return None
    try:
        draw_id = int(row[0].strip())
        mains = [int(row[i].strip()) for i in range(2, 8)]
        strong_raw = row[8].strip()
        strong = int(strong_raw) if strong_raw else None
    except (ValueError, IndexError):
        return None
    if strong is None:
        return None
    if not all(1 <= m <= 37 for m in mains):
        return None
    if not (1 <= strong <= 7):
        return None
    return (draw_id, sorted(mains), strong)


def load_history(path: Path | str) -> list[tuple[int, list[int], int]]:
    """Load all valid draws (current game format) from CSV. Sorted by draw_id ascending."""
    path = Path(path)
    if not path.is_file():
        return []
    draws = []
    for enc in ("utf-8", "utf-8-sig", "cp1255", "latin-1"):
        try:
            with open(path, encoding=enc) as f:
                r = csv.reader(f)
                next(r, None)  # header
                for row in r:
                    if len(row) < 9:
                        continue
                    parsed = parse_row(row)
                    if parsed:
                        draws.append(parsed)
            break
        except (UnicodeDecodeError, OSError):
            continue
    draws.sort(key=lambda x: x[0])
    return draws
