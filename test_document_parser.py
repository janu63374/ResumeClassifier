
from pathlib import Path
from backend.app.services.document_parser import extract_resume_text

UPLOAD_DIR = Path("data/uploads")

files = list(UPLOAD_DIR.glob("*.pdf")) + list(UPLOAD_DIR.glob("*.docx"))

if not files:
    print("No uploaded resumes found.")
else:
    for file in files:
        print("\n" + "=" * 50)
        print("FILE:", file.name)

        try:
            result = extract_resume_text(str(file))

            print("TYPE:", result["file_type"])
            print("CHARACTERS:", result["character_count"])
            print("\nEXTRACTED TEXT:")
            print(result["text"][:1000])

            print("\nSTATUS: SUCCESS")

        except Exception as error:
            print("STATUS: FAILED")
            print("ERROR:", error)
