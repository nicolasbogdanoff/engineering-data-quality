"""Profile and validate a tiny subgrouped engineering dataset."""

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

print("Validation issues:", issues)
print("Measurement summary:")
print(profile["measurement_summary"])
