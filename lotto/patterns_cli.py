"""CLI for patterns: lotto-patterns [csv_path]."""
import sys
from pathlib import Path
from lotto.patterns import main as patterns_main

def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    result = patterns_main(csv_path=path)
    if result is None:
        sys.exit(1)


if __name__ == "__main__":
    main()
