
import json
import logging
import os
import re
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")

GEMINI_MODEL = "gemini-3.5-flash-lite"


# Used only when Gemini is unavailable.
SKILL_DICTIONARY = [
    "Python", "Java", "JavaScript", "C++", "C#", "C",
    "SQL", "PHP", "HTML", "CSS", "React", "Node.js",
    "Django", "FastAPI", "Flask", "REST API",
    "MySQL", "PostgreSQL", "MongoDB", "SQLite",
    "Machine Learning", "Deep Learning", "TensorFlow",
    "OpenCV", "NumPy", "Pandas", "Scikit-learn",
    "Linux", "Unix", "Windows", "Git", "GitHub",
    "Docker", "Jenkins", "Microsoft Office", "Excel",
    "PowerPoint", "HRIS", "Recruitment", "Payroll",
    "Employee Relations", "Performance Management",
    "MicroStation", "GeoPak", "ArcView",
    "Microsoft Access", "AutoCAD", "GPS",
    "Social Work", "Psychotherapy", "Crisis Intervention"
]


@lru_cache(maxsize=1)
def get_gemini_client():
    """Create the Gemini client once and reuse it."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=30000)
    )


def extract_skills_with_dictionary(text):
    """Fallback extractor using the existing skill dictionary."""

    text = re.sub(
        r"https?://\S+|www\.\S+|github\.com/\S+|linkedin\.com/\S+",
        " ",
        text,
        flags=re.IGNORECASE
    )

    extracted_skills = []

    for skill in sorted(SKILL_DICTIONARY, key=len, reverse=True):

        if skill == "C":
            pattern = re.compile(
                r"(?<![A-Za-z0-9+#/])C(?![A-Za-z0-9+#/])"
            )

        elif skill in {"C++", "C#"}:
            pattern = re.compile(
                r"(?<![A-Za-z0-9+#])"
                + re.escape(skill)
                + r"(?![A-Za-z0-9+#])",
                re.IGNORECASE
            )

        else:
            pattern = re.compile(
                r"(?<![A-Za-z0-9])"
                + re.escape(skill)
                + r"(?![A-Za-z0-9])",
                re.IGNORECASE
            )

        match = pattern.search(text)

        if match:
            start = text.rfind("\n", 0, match.start()) + 1
            end = text.find("\n", match.end())

            if end == -1:
                end = len(text)

            evidence = text[start:end].strip()

            extracted_skills.append({
                "skill": skill,
                "evidence": evidence,
                "confidence": "explicit_match"
            })

    extracted_skills.sort(
        key=lambda item: item["skill"].lower()
    )

    return extracted_skills


def extract_skills_with_gemini(text):
    """Extract explicitly supported skills using Gemini AI."""

    prompt = f"""
You are a professional resume and job-description skill extraction system.

Extract skills explicitly mentioned in the supplied text.

Rules:
1. Identify technical skills, programming languages, frameworks,
   libraries, databases, tools, platforms, and relevant professional skills.
2. Do not invent skills or infer skills only from a job title.
3. Do not treat a person's name, company name, job title, or degree
   as a skill.
4. Return the skill name as written in the supplied text.
5. For every skill, provide an evidence excerpt copied exactly
   from the supplied text.
6. Avoid duplicate skills.
7. If no skills are found, return an empty list.
8. Return valid JSON only.

Required JSON format:
[
  {{
    "skill": "Python",
    "evidence": "Developed applications using Python"
  }}
]

TEXT TO ANALYZE:
{text}
"""

    client = get_gemini_client()

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    result = json.loads(response.text)

    if isinstance(result, dict):
        result = result.get("skills", [])

    if not isinstance(result, list):
        raise ValueError("Unexpected Gemini response format.")

    extracted_skills = []
    seen_skills = set()

    for item in result:

        if not isinstance(item, dict):
            continue

        skill = item.get("skill")
        evidence = item.get("evidence")

        if not isinstance(skill, str) or not isinstance(evidence, str):
            continue

        skill = skill.strip()
        evidence = evidence.strip()

        if not skill or not evidence:
            continue

        # Evidence must actually appear in the supplied text.
        if evidence.lower() not in text.lower():
            continue

        key = skill.lower()

        if key in seen_skills:
            continue

        seen_skills.add(key)

        extracted_skills.append({
            "skill": skill,
            "evidence": evidence,
            "confidence": "ai_extracted"
        })

    extracted_skills.sort(
        key=lambda item: item["skill"].lower()
    )

    return extracted_skills


def extract_skills(text):
    """
    Main skill extraction function.

    Gemini is used first. The original dictionary extractor
    is retained as a fallback if the AI request fails.
    """

    if not text or not text.strip():
        return []

    try:
        return extract_skills_with_gemini(text)

    except Exception as error:
        logger.warning(
            "Gemini skill extraction failed. "
            "Using dictionary fallback. Reason: %s",
            error
        )

        return extract_skills_with_dictionary(text)
