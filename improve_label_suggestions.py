
import pandas as pd
import re
from pathlib import Path

# Load original resume dataset
df = pd.read_csv("resumes.csv")

# Responsibility-related phrases for each category
CATEGORY_RULES = {
    "Engineering": [
        "designed and developed",
        "maintained equipment",
        "tested equipment",
        "troubleshot systems",
        "performed engineering",
        "installed and repaired",
        "developed technical solutions",
        "inspected electrical systems",
        "operated manufacturing equipment",
        "performed quality testing"
    ],
    "Finance": [
        "prepared financial statements",
        "managed accounts payable",
        "managed accounts receivable",
        "reconciled bank statements",
        "maintained general ledger",
        "prepared financial reports",
        "processed invoices",
        "managed payroll",
        "prepared budgets",
        "performed financial analysis"
    ],
    "HR": [
        "managed employee relations",
        "conducted recruitment",
        "managed recruitment",
        "handled employee benefits",
        "managed personnel records",
        "conducted performance evaluations",
        "coordinated employee training",
        "managed staffing",
        "handled employee onboarding",
        "developed human resource policies"
    ],
    "Sales": [
        "managed sales accounts",
        "generated sales leads",
        "achieved sales targets",
        "developed sales strategies",
        "managed customer relationships",
        "negotiated sales contracts",
        "acquired new customers",
        "managed sales operations",
        "increased sales revenue",
        "developed new business"
    ]
}


def find_evidence(text, phrases):
    matches = []
    lines = str(text).splitlines()

    for line in lines:
        clean_line = re.sub(r"\s+", " ", line).strip()

        if not clean_line:
            continue

        for phrase in phrases:
            pattern = (
                r"(?<!\w)"
                + re.escape(phrase)
                + r"(?!\w)"
            )

            if re.search(pattern, clean_line, re.IGNORECASE):
                matches.append({
                    "phrase": phrase,
                    "evidence": clean_line
                })

    return matches


results = []

for _, row in df.iterrows():
    primary = str(row["Category"]).strip()
    text = str(row["Text"])

    for category, phrases in CATEGORY_RULES.items():
        if category == primary:
            continue

        evidence_matches = find_evidence(text, phrases)

        if evidence_matches:
            results.append({
                "Resume": row["Resume"],
                "Primary_Category": primary,
                "Suggested_Category": category,
                "Matched_Phrase_Count": len(evidence_matches),
                "Evidence": " || ".join(
                    item["evidence"]
                    for item in evidence_matches
                ),
                "Review_Status": "Needs Human Review"
            })


report = pd.DataFrame(results)

output_path = Path(
    "data/processed/responsibility_suggestions.csv"
)

output_path.parent.mkdir(parents=True, exist_ok=True)

report.to_csv(output_path, index=False)

print("RESPONSIBILITY-BASED SUGGESTIONS COMPLETED")
print("------------------------------------------")
print("Total resumes checked:", len(df))
print("Suggestions generated:", len(report))

if not report.empty:
    print("\nSuggestions by category:")
    print(report["Suggested_Category"].value_counts())

    print("\nFirst 10 suggestions:")
    print(report.head(10).to_string(index=False))
else:
    print("\nNo matching responsibility phrases found.")

print("\nReport saved to:", output_path)
