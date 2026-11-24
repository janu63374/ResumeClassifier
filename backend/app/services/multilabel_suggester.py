
import re

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
        "performed quality testing",
        "developed a full-stack web application",
        "developed a rest api",
        "developed a game in java",
        "software development",
        "software engineering",
        "developed software applications",
        "built web applications",
        "developed web applications",
        "programmed applications"
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
        "performed financial analysis",
        "monitored expenses",
        "audited employee business expenses",
        "financial audit department",
        "assisted financial audit",
        "financial forecasting",
        "forecasting shipments",
        "reviewed financial transactions",
        "analyzed financial data",
        "managed financial records",
        "prepared expense reports",
        "accounting department"
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


def suggest_additional_categories(text, primary_category=None):
    suggestions = []

    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in str(text).splitlines()
        if line.strip()
    ]

    for category, phrases in CATEGORY_RULES.items():

        if category == primary_category:
            continue

        evidence = []
        seen_lines = set()

        for line in lines:
            for phrase in phrases:
                pattern = (
                    r"(?<!\w)"
                    + re.escape(phrase)
                    + r"(?!\w)"
                )

                if re.search(pattern, line, re.IGNORECASE):
                    if line not in seen_lines:
                        evidence.append({
                            "matched_phrase": phrase,
                            "resume_evidence": line
                        })
                        seen_lines.add(line)

        if len(evidence)>=2:
            if len(evidence)>=4:
                confidence="High"
            else:
                confidence="Medium"
            suggestions.append({
                "suggested_category": category,
                "matched_evidence_count": len(evidence),
                "unique_matched_phrase_count": len(set(
                    item["matched_phrase"] for item in evidence
                )),
                "confidence":confidence,
                "evidence": evidence,
                "review_status": "Needs Human Review"
            })

    return suggestions
