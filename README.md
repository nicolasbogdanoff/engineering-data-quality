# Engineering Data Quality

A small, testable Python toolkit for profiling and validating subgrouped engineering data before statistical process control (SPC) analysis.

The project is intentionally narrow: it helps identify structural data problems early, without silently repairing measurements or deciding which observations should be excluded from a control chart.

## Features

- Detects missing subgroup identifiers and duplicate subgroup identifiers.
- Checks that measurement columns are numeric and complete.
- Reports row count, subgroup count, measurement count, and basic numeric summaries.
- Preserves the original data and returns explicit validation issues.
- Provides a simple foundation for CSV/Excel ingestion pipelines and SPC workflows.
- Includes unit tests for valid data and common quality failures.

## Quick start

~~~bash
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -e ".[dev]"
pytest
~~~

## Example

~~~python
import pandas as pd

from engineering_data_quality import profile_frame, validate_subgroups

data = pd.DataFrame(
    {
        "Subgroup": [1, 2, 3],
        "x1": [10.1, 10.0, 10.2],
        "x2": [9.9, 10.1, 10.0],
    }
)

issues = validate_subgroups(data, subgroup_column="Subgroup")
profile = profile_frame(
    data,
    subgroup_column="Subgroup",
    measurement_columns=["x1", "x2"],
)

print(issues)
print(profile["measurement_summary"])
~~~

## Validation rules

The current validator checks:

1. The input is a non-empty pandas DataFrame.
2. The subgroup column exists and contains no missing values.
3. Subgroup identifiers are unique.
4. The selected measurement columns exist.
5. Measurement columns contain no missing values.
6. Measurement columns are numeric.

The toolkit reports issues as structured records with a code, message, and affected column where applicable. It does not drop rows, coerce invalid values, or infer a replacement value.

## Relation to SPC Connect

This toolkit is a companion project for [SPC Connect](https://github.com/nicolasbogdanoff/spc_connect_cloud_app). It addresses the data-readiness stage before subgroup statistics, control limits, and capability indices are calculated.

## Repository layout

| Path | Purpose |
| --- | --- |
| engineering_data_quality/quality.py | Validation and profiling functions |
| engineering_data_quality/__init__.py | Public package interface |
| tests/test_quality.py | Unit tests |
| pyproject.toml | Package metadata and dependencies |

## Scope and limitations

This is a data-readiness utility, not a quality-management system. It does not establish measurement-system adequacy, subgrouping strategy, specification limits, statistical control, or engineering causality. Those decisions remain part of the analysis context.

## Author

Nicolás Mauricio Bogdanoff  
ORCID: https://orcid.org/0009-0004-6275-3013
