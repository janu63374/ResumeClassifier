
import re
import spacy


nlp = spacy.load("en_core_web_sm")


# Common resume headings and terms that should not be candidate names
INVALID_NAMES = {
    "summary",
    "professional overview",
    "professional summary",
    "experience",
    "education",
    "skills",
    "highlights",
    "core qualifications",
    "accomplishments",
    "engineering manager",
    "engineering technician",
    "regional hr manager",
    "human resources",
    "contact",
    "profile",
    "career objective",
    "objective",
}


BLOCKED_NAME_WORDS = {
    "manager", "engineer", "technician", "supervisor",
    "clinical", "professional", "social", "software",
    "human", "resources", "acumen", "psychotherapist",
    "experience", "education", "skills", "highlights",
    "university", "college", "institute", "school",
    "corporation", "company", "technologies", "inc"
}


# Technical terms that should not be treated as locations
TECHNICAL_TERMS = {
    "python", "java", "javascript", "sql", "postgresql",
    "mysql", "mongodb", "react", "node.js", "flask",
    "fastapi", "django", "numpy", "pandas", "docker",
    "tensorflow", "opencv", "github", "git", "html",
    "css", "maven", "linux", "unix"
}


# Common action words and generic terms that should not be organizations
INVALID_ORG_WORDS = {
    "explored", "implemented", "developed", "contributed",
    "conducted", "wrote", "presented", "assess",
    "languages", "frameworks", "libraries", "projects",
    "technical", "skills", "experience", "education",
    "liberal", "arts"
}


def extract_email(text):
    match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    return match.group(0) if match else None


def extract_phone(text):
    patterns = [
        r"(?<!\d)\+\d{1,3}[-.\s]?\d{2,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}(?!\d)",
        r"(?<!\d)\d{3}[-.\s]\d{3}[-.\s]\d{4}(?!\d)",
        r"(?<!\d)\d{10}(?!\d)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            return match.group(0).strip()

    return None


def extract_name_candidates(text):
    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in text.splitlines()
        if line.strip()
    ]

    candidates = []

    for line in lines[:5]:
        normalized = line.lower()

        if normalized in INVALID_NAMES:
            continue

        if len(line.split()) not in (2, 3):
            continue

        if len(line) > 40:
            continue

        if not re.fullmatch(
            r"[A-Za-z]+(?:[ '-][A-Za-z]+){1,2}",
            line
        ):
            continue

        words = set(normalized.split())

        if words & BLOCKED_NAME_WORDS:
            continue

        candidates.append({
            "value": line,
            "confidence": "low",
            "evidence": line
        })

    return candidates if candidates else None


def is_valid_entity(entity_text):
    value = re.sub(r"\s+", " ", entity_text).strip()

    if not value:
        return False

    # Reject long or multiline entity fragments
    if len(value) > 60 or "\n" in entity_text:
        return False

    # Reject bullet points and incomplete sentences
    if any(symbol in value for symbol in ["•", "●", "▪", "►"]):
        return False

    # Reject entities that are only technical terms
    words = set(re.findall(r"[a-zA-Z0-9.]+", value.lower()))

    if words and words.issubset(TECHNICAL_TERMS):
        return False

    return True


def extract_candidate_information(text):
    doc = nlp(text)

    organizations = []
    locations = []
    dates = []

    for ent in doc.ents:
        value = ent.text.strip()

        if not is_valid_entity(value):
            continue

        normalized = value.lower()

        if ent.label_ == "ORG":

            words = set(re.findall(r"[a-zA-Z]+", normalized))

            if words & INVALID_ORG_WORDS:
                continue

            if len(value.split()) > 5:
                continue

            if value not in organizations:
                organizations.append(value)

        elif ent.label_ == "GPE":

            if normalized in TECHNICAL_TERMS:
                continue

            if len(value.split()) > 4:
                continue

            if value not in locations:
                locations.append(value)

        elif ent.label_ == "DATE":

            if value not in dates:
                dates.append(value)

    return {
        "candidate_name_candidates": extract_name_candidates(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "organizations": organizations,
        "locations": locations,
        "dates": dates,
        "source_text": text
    }
