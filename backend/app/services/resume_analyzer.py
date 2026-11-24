from backend.app.services.candidate_extractor import (
    extract_candidate_information
)

from backend.app.services.skill_extractor import extract_skills


def analyze_resume(text):

    candidate_info = extract_candidate_information(text)

    skills = extract_skills(text)

    return {
        "candidate": {
            "name_candidates": candidate_info["candidate_name_candidates"],
            "email": candidate_info["email"],
            "phone": candidate_info["phone"],
            "organizations": candidate_info["organizations"],
            "locations": candidate_info["locations"],
            "dates": candidate_info["dates"]
        },
        "skills": skills,
        "total_skills": len(skills),
        "analysis_status": "completed"
    }