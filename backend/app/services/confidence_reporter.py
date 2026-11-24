def generate_confidence_report(match_result):
    total_skills = match_result.get("total_job_skills", 0)
    matched_skills = match_result.get("matched_skill_count", 0)
    matching_skills = match_result.get("matching_skills", [])

    if total_skills == 0:
        return {
            "confidence_level": "Low",
            "confidence_score": 0,
            "uncertainty": "No recognized job skills were found.",
            "limitations": [
                "The job description may contain skills not supported by the current skill dictionary."
            ]
        }

    coverage = matched_skills / total_skills
    confidence_score = round(coverage * 100, 2)

    if coverage >= 0.75:
        confidence_level = "High"
    elif coverage >= 0.40:
        confidence_level = "Medium"
    else:
        confidence_level = "Low"

    uncertainties = []

    if matched_skills < total_skills:
        uncertainties.append(
            "Some required job skills were not found in the resume."
        )

    if not matching_skills:
        uncertainties.append(
            "No matching skill evidence was identified."
        )

    if not uncertainties:
        uncertainties.append(
            "All recognized job skills were found, but skill proficiency and practical ability are not verified."
        )

    return {
        "confidence_level": confidence_level,
        "confidence_score": confidence_score,
        "matched_skill_count": matched_skills,
        "total_job_skills": total_skills,
        "uncertainty": uncertainties,
        "limitations": [
            "Confidence is based on recognized skill coverage, not a calibrated probability.",
            "The system cannot verify actual skill proficiency or practical experience.",
            "Skills missing from the current skill dictionary may not be recognized."
        ]
    }