# EDA Class — Implementation Plan for Cursor

## Overview

Build a single Python class called `EDA` that accepts a dataset path and an optional target column name, runs a full exploratory data analysis, and writes a detailed `.md` report file.

---

## Table of Contents

1. [Dependencies](#dependencies)
2. [CLI Entry Point](#cli-entry-point)
3. [Class Signature & Constructor](#class-signature--constructor)
4. [Method List](#method-list)
5. [Method Specifications](#method-specifications)
6. [Report Structure](#report-structure)
7. [File Structure](#file-structure)
8. [Edge Cases to Handle](#edge-cases-to-handle)
9. [Data Type Reference](#data-type-reference)

---

## Dependencies

```
pandas
numpy
scipy
scikit-learn
tabulate
openpyxl       # Excel support
```

Install command to include in README:
```bash
pip install pandas numpy scipy scikit-learn tabulate openpyxl
```

---

## CLI Entry Point

At the bottom of the file, outside the class:

```python
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",   required=True,  help="Path to dataset file")
    parser.add_argument("--target",  default=None,   help="Target column name (optional)")
    parser.add_argument("--output",  default=None,   help="Output .md file path (optional)")
    args = parser.parse_args()

    eda = EDA(input_path=args.input, target_col=args.target, output_path=args.output)
    eda.run()
```

---

## Class Signature & Constructor

```python
class EDA:
    def __init__(self, input_path: str, target_col: str = None, output_path: str = None):
```

### Constructor responsibilities:
- Store `input_path`, `target_col`, `output_path`
- If `output_path` is None, default to same directory as input file with name `<filename>_eda_report.md`
- Initialize `self.df = None`
- Initialize `self.col_types = {}` — will map column name → semantic type string
- Initialize `self.warnings = []` — list of warning strings collected throughout analysis
- Initialize `self.report_sections = []` — list of markdown strings to be joined at the end
- Do NOT load data or run analysis in `__init__`

---

## Method List

| Method | Purpose |
|---|---|
| `run()` | Orchestrator — calls all methods in order, then writes the report |
| `_load_data()` | Load dataset from file into `self.df` |
| `_infer_types()` | Detect semantic type for every column, populate `self.col_types` |
| `_detect_task_type()` | If target col given, return `"binary"`, `"multiclass"`, or `"regression"` |
| `_section_overview()` | Dataset-level summary section |
| `_section_target()` | Target column analysis section (skipped if no target) |
| `_section_columns()` | Loop over all columns, call the right per-column method |
| `_analyze_numeric(col)` | Full stats for numeric columns |
| `_analyze_categorical(col)` | Full stats for categorical columns |
| `_analyze_boolean(col)` | Stats for boolean columns |
| `_analyze_datetime(col)` | Stats for datetime columns |
| `_analyze_text(col)` | Basic stats for free-text columns |
| `_analyze_id(col)` | Flag ID-like columns, skip deep analysis |
| `_section_missing()` | Deep missing values analysis section |
| `_section_correlations()` | All correlation types section |
| `_section_outliers()` | Aggregated outlier summary section |
| `_section_warnings()` | Collect and print all data quality warnings |
| `_section_toc()` | Generate table of contents (called last, prepended to report) |
| `_add_warning(msg)` | Helper — appends a string to `self.warnings` |
| `_md_table(df_or_list)` | Helper — returns a markdown table string using `tabulate` |
| `_write_report()` | Join all sections, prepend TOC, write to `.md` file |

---

## Method Specifications

### `run()`
Calls every method in this exact order:
1. `_load_data()`
2. `_infer_types()`
3. `_section_overview()` → append to `self.report_sections`
4. `_section_target()` → append if target col exists
5. `_section_columns()` → append
6. `_section_missing()` → append
7. `_section_correlations()` → append
8. `_section_outliers()` → append
9. `_section_warnings()` → append
10. `_section_toc()` → **prepend** to front of `self.report_sections`
11. `_write_report()`
12. Print: `"Report written to: <output_path>"`

---

### `_load_data()`
- Detect file extension: `.csv`, `.tsv`, `.xlsx`, `.xls`, `.json`, `.parquet`
- For CSV: try `utf-8` first, fallback to `latin-1`; auto-detect separator using `pd.read_csv(sep=None, engine='python')`
- For others: use the appropriate `pd.read_*` method
- Raise `ValueError` with a clear message if extension is unsupported
- Raise `ValueError` if dataframe is empty after loading
- If `self.target_col` is provided and not in columns, raise `ValueError`
- Store result in `self.df`

---

### `_infer_types()`
Populate `self.col_types` with one of these string values for each column:

| Type String | Criteria |
|---|---|
| `"numeric_continuous"` | numeric dtype AND unique count > 20 |
| `"numeric_discrete"` | numeric dtype AND unique count <= 20 |
| `"categorical"` | object/string dtype OR any dtype with unique count <= 20 (and not boolean) |
| `"boolean"` | exactly 2 unique non-null values (including 0/1, True/False, yes/no, y/n) |
| `"datetime"` | dtype is datetime, OR `pd.to_datetime()` succeeds on > 80% of non-null values |
| `"text"` | object dtype AND average word count per value > 3 AND unique ratio > 0.5 |
| `"id_like"` | unique count == total row count OR unique ratio > 0.99 |

Rules:
- Check `"id_like"` first — it overrides everything else
- Check `"boolean"` before `"categorical"`
- Try datetime parsing only on object columns not already classified
- For columns where dtype is numeric but pandas stored as object (string numbers): attempt `pd.to_numeric()` — if it succeeds on > 90% of values, reclassify and convert; add a warning

---

### `_detect_task_type()`
Only called if `self.target_col` is not None. Returns a string:
- `"binary"` — 2 unique non-null values in target column
- `"multiclass"` — 3 to 20 unique non-null values, dtype is object or integer
- `"regression"` — numeric dtype with > 20 unique values
- `"unknown"` — fallback

---

### `_section_overview()`
Produces a section with the following, all formatted as markdown:

- **File info**: file name, file size in KB/MB, number of rows, number of columns
- **Memory usage**: `df.memory_usage(deep=True).sum()` formatted in KB/MB
- **Missing values**: total missing cells (count + % of all cells)
- **Duplicate rows**: count + % of total rows; list first 3 duplicate row indices if any
- **Column type breakdown**: count of each semantic type (e.g. "4 numeric_continuous, 2 categorical, 1 datetime")
- **Column summary table**: one row per column with columns `[Column, Inferred Type, Pandas Dtype, Missing Count, Missing %]`

---

### `_section_target()`
Only runs if `self.target_col` is given. Calls `_detect_task_type()` and branches:

**If binary or multiclass:**
- Task type label
- Class value counts table: `[Class, Count, Percentage]`
- Imbalance warning if minority class < 10% of total → call `_add_warning()`
- Missing values in target column

**If regression:**
- Task type label
- Descriptive stats: count, mean, median, std, min, max, skewness, kurtosis
- Percentiles: 5th, 25th, 75th, 95th
- Outlier count (IQR method)
- Missing values in target column

---

### `_section_columns()`
Iterates over every column in `self.df`. For each column, calls the appropriate method based on `self.col_types[col]`:

| Type | Method Called |
|---|---|
| `numeric_continuous` or `numeric_discrete` | `_analyze_numeric(col)` |
| `categorical` | `_analyze_categorical(col)` |
| `boolean` | `_analyze_boolean(col)` |
| `datetime` | `_analyze_datetime(col)` |
| `text` | `_analyze_text(col)` |
| `id_like` | `_analyze_id(col)` |

Each method returns a markdown string. Append all to `self.report_sections` under a `## Per-Column Analysis` header.

---

### `_analyze_numeric(col)`
Returns a markdown subsection `### col_name` with:
- Inferred type, pandas dtype
- Count of non-null values, missing count + %
- Unique value count
- Min, max, mean, median, mode
- Standard deviation, variance
- Skewness — flag `⚠️ High skew` if |skew| > 1; flag `⚠️ Severe skew` if |skew| > 2; call `_add_warning()`
- Kurtosis
- Percentiles: 1st, 5th, 25th, 75th, 95th, 99th — as a small table
- IQR outlier count: values below `Q1 - 1.5*IQR` or above `Q3 + 1.5*IQR`; flag if > 5%
- Z-score outlier count: values where |z| > 3
- Zero count + % of non-null values
- Negative count + % (only show if negatives exist)
- For `numeric_discrete` only: full value counts table `[Value, Count, %]`

---

### `_analyze_categorical(col)`
Returns a markdown subsection `### col_name` with:
- Inferred type, pandas dtype
- Count of non-null values, missing count + %
- Unique value count (cardinality)
- Warning if cardinality > 50 → call `_add_warning()`
- Warning if cardinality == number of rows → call `_add_warning()` (reclassify note)
- Mode (most frequent value)
- Least frequent value and its count
- Top 10 value counts table: `[Value, Count, Percentage]`
- If more than 10 unique values, note "Showing top 10 of N unique values"

---

### `_analyze_boolean(col)`
Returns a markdown subsection `### col_name` with:
- Inferred type, detected true/false values
- Missing count + %
- Value counts table: `[Value, Count, Percentage]`
- True ratio (proportion of truthy values)

---

### `_analyze_datetime(col)`
Returns a markdown subsection `### col_name` with:
- Inferred type
- Missing count + %
- Earliest date, latest date, total range in days
- Most common year (value counts top 3)
- Most common month (value counts top 3)
- Most common day of week (value counts top 3)
- Is monotonically increasing: yes/no
- Time gaps between consecutive values: min gap, max gap, mean gap (formatted as human-readable duration)

---

### `_analyze_text(col)`
Returns a brief markdown subsection `### col_name` with:
- Flag as text column
- Non-null count, missing count + %
- Character length: min, max, mean
- Word count: min, max, mean
- Empty string count (values that are `""` after stripping)
- Note: "Deep NLP analysis not included"

---

### `_analyze_id(col)`
Returns a brief markdown subsection `### col_name` with:
- Flag: "Likely an identifier column — deep analysis skipped"
- Unique count + unique ratio
- Sample of 5 values

---

### `_section_missing()`
Produces a `## Missing Values` section with:
- Total missing cells across entire dataset
- Table of all columns with any missing values: `[Column, Missing Count, Missing %, Inferred Type]` — sorted by missing % descending
- List of columns with **0%** missing (just the names, comma-separated)
- Columns with **> 50% missing** — flagged individually, call `_add_warning()` for each
- Columns with **100% missing** — flagged as empty columns, call `_add_warning()`
- **Co-occurrence analysis**: for each pair of columns both having missing values, compute the percentage of rows where both are missing simultaneously. Report pairs where co-occurrence > 50% in a table: `[Column A, Column B, Co-missing Rows, Co-missing %]`

---

### `_section_correlations()`
Produces a `## Correlations` section with three subsections:

**Numeric vs Numeric — Pearson Correlation:**
- Compute full correlation matrix on all numeric columns
- Report only pairs with |r| > 0.5, sorted by |r| descending
- Table: `[Feature A, Feature B, Pearson r, Strength]`
- Strength labels: 0.5–0.7 = Moderate, 0.7–0.9 = Strong, > 0.9 = Very Strong
- Flag pairs with |r| > 0.9 as potential multicollinearity → call `_add_warning()`
- If no pairs exceed threshold, write "No strong numeric correlations found"

**Categorical vs Categorical — Cramér's V:**
- Implement Cramér's V from scratch using `scipy.stats.chi2_contingency`
- Compute for all pairs of categorical columns (skip if too many unique values — cardinality > 50)
- Report pairs with V > 0.3, sorted descending
- Table: `[Feature A, Feature B, Cramér's V, Strength]`
- Strength labels: 0.3–0.5 = Moderate, 0.5–0.7 = Strong, > 0.7 = Very Strong

**Feature vs Target (if target column provided):**
- If regression target: Pearson r between each numeric feature and target — table sorted by |r| descending
- If classification target: Cramér's V between each categorical feature and target, and point-biserial correlation between each numeric feature and target
- Table: `[Feature, Metric, Value]` — sorted by absolute value descending

---

### `_section_outliers()`
Produces a `## Outlier Summary` section:
- Aggregate all IQR and Z-score outlier counts computed during `_analyze_numeric()`
- Store these counts in `self` during `_analyze_numeric()` so this method can access them
- Table: `[Column, IQR Outlier Count, IQR Outlier %, Z-score Outlier Count, Z-score Outlier %]`
- Sorted by IQR outlier count descending
- Flag columns where IQR outlier % > 5% → call `_add_warning()`
- If no numeric columns, write "No numeric columns found for outlier analysis"

---

### `_section_warnings()`
Produces a `## ⚠️ Data Quality Warnings` section:
- If `self.warnings` is empty: write "No data quality issues detected ✅"
- Otherwise: numbered list of all warnings in `self.warnings`
- Group warnings by category if possible: Missing Data, Outliers, Correlations, Cardinality, Skewness, Class Imbalance, Other

---

### `_section_toc()`
Builds a Table of Contents by scanning all `##` and `###` headers already added to `self.report_sections`. Returns a markdown TOC string. **Prepend** this to the front of `self.report_sections` after all sections are built. Also prepend a report title `# EDA Report: <filename>` and a generation timestamp.

---

### `_add_warning(msg: str)`
Simple helper:
```python
def _add_warning(self, msg: str):
    self.warnings.append(msg)
```

---

### `_md_table(data, headers)`
Helper that wraps `tabulate`:
```python
from tabulate import tabulate
def _md_table(self, data, headers):
    return tabulate(data, headers=headers, tablefmt="pipe", floatfmt=".4f")
```

---

### `_write_report()`
- Join all strings in `self.report_sections` with `"\n\n"`
- Write to `self.output_path` with `encoding="utf-8"`
- Print confirmation message

---

## Report Structure

The final `.md` file will have this section order:

```
# EDA Report: <filename>
Generated: <timestamp>

## Table of Contents

## 1. Dataset Overview
## 2. Target Column Analysis        ← only if target provided
## 3. Per-Column Analysis
   ### col_1
   ### col_2
   ### ...
## 4. Missing Values
## 5. Correlations
## 6. Outlier Summary
## 7. ⚠️ Data Quality Warnings
```

---

## File Structure

```
eda.py          ← entire implementation, single file, no submodules needed
README.md       ← usage instructions and dependency install command
```

---

## Edge Cases to Handle

| Scenario | How to Handle |
|---|---|
| Empty dataframe | Raise `ValueError` with message after loading |
| All columns are missing | Raise `ValueError` |
| Single column dataset | Run normally, skip correlation sections gracefully |
| Single row dataset | Run normally, note in overview |
| Target column not in dataframe | Raise `ValueError` with column name in message |
| Column with all NaN | Mark as 100% missing, skip stats, call `_add_warning()` |
| Numeric column stored as string (e.g. `"1,000"`) | Attempt `pd.to_numeric(errors='coerce')` after stripping commas; warn if conversion works |
| Division by zero in any percentage calculation | Wrap in try/except or check denominator |
| Correlation computation on < 2 numeric columns | Skip silently and note in section |
| `pd.to_datetime()` raising exceptions | Catch all exceptions, do not classify as datetime |
| Mixed type columns | Flag in warnings, treat as categorical |
| Only one class in target column | Warn: "Target column has only one unique value" |

---

## Data Type Reference

Quick reference for Cursor — the exact type strings used in `self.col_types`:

```python
VALID_TYPES = [
    "numeric_continuous",
    "numeric_discrete",
    "categorical",
    "boolean",
    "datetime",
    "text",
    "id_like",
]
```

---

## Notes for Cursor

- Use f-strings throughout for readability
- All percentage values should be rounded to 2 decimal places
- All float stats should be rounded to 4 decimal places
- Use `tabulate(..., tablefmt="pipe")` for ALL tables — this is GitHub-flavored markdown
- Never use `print()` inside analysis methods — only in `run()` and `_write_report()`
- Every method that appends to `self.report_sections` should add a clear `##` or `###` header
- Add `# ---` horizontal rules between major sections in the output markdown
- The script must work end-to-end with: `python eda.py --input mydata.csv --target label`
