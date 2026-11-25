
import re
import spacy
import html

nlp = spacy.load("en_core_web_sm")


# Common resume headings and terms that should not be candidate names
INVALID_NAMES = {
    "name",
    "full name",
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
    text = html.unescape(text)

    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in text.splitlines()
        if line.strip()
    ]

    candidates = {}

    field_labels = {
    "name", "full name", "candidate name",
    "address", "permanent address", "current address",
    "phone", "permanent phone", "mobile", "telephone",
    "email", "e-mail", "contact", "date of birth",
    "dob", "nationality", "gender", "location",
    "linkedin", "website"
     }

    title_pattern = re.compile(
        r"^(?:(?:Mr|Mrs|Ms|Miss|Dr|Prof)\.?\s+)",
        re.IGNORECASE
    )

    name_token = (
        r"(?:[A-Za-z](?:\.[A-Za-z]){1,5}\.?|"
        r"[A-Za-z]\.?|"
        r"[A-Za-z]+(?:['-][A-Za-z]+)*)"
    )

    name_pattern = re.compile(
        rf"^{name_token}(?:\s*{name_token}){{0,3}}$",
        re.IGNORECASE
    )

    role_words = {
        "developer", "analyst", "designer",
        "administrator", "consultant", "architect",
        "specialist", "intern", "student",
        "engineer", "manager", "technician",
        "supervisor", "experienced"
    }

    for index, line in enumerate(lines[:40]):

        if len(line) > 100:
            continue

        # Remove contact information appearing after the name.
        candidate = re.split(
            r"\s*(?:\||•|·|▪|◦)\s*",
            line,
            maxsplit=1
        )[0]

        if candidate.lower().strip(" :") in field_labels:
            continue

        candidate = re.sub(
            r"\s+(?:e-?mail|phone|mobile|contact|address|linkedin|website)\b.*$",
            "",
            candidate,
            flags=re.IGNORECASE
        )

        # Remove labels such as Name: or Candidate Name:
        candidate = re.sub(
            r"^(?:candidate\s+name|name)\s*:\s*",
            "",
            candidate,
            flags=re.IGNORECASE
        ).strip(" -–—|,;")

        if not candidate:
            continue

        if candidate.lower().strip(" :") in field_labels:
            continue

        if candidate.lower().strip() in INVALID_NAMES:
            continue

        if any(char.isdigit() for char in candidate):
            continue

        body = title_pattern.sub("", candidate).strip()

        if not name_pattern.fullmatch(body):
            continue

        if len(body) > 45:
            continue

        name_parts = re.findall(r"[A-Za-z]+", body)

        if not name_parts or not any(len(part) >= 2 for part in name_parts):
            continue

        normalized_words = {
            word.lower() for word in name_parts
        }

        if normalized_words & BLOCKED_NAME_WORDS:
            continue

        if normalized_words & TECHNICAL_TERMS:
            continue

        if normalized_words & role_words:
            continue

        doc = nlp(candidate)

        person_detected = any(
            ent.label_ == "PERSON"
            and ent.text.strip().lower() == candidate.lower()
            for ent in doc.ents
        )

        score = 40 - index

        if person_detected:
            score += 5

        candidates[candidate.lower()] = {
            "value": candidate,
            "confidence": "high" if person_detected else "medium",
            "evidence": candidate,
            "_score": score
        }

    if not candidates:
        return None

    best_candidate = max(
        candidates.values(),
        key=lambda item: item["_score"]
    )

    best_candidate.pop("_score", None)

    return [best_candidate]

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
