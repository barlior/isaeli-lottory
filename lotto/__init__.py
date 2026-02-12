"""
Israeli Lotto (Pais): generate and validate sets from history.
Game: 6 main numbers from 1-37, 1 strong number from 1-7.
"""
from lotto.data import (
    MAIN_POOL,
    STRONG_POOL,
    DEFAULT_CSV_FILENAME,
    load_history,
    parse_row,
    get_rules_dir,
    get_default_csv_path,
)
from lotto.validate import load_rules, validate_set
from lotto.analysis import analyze, generate_one_set, passes_rules
from lotto.patterns import analyze_patterns

__all__ = [
    "MAIN_POOL",
    "STRONG_POOL",
    "DEFAULT_CSV_FILENAME",
    "load_history",
    "parse_row",
    "get_rules_dir",
    "get_default_csv_path",
    "load_rules",
    "validate_set",
    "analyze",
    "generate_one_set",
    "passes_rules",
    "analyze_patterns",
]
