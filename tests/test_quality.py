import pandas as pd
import pytest

from engineering_data_quality import profile_frame, validate_subgroups


def valid_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Subgroup": [1, 2, 3],
            "x1": [10.1, 10.0, 10.2],
            "x2": [9.9, 10.1, 10.0],
        }
    )


def test_valid_frame_has_no_issues() -> None:
    assert validate_subgroups(valid_frame(), "Subgroup") == []


def test_profile_reports_shape_and_measurement_summary() -> None:
    profile = profile_frame(
        valid_frame(),
        subgroup_column="Subgroup",
        measurement_columns=["x1", "x2"],
    )

    assert profile["row_count"] == 3
    assert profile["subgroup_count"] == 3
    assert profile["measurement_count"] == 2
    assert profile["issues"] == []
    assert len(profile["measurement_summary"]) == 2


def test_duplicate_subgroups_are_reported_without_dropping_rows() -> None:
    frame = valid_frame()
    frame.loc[2, "Subgroup"] = 2

    issues = validate_subgroups(frame, "Subgroup")

    assert any(issue.code == "duplicate-subgroup" for issue in issues)
    assert len(frame) == 3


def test_missing_and_non_numeric_measurements_are_reported() -> None:
    frame = valid_frame()
    frame.loc[1, "x1"] = None
    frame["x2"] = ["ok", "bad", "values"]

    issues = validate_subgroups(frame, "Subgroup")

    codes = {issue.code for issue in issues}
    assert "missing-measurement" in codes
    assert "non-numeric-measurement" in codes


def test_missing_subgroup_column_raises_when_profiling() -> None:
    with pytest.raises(ValueError, match="subgroup column"):
        profile_frame(pd.DataFrame({"x1": [1.0]}), "Subgroup")
