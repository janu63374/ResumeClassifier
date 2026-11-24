
from pathlib import Path

from backend.app.services.document_parser import extract_resume_text
from backend.app.services.resume_analyzer import analyze_resume


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

            result = analyze_resume(resume["text"])

            print("\nCANDIDATE INFORMATION:")
            print(result["candidate"])

            print("\nEXTRACTED SKILLS:")

            for skill in result["skills"]:
                print(
                    skill["skill"],
                    "| Evidence:", skill["evidence"]
                )

            print("\nTOTAL SKILLS:", result["total_skills"])
            print("STATUS:", result["analysis_status"])

        except Exception as error:
            print("ERROR:", error)
