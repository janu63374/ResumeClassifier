
import re

from backend.app.services.skill_extractor import extract_skills


# Map common skill names and variations to one standard name.
SKILL_ALIASES = {
    "js": "javascript",
    "javascript": "javascript",

    "react.js": "react",
    "reactjs": "react",
    "react": "react",

    "nodejs": "node.js",
    "node.js": "node.js",

    "postgres": "postgresql",
    "postgresql": "postgresql",

    "rest api": "rest api",
    "rest apis": "rest api",

    "amazon web services": "aws",
    "aws": "aws",

    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "scikit-learn": "scikit-learn",

    "powerbi": "power bi",
    "power bi": "power bi",

    "mongodb": "mongodb",
    "mongo db": "mongodb",
}


def canonicalize_skill(skill):
    """Convert common skill variations to a standard name."""

    cleaned = re.sub(r"\s+", " ", skill.strip().lower())

    return SKILL_ALIASES.get(cleaned, cleaned)


def normalize_skills(skills):
    """Normalize skill names while preserving evidence."""

    normalized = {}

    for item in skills:

        if isinstance(item, dict):
            skill = item.get("skill", "")
            evidence = item.get("evidence", "")

        elif isinstance(item, str):
            skill = item
            evidence = ""

        else:
            continue

        if not isinstance(skill, str) or not skill.strip():
            continue

        key = canonicalize_skill(skill)

        if key not in normalized:
            normalized[key] = {
                "skill": key,
                "evidence": evidence
            }

    return normalized


def match_resume_to_job(resume_text, job_description):

    if not resume_text or not job_description:
        raise ValueError("Resume text and job description are required.")

    resume_skills = normalize_skills(extract_skills(resume_text))
    job_skills = normalize_skills(extract_skills(job_description))

    if not job_skills:
        return {
            "match_score": 0,
            "total_job_skills": 0,
            "matched_skill_count": 0,
            "matching_skills": [],
            "missing_skills": [],
            "message": "No recognized skills found in the job description."
        }

    matching_names = sorted(set(resume_skills) & set(job_skills))
    missing_names = sorted(set(job_skills) - set(resume_skills))

    matching_skills = [
        {
            "skill": resume_skills[name]["skill"],
            "resume_evidence": resume_skills[name]["evidence"]
        }
        for name in matching_names
    ]

    match_score = round(
        len(matching_names) / len(job_skills) * 100,
        2
    )

    return {
        "match_score": match_score,
        "total_job_skills": len(job_skills),
        "matched_skill_count": len(matching_names),
        "matching_skills": matching_skills,
        "missing_skills": [
            job_skills[name]["skill"] for name in missing_names
        ],
        "message": "Resume and job description comparison completed."
    }
