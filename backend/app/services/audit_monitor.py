from datetime import datetime, timezone


SENSITIVE_FIELDS = [
    "date_of_birth",
    "gender",
    "religion",
    "race",
    "ethnicity",
    "marital_status",
    "nationality"
]


def generate_audit_report(action, filename, details=None):
    audit_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "filename": filename,
        "details": details or {},
        "status": "recorded"
    }

    return audit_record


def check_sensitive_attributes(candidate_data):
    detected_fields = []

    if not isinstance(candidate_data, dict):
        return {
            "sensitive_fields_detected": [],
            "warning": "Candidate data must be a dictionary."
        }

    for field in SENSITIVE_FIELDS:
        if field in candidate_data:
            detected_fields.append(field)

    return {
        "sensitive_fields_detected": detected_fields,
        "fairness_warning": (
            "Sensitive personal attributes should not be used "
            "for candidate ranking or scoring."
            if detected_fields
            else "No listed sensitive fields were found in the supplied data."
        )
    }


def generate_privacy_report():
    return {
        "privacy_checks": [
            {
                "check": "File storage",
                "recommendation": "Restrict access to uploaded resumes."
            },
            {
                "check": "Personal information",
                "recommendation": "Avoid exposing candidate contact details unnecessarily."
            },
            {
                "check": "Data retention",
                "recommendation": "Delete resumes when they are no longer required."
            },
            {
                "check": "Candidate scoring",
                "recommendation": "Do not use sensitive personal attributes for scoring."
            }
        ],
        "message": "Basic privacy recommendations generated."
    }