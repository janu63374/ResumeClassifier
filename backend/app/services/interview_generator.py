
import json
import os
import re

from dotenv import load_dotenv
from google import genai


load_dotenv()


def generate_interview_questions(resume_text, job_description):
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is required.")

    if not job_description or not job_description.strip():
        raise ValueError("Job description is required.")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY was not found. Check the project's .env file."
        )

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are an expert technical interviewer.

Generate 10 personalized interview questions using BOTH the candidate's
resume and the job description below.

Requirements:
- Questions must be specific to the candidate's actual resume and target role.
- Do not invent projects, qualifications, skills, or work experience.
- Include a balanced mix of technical, project-based, problem-solving,
  experience, and behavioral questions.
- Avoid generic questions that could apply to every candidate.
- Each question must have a short purpose explaining what it evaluates.
- Return valid JSON only. Do not include Markdown or code fences.


IMPORTANT QUESTION LENGTH RULES:
- Keep every interview question short and direct.
- Each question must contain no more than 20 words.
- Use simple, professional English.
- Ask only ONE thing per question.
- Avoid lengthy explanations and multiple-part questions.
- Keep each purpose to a maximum of 12 words.
- Do not sacrifice relevance to the resume or job description.
- Generate exactly 10 questions.


Required JSON structure:
{{
  "questions": [
    {{
      "category": "Technical",
      "question": "Question text",
      "purpose": "What this question evaluates"
    }}
  ]
}}

Candidate resume:
{resume_text[:15000]}

Job description:
{job_description[:10000]}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        response_text = response.text

        if not response_text:
            raise RuntimeError("Gemini returned an empty response.")

        # Remove code fences if the model includes them.
        response_text = response_text.strip()
        response_text = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            response_text,
            flags=re.IGNORECASE
        )

        generated_data = json.loads(response_text)
        questions = generated_data.get("questions", [])

        if not isinstance(questions, list) or not questions:
            raise ValueError("Gemini did not return a valid question list.")

        validated_questions = []

        for item in questions:
            if not isinstance(item, dict):
                continue

            category = str(item.get("category", "")).strip()
            question = str(item.get("question", "")).strip()
            purpose = str(item.get("purpose", "")).strip()

            if category and question and purpose:
                validated_questions.append({
                    "category": category,
                    "question": question,
                    "purpose": purpose
                })

        if not validated_questions:
            raise ValueError("Gemini returned no valid interview questions.")

        return {
            "total_questions": len(validated_questions),
            "questions": validated_questions,
            "generation_method": "Google Gemini AI",
            "message": "Personalized interview questions generated successfully."
        }

    except json.JSONDecodeError as error:
        raise RuntimeError(
            "Gemini returned an invalid response format. Please try again."
        ) from error

    except Exception as error:
        raise RuntimeError(
            f"AI interview question generation failed: {str(error)}"
        ) from error
