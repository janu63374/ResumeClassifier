def calculate_custom_score(match_result, criteria):
    total_job_skills = match_result.get("total_job_skills", 0)
    matched_skill_count = match_result.get("matched_skill_count", 0)

    skill_weight = criteria.get("skill_weight", 100)

    if total_job_skills == 0:
        return {
            "custom_score": 0,
            "score_status": "Not Scored",
            "explanation": "No recognized job skills were found."
        }

    skill_score = (matched_skill_count / total_job_skills) * 100

    custom_score = round(
        skill_score * skill_weight / 100, 2
    )

    return {
        "custom_score": custom_score,
        "skill_score": round(skill_score, 2),
        "skill_weight": skill_weight,
        "matched_skill_count": matched_skill_count,
        "total_job_skills": total_job_skills,
        "score_status": "Scored",
        "scoring_method": "Recruiter-configurable skill weight",
        "explanation": (
            f"Skill coverage is {round(skill_score, 2)}%. "
            f"Recruiter assigned a weight of {skill_weight}%."
        )
    }