from pathlib import Path

from backend.app.services.document_parser import extract_resume_text
from backend.app.services.skill_extractor import extract_skills


UPLOAD_DIR = Path("data/uploads")

files = list(UPLOAD_DIR.glob("*.pdf")) + list(UPLOAD_DIR.glob("*.docx"))

if not files:
    print("No resumes found.")

else:
    for file in files:

        print("\n" + "=" * 50)
        print("RESUME:", file.name)

        try:
            resume = extract_resume_text(str(file))

            skills = extract_skills(resume["text"])

            print("\nEXTRACTED SKILLS:")

            for skill in skills:
                print("Skill:", skill["skill"])
                print("Evidence:", skill["evidence"])
                print("Confidence:", skill["confidence"])
                print("-" * 30)

            print("TOTAL SKILLS:", len(skills))
            print("STATUS: SUCCESS")

        except Exception as error:
            print("STATUS: FAILED")
            print("ERROR:", error)