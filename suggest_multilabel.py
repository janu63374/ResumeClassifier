
import pandas as pd
import re
from pathlib import Path

# Read the existing dataset
df = pd.read_csv("resumes.csv")

# Keywords for the four existing categories
CATEGORY_KEYWORDS = {
    "Engineering": [
        "mechanical engineering", "electrical engineering",
        "engineering design", "automation", "hydraulic",
        "electrical systems", "mechanical systems",
        "cad", "plc", "circuit design", "labview",
        "engineering technician", "test equipment"
    ],
    "Finance": [
        "financial analysis", "financial reporting",
        "financial statements", "accounts payable",
        "accounts receivable", "budget planning",
        "bookkeeping", "tax preparation", "general ledger",
        "bank reconciliation", "financial forecasting"
    ],
    "HR": [
        "human resources", "employee relations",
        "talent acquisition", "recruitment",
        "employee benefits", "employee onboarding",
        "performance management", "personnel management",
        "hr administration", "new hire orientation"
    ],
    "Sales": [
        "sales management", "sales representative",
        "sales targets", "sales quota", "lead generation",
        "business development", "customer acquisition",
        "sales negotiation", "account management",
        "sales forecasting"
    ]
}

def suggest_categories(text, primary_category):
    text = str(text).lower()
    suggestions = []
    evidence = []

    for category, keywords in CATEGORY_KEYWORDS.items():

        # Do not suggest the existing primary category
        if category == primary_category:
            continue

        matched = []

        for keyword in keywords:
            pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"

            if re.search(pattern, text):
                matched.append(keyword)

        # Suggest only when at least two keywords match
        if len(matched) >= 2:
            suggestions.append(category)
            evidence.append(
                category + ": " + ", ".join(matched)
            )

    return suggestions, evidence


results = []

for _, row in df.iterrows():
    primary = str(row["Category"]).strip()
    suggestions, evidence = suggest_categories(
        row["Text"],
        primary
    )

    results.append({
        "Resume": row["Resume"],
        "Primary_Category": primary,
        "Suggested_Additional_Categories": ", ".join(suggestions),
        "Evidence": " | ".join(evidence),
        "Review_Status": "Needs Review"
    })

output = pd.DataFrame(results)

output_path = Path("data/processed/automatic_label_suggestions.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

output.to_csv(output_path, index=False)

print("Automatic suggestions generated successfully!")
print("Total resumes:", len(output))
print("Resumes with suggestions:",
      (output["Suggested_Additional_Categories"] != "").sum())
print("Output file:", output_path)
print("\nFirst 10 suggestions:")
print(output.head(10).to_string(index=False))
