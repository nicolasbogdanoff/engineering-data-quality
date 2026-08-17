from pathlib import Path

from engineering_data_quality import profile_csv


DATA_PATH = Path(__file__).with_name("sample_engineering_data.csv")
profile = profile_csv(DATA_PATH, subgroup_column="Subgroup")

print("Profile issues:", profile["issues"])
print("Measurement summary:")
for row in profile["measurement_summary"]:
    print(row)
