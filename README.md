# Israeli Lotto (Pais)

Generate and validate Israeli Lotto sets (6 main numbers 1–37, 1 strong number 1–7) using historical CSV data and configurable rules.

## Layout

The **project** folder is `israeli-lotto/`. The **Python package** you import is `lotto` (lives inside `israeli-lotto/lotto/`). That way the project name and the import name are clearly different.

```
israeli-lotto/           # project root
├── pyproject.toml
├── README.md
├── lotto/                # Python package (import lotto)
│   ├── __init__.py
│   ├── data.py
│   ├── analysis.py
│   ├── patterns.py
│   ├── validate.py
│   ├── validate_cli.py
│   ├── patterns_cli.py
│   └── __main__.py
├── rules/
│   ├── LOTTO_RULES.yaml
│   └── LOTTO_RULES.json
└── data/                 # place lotto-history.csv here (no spaces in name)
```

## Install

On macOS (and many Linux setups), the system Python is "externally managed" — use one of these:

**Option A: Virtual environment (recommended)**

```bash
cd israeli-lotto
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Then use `lotto-generate`, `lotto-validate`, `lotto-patterns` from anywhere while the venv is active. To activate the venv again later: `source israeli-lotto/.venv/bin/activate`.

**Option B: Run without installing**

No `pip install` needed. From the project root:

```bash
cd israeli-lotto
python3 -m lotto
python3 -m lotto.validate_cli 1 8 20 23 25 33 6
python3 -m lotto.patterns_cli
```

## CSV file (Mac-friendly name)

Use **`lotto-history.csv`** (no spaces). Put it in:

- `israeli-lotto/data/lotto-history.csv`, or
- `~/Downloads/lotto-history.csv`,

or set `LOTTO_CSV` to the full path. If you have the file as "Lotto 2.csv", rename it:

```bash
mv "/Users/liorba/Downloads/Lotto 2.csv" ~/Downloads/lotto-history.csv
# or into the project:
mv "/Users/liorba/Downloads/Lotto 2.csv" /path/to/israeli-lotto/data/lotto-history.csv
```

## Usage

- **Generate 8 sets** (from history + rules):
  ```bash
  cd israeli-lotto && python3 -m lotto
  # or: lotto-generate   (if installed)
  ```

- **Validate one set**:
  ```bash
  lotto-validate 1 8 20 23 25 33 6
  ```

- **Re-analyze CSV** (pattern stats):
  ```bash
  lotto-patterns
  # or: lotto-patterns /path/to/lotto-history.csv
  ```

## Rules

Edit `rules/LOTTO_RULES.yaml` and keep `rules/LOTTO_RULES.json` in sync. Summary: no consecutive main numbers; sum of 6 mains in [75, 153]; odd count 2–4; spread in [19, 33].
