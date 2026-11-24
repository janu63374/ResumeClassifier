
from backend.app.services.skill_extractor import extract_skills


# Job roles and their relevant skills
ROLE_SKILLS = {
    "Software Developer": [
        "Python", "Java", "JavaScript", "HTML",
        "CSS", "SQL", "React", "Node.js"
    ],

    "Data Analyst": [
        "Python", "SQL", "Excel", "Power BI",
        "Tableau", "Pandas", "NumPy"
    ],

    "Data Scientist": [
        "Python", "SQL", "Machine Learning",
        "Pandas", "NumPy", "TensorFlow"
    ],

    "Web Developer": [
        "HTML", "CSS", "JavaScript",
        "React", "Node.js", "PHP"
    ],

    "Database Administrator": [
        "SQL", "MySQL", "PostgreSQL",
        "Oracle", "Database"
    ],

    "HR Executive": [
        "Recruitment", "Human Resources",
        "Payroll", "Communication",
        "Employee Relations"
    ],

    "Finance Analyst": [
        "Accounting", "Financial Analysis",
        "Excel", "Financial Reporting",
        "Budgeting"
    ],

    "Digital Marketing Executive": [
        "SEO", "Digital Marketing",
        "Social Media Marketing",
        "Google Analytics", "Content Marketing"
    ],

    "Sales Executive": [
        "Sales", "Communication",
        "Negotiation", "CRM",
        "Customer Relationship Management"
    ],

    "Project Coordinator": [
        "Project Management", "Communication",
        "Planning", "Coordination",
        "Microsoft Office"
    ]
}


def recommend_job_roles(resume_text, top_n=5):

    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is required.")

    extracted_skills = extract_skills(resume_text)

    candidate_skills = {
        item["skill"].strip().lower()
        for item in extracted_skills
        if isinstance(item, dict) and item.get("skill")
    }

    if not candidate_skills:
        return {
            "extracted_skills": [],
            "total_recommendations": 0,
            "recommendations": [],
            "message": "No recognized skills found in the resume."
        }

    recommendations = []

    for role, required_skills in ROLE_SKILLS.items():

        matched_skills = [
            skill for skill in required_skills
            if skill.lower() in candidate_skills
        ]

        if not matched_skills:
            continue

        score = round(
            len(matched_skills) / len(required_skills) * 100,
            2
        )

        recommendations.append({
            "job_role": role,
            "match_score": score,
            "matched_skills": matched_skills,
            "total_matched_skills": len(matched_skills),
            "total_role_skills": len(required_skills)
        })

    recommendations.sort(
        key=lambda item: item["match_score"],
        reverse=True
    )

    recommendations = recommendations[:top_n]

    return {
        "extracted_skills": sorted(candidate_skills),
        "total_recommendations": len(recommendations),
        "recommendations": recommendations,
        "message": "Alternative job-role recommendations generated successfully."
    }
