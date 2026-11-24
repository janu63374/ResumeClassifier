
def score_candidate(match_result):

    total_job_skills = match_result.get("total_job_skills", 0)
    matched_skill_count = match_result.get("matched_skill_count", 0)

    matching_skills = match_result.get("matching_skills", [])
    missing_skills = match_result.get("missing_skills", [])

    if total_job_skills == 0:
        return {
            "candidate_score": 0,
            "score_status": "Not Scored",
            "matched_skill_count": 0,
            "total_job_skills": 0,
            "matching_skills": [],
            "missing_skills": [],
            "scoring_method": "Required skill coverage",
            "explanation": "No recognized job skills were found."
        }

    # Calculate score based on required skill coverage
    candidate_score = round(
        (matched_skill_count / total_job_skills) * 100, 2
    )

    # Keep the evidence associated with each matched skill
    evidence = []

    for item in matching_skills:
        evidence.append({
            "skill": item.get("skill"),
            "resume_evidence": item.get("resume_evidence", "")
        })

    return {
        "candidate_score": candidate_score,
        "score_status": "Scored",
        "matched_skill_count": matched_skill_count,
        "total_job_skills": total_job_skills,
        "matching_skills": evidence,
        "missing_skills": missing_skills,
        "scoring_method": "Required skill coverage",
        "explanation": (
            f"{matched_skill_count} out of {total_job_skills} "
            "recognized job skills were found in the resume."
        )
    }
