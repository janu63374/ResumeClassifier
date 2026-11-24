
from pathlib import Path

from backend.app.services.document_parser import extract_resume_text
from backend.app.services.candidate_extractor import extract_candidate_information


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
            print("FIRST 500 CHARACTERS:")
            print(resume["text"][:500])
            result = extract_candidate_information(resume["text"])
            print("EMAIL MATCHES:", result["email"])
            print("PHONE MATCHES:", result["phone"])
            print("EMAIL/PHONE SEARCH:")
            for line in resume["text"].splitlines():
                if "@" in line or any(char.isdigit() for char in line):
                    print(line)

            print("NAME CANDIDATES:", result["candidate_name_candidates"])
            print("EMAIL:", result["email"])
            print("PHONE:", result["phone"])
            print("ORGANIZATIONS:", result["organizations"][:10])
            print("LOCATIONS:", result["locations"][:10])
            print("DATES:", result["dates"][:10])
            print("STATUS: SUCCESS")

        except Exception as error:
            print("STATUS: FAILED")
            print("ERROR:", error)
