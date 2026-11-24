
import pandas as pd
from pathlib import Path

suggestions = pd.read_csv(
    "data/processed/improved_label_suggestions.csv"
)

resumes = pd.read_csv("resumes.csv")

merged = suggestions.merge(
    resumes[["Resume", "Text"]],
    on="Resume"
)

report = []

for _, row in merged.iterrows():

    report.append("=" * 65)
    report.append(f"Resume: {row['Resume']}")
    report.append(f"Primary: {row['Primary_Category']}")
    report.append(f"Suggested: {row['Suggested_Category']}")
    report.append(f"Keywords: {row['Evidence']}")
    report.append("-" * 65)

    keywords = [
        word.strip().lower()
        for word in str(row["Evidence"]).split(",")
    ]

    for line in str(row["Text"]).splitlines():
        if any(keyword in line.lower() for keyword in keywords):
            report.append(line.strip())

    report.append("")

output = Path("data/processed/suggestion_evidence.txt")
output.write_text("\n".join(report), encoding="utf-8")

print("Evidence report created successfully!")
print("Suggestions checked:", len(merged))
print("Report:", output)
