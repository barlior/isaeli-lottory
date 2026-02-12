"""CLI for validate: lotto-validate n1 n2 n3 n4 n5 n6 strong."""
import sys
from lotto.validate import load_rules, validate_set

def main():
    raw = sys.argv[1:]
    if len(raw) != 7:
        print("Usage: lotto-validate n1 n2 n3 n4 n5 n6 strong")
        print("Example: lotto-validate 1 9 12 25 27 31 7")
        sys.exit(2)
    try:
        mains = sorted([int(x) for x in raw[:6]])
        strong = int(raw[6])
    except ValueError:
        print("All arguments must be integers.")
        sys.exit(2)
    rules = load_rules()
    if rules is None:
        print("Warning: rules/LOTTO_RULES.json not found; only format checks apply.")
    ok, messages = validate_set(mains, strong, rules)
    for m in messages:
        print(m)
    sys.exit(0 if ok else 1)
