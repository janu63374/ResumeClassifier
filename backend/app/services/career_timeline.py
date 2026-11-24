
import re
from datetime import datetime


# Recognize employment date ranges
DATE_RANGE_PATTERN = re.compile(
    r'\b('
    r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|'
    r'May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|'
    r'Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
    r'\.?\s+\d{4}'
    r'|'
    r'\d{4}'
    r')\s*[-–—to]+\s*('
    r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|'
    r'May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|'
    r'Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
    r'\.?\s+\d{4}'
    r'|'
    r'Present|Current|'
    r'\d{4}'
    r')\b',
    re.IGNORECASE
)


MONTHS = {
    "jan": 1, "feb": 2, "mar": 3,
    "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9,
    "oct": 10, "nov": 11, "dec": 12
}


SECTION_HEADERS = {
    "experience",
    "work experience",
    "professional experience",
    "employment history",
    "career history"
}


END_HEADERS = {
    "education",
    "projects",
    "technical skills",
    "skills",
    "certifications",
    "achievements",
    "publications",
    "interests"
}


def parse_date(value):

    value = value.strip().replace(".", "")

    if value.lower() in ["present", "current"]:
        return datetime.now().year * 12 + datetime.now().month

    if re.fullmatch(r"\d{4}", value):
        return int(value) * 12 + 1

    parts = value.split()

    month = MONTHS.get(parts[0][:3].lower())
    year = int(parts[1])

    if month:
        return year * 12 + month

    return None


def extract_career_timeline(resume_text):

    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is required.")

    lines = [
        line.strip()
        for line in resume_text.splitlines()
        if line.strip()
    ]

    # Locate the experience section
    start_index = None
    end_index = len(lines)

    for index, line in enumerate(lines):
        header = line.strip().lower().rstrip(":").strip()

        if header in SECTION_HEADERS:
            start_index = index + 1
            break

    if start_index is None:
        return {
            "total_positions": 0,
            "timeline": [],
            "message": "No recognizable experience section found."
        }

    for index in range(start_index, len(lines)):
        header = lines[index].lower().rstrip(":").strip()

        if header in END_HEADERS:
            end_index = index
            break

    experience_lines = lines[start_index:end_index]

    timeline = []

    for index, line in enumerate(experience_lines):

        match = DATE_RANGE_PATTERN.search(line)

        if not match:
            continue

        start_date = match.group(1).strip()
        end_date = match.group(2).strip()

        # Find a likely job title before the date
        job_title = None

        for previous in range(index - 1, max(-1, index - 5), -1):
            candidate = experience_lines[previous]

            if (
                not candidate.startswith(("•", "-", "*"))
                and not DATE_RANGE_PATTERN.search(candidate)
                and len(candidate) < 100
            ):
                job_title = candidate
                break

        # Find a likely organization after the date
        organization = None

        for following in range(index + 1, min(index + 4, len(experience_lines))):
            candidate = experience_lines[following]

            if (
                not candidate.startswith(("•", "-", "*"))
                and not DATE_RANGE_PATTERN.search(candidate)
                and len(candidate) < 100
            ):
                organization = candidate
                break

        start_value = parse_date(start_date)

        timeline.append({
            "job_title": job_title,
            "organization": organization,
            "start_date": start_date,
            "end_date": end_date,
            "date_range": f"{start_date} - {end_date}",
            "sort_date": start_value,
            "evidence": line
        })

    # Sort entries by starting date, newest first
    timeline.sort(
        key=lambda item: item["sort_date"] or 0,
        reverse=True
    )

    for item in timeline:
        item.pop("sort_date")

    return {
        "total_positions": len(timeline),
        "timeline": timeline,
        "message": "Career timeline analysis completed."
    }
