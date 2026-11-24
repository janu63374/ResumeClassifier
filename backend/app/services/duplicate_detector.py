import hashlib
from pathlib import Path


def calculate_file_hash(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def detect_duplicate_resumes(upload_dir, current_filename):
    upload_dir = Path(upload_dir)
    current_path = upload_dir / current_filename

    if not current_path.exists():
        raise FileNotFoundError("Resume file not found.")

    current_hash = calculate_file_hash(current_path)
    duplicates = []

    for file_path in upload_dir.iterdir():
        if not file_path.is_file():
            continue

        if file_path.name == current_filename:
            continue

        if file_path.suffix.lower() not in [".pdf", ".docx"]:
            continue

        try:
            existing_hash = calculate_file_hash(file_path)

            if existing_hash == current_hash:
                duplicates.append(file_path.name)

        except OSError:
            continue

    return {
        "filename": current_filename,
        "is_duplicate": len(duplicates) > 0,
        "duplicate_count": len(duplicates),
        "duplicate_files": duplicates,
        "detection_method": "SHA-256 file hash",
        "message": (
            "Duplicate resume detected."
            if duplicates
            else "No exact duplicate resume found."
        )
    }