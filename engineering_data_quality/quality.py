from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence

import pandas as pd
from pandas.api.types import is_numeric_dtype


@dataclass(frozen=True)
class ValidationIssue:
    """A non-destructive data-quality finding."""

    code: str
    message: str
    column: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        return asdict(self)


def _measurement_columns(
    frame: pd.DataFrame,
    subgroup_column: str,
    measurement_columns: Sequence[str] | None,
) -> list[str]:
    if measurement_columns is None:
        return [column for column in frame.columns if column != subgroup_column]
    return list(measurement_columns)


def validate_subgroups(
    frame: pd.DataFrame,
    subgroup_column: str,
    measurement_columns: Sequence[str] | None = None,
) -> list[ValidationIssue]:
    """Return explicit validation findings without changing the input frame."""

    if not isinstance(frame, pd.DataFrame):
        raise TypeError("frame must be a pandas DataFrame.")

    issues: list[ValidationIssue] = []
    if frame.empty:
        issues.append(
            ValidationIssue("empty-data", "The input DataFrame contains no rows.")
        )

    if subgroup_column not in frame.columns:
        return issues + [
            ValidationIssue(
                "missing-subgroup-column",
                f"The subgroup column {subgroup_column!r} does not exist.",
                subgroup_column,
            )
        ]

    subgroup = frame[subgroup_column]
    if subgroup.isna().any():
        issues.append(
            ValidationIssue(
                "missing-subgroup",
                "The subgroup column contains missing identifiers.",
                subgroup_column,
            )
        )

    if subgroup.duplicated().any():
        issues.append(
            ValidationIssue(
                "duplicate-subgroup",
                "The subgroup column contains duplicate identifiers.",
                subgroup_column,
            )
        )

    selected_measurements = _measurement_columns(
        frame,
        subgroup_column,
        measurement_columns,
    )
    if not selected_measurements:
        issues.append(
            ValidationIssue(
                "no-measurements",
                "At least one measurement column is required.",
            )
        )

    for column in selected_measurements:
        if column not in frame.columns:
            issues.append(
                ValidationIssue(
                    "missing-measurement-column",
                    f"The measurement column {column!r} does not exist.",
                    column,
                )
            )
            continue

        series = frame[column]
        if series.isna().any():
            issues.append(
                ValidationIssue(
                    "missing-measurement",
                    "The measurement column contains missing values.",
                    column,
                )
            )
        if not is_numeric_dtype(series):
            issues.append(
                ValidationIssue(
                    "non-numeric-measurement",
                    "The measurement column is not numeric.",
                    column,
                )
            )

    return issues


def profile_frame(
    frame: pd.DataFrame,
    subgroup_column: str,
    measurement_columns: Sequence[str] | None = None,
) -> dict[str, object]:
    """Return a compact profile while preserving the original data."""

    selected_measurements = _measurement_columns(
        frame,
        subgroup_column,
        measurement_columns,
    )
    issues = validate_subgroups(
        frame,
        subgroup_column,
        selected_measurements,
    )

    missing_columns = [
        issue
        for issue in issues
        if issue.code in {"missing-subgroup-column", "missing-measurement-column"}
    ]
    if missing_columns:
        raise ValueError(missing_columns[0].message)

    summary = frame[selected_measurements].describe().T
    summary = summary.reindex(columns=["count", "mean", "std", "min", "max"])
    summary = summary.reset_index(names="column")

    return {
        "row_count": int(len(frame)),
        "subgroup_count": int(frame[subgroup_column].nunique(dropna=True)),
        "measurement_count": len(selected_measurements),
        "issues": [issue.as_dict() for issue in issues],
        "measurement_summary": summary.to_dict(orient="records"),
    }


def profile_csv(
    path: str | Path,
    subgroup_column: str,
    measurement_columns: Sequence[str] | None = None,
    **read_csv_kwargs: Any,
) -> dict[str, object]:
    """Read a CSV file and return the same structured profile as profile_frame."""

    frame = pd.read_csv(path, **read_csv_kwargs)
    return profile_frame(
        frame,
        subgroup_column=subgroup_column,
        measurement_columns=measurement_columns,
    )
