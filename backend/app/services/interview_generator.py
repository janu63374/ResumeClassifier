def generate_interview_questions(resume_text, job_description):
    if not resume_text or not job_description:
        raise ValueError("Resume text and job description are required.")

    questions = [
        {
            "category": "Technical",
            "question": "Which technical skills from your resume are most relevant to this job?",
            "purpose": "Evaluate relevant technical knowledge."
        },
        {
            "category": "Experience",
            "question": "Can you explain a project or work experience from your resume that relates to this job?",
            "purpose": "Understand practical experience."
        },
        {
            "category": "Problem Solving",
            "question": "Describe a technical or professional challenge you faced and how you solved it.",
            "purpose": "Evaluate problem-solving ability."
        },
        {
            "category": "Job Related",
            "question": "How would you apply your existing skills to the responsibilities described in this job?",
            "purpose": "Evaluate job readiness."
        },
        {
            "category": "Behavioral",
            "question": "How do you learn a new skill or technology when working on an unfamiliar task?",
            "purpose": "Understand learning ability."
        }
    ]

    return {
        "total_questions": len(questions),
        "questions": questions,
        "generation_method": "Rule-based question generation",
        "message": "Interview questions generated successfully."
    }