import json
from fastapi import APIRouter, UploadFile, File, Body
from typing import Annotated
from pathlib import Path
from uuid import uuid4

from backend.app.services.document_parser import extract_resume_text

from fastapi import HTTPException

from backend.app.services.resume_analyzer import analyze_resume
from backend.app.services.multilabel_suggester import suggest_additional_categories
from backend.app.services.job_matcher import match_resume_to_job
from backend.app.services.skill_graph import generate_skill_graph

from backend.app.services.candidate_scorer import score_candidate

from backend.app.services.career_timeline import extract_career_timeline

from backend.app.services.role_recommender import recommend_job_roles

from backend.app.services.interview_generator import generate_interview_questions

from backend.app.services.custom_scorer import calculate_custom_score

from backend.app.services.confidence_reporter import generate_confidence_report

from backend.app.services.duplicate_detector import detect_duplicate_resumes

from datetime import datetime

from backend.app.services.audit_monitor import (
    generate_audit_report,
    check_sensitive_attributes,
    generate_privacy_report
)

router = APIRouter(
    prefix="/api/resumes",
    tags=["Resume Upload"]
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
METADATA_FILE = UPLOAD_DIR / "resume_metadata.json"

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/upload")
async def upload_resumes(
    files: Annotated[
        list[UploadFile],
        File(description="Select multiple PDF or DOCX resumes")
    ]
):

    results = []

    for file in files:

        original_name = Path(file.filename or "").name
        extension = Path(original_name).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            results.append({
                "filename": original_name,
                "status": "rejected",
                "reason": "Only PDF and DOCX files are allowed."
            })
            await file.close()
            continue

        content = await file.read(MAX_FILE_SIZE + 1)

        if not content:
            results.append({
                "filename": original_name,
                "status": "rejected",
                "reason": "Empty file."
            })
            await file.close()
            continue

        if len(content) > MAX_FILE_SIZE:
            results.append({
                "filename": original_name,
                "status": "rejected",
                "reason": "File size exceeds 10 MB."
            })
            await file.close()
            continue

        stored_name = f"{uuid4().hex}{extension}"

        # Save original filename in metadata

        metadata = {}

        if METADATA_FILE.exists():
            try:
                metadata = json.loads(
                    METADATA_FILE.read_text(encoding="utf-8")
                )
            except (json.JSONDecodeError, OSError):
                metadata = {}

        metadata[stored_name] = original_name

        METADATA_FILE.write_text(
            json.dumps(metadata, indent=4),
            encoding="utf-8"
        )

        file_path = UPLOAD_DIR / stored_name

        try:
            file_path.write_bytes(content)

            # Automatically extract resume text
            extracted_data = extract_resume_text(str(file_path))

            results.append({
                "filename": original_name,
                "stored_filename": stored_name,
                "file_size": len(content),
                "character_count": extracted_data["character_count"],
                "extracted_text": extracted_data["text"],
                "upload_status": "uploaded",
                "extraction_status": "success"
            })

        except Exception as error:

            results.append({
                "filename": original_name,
                "stored_filename": stored_name,
                "upload_status": "uploaded",
                "extraction_status": "failed",
                "reason": str(error)
            })

        finally:
            await file.close()

    return {
        "message": "Resume upload and extraction processing completed.",
        "total_files": len(files),
        "results": results
    }

@router.post("/{stored_filename}/analyze")
async def analyze_uploaded_resume(stored_filename: str):

    # Prevent directory traversal
    if Path(stored_filename).name != stored_filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename."
        )

    file_path = UPLOAD_DIR / stored_filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Resume file not found."
        )

    try:
        # Extract text from uploaded resume
        resume_data = extract_resume_text(str(file_path))

        # Analyze candidate information and skills
        analysis = analyze_resume(resume_data["text"])

        return {
            "message": "Resume analysis completed successfully.",
            "filename": stored_filename,
            "character_count": resume_data["character_count"],
            "analysis": analysis
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Resume analysis failed: {str(error)}"
        )


@router.post("/{stored_filename}/suggest-categories")
async def suggest_resume_categories(stored_filename: str):

    if Path(stored_filename).name != stored_filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename."
        )

    file_path = UPLOAD_DIR / stored_filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Resume file not found."
        )

    try:
        resume_data = extract_resume_text(str(file_path))

        suggestions = suggest_additional_categories(
            resume_data["text"]
        )

        return {
            "message": "Additional category suggestions generated.",
            "filename": stored_filename,
            "suggestions": suggestions,
            "note": "Suggestions require human review and are not final hiring decisions."
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Category suggestion failed: {str(error)}"
        )


@router.post("/{stored_filename}/match-job")
async def match_resume_with_job(
    stored_filename: str,
    job_description: str = Body(..., embed=True)
):
    if Path(stored_filename).name != stored_filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    file_path = UPLOAD_DIR / stored_filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Resume file not found.")

    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    try:
        resume_data = extract_resume_text(str(file_path))

        result = match_resume_to_job(
            resume_data["text"],
            job_description
        )

        return {
            "message": "Job matching completed successfully.",
            "filename": stored_filename,
            "result": result,
            "note": "Match score represents skill overlap, not an employment decision."
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Job matching failed: {str(error)}"
        )


@router.post("/match-multiple")
async def match_multiple_resumes(
    stored_filenames: list[str] = Body(...),
    job_description: str = Body(...)
):
    if not stored_filenames:
        raise HTTPException(
            status_code=400,
            detail="Please provide at least one resume filename."
        )

    if len(stored_filenames) > 20:
        raise HTTPException(
            status_code=400,
            detail="A maximum of 20 resumes can be compared at once."
        )

    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty."
        )

    results = []

    for filename in dict.fromkeys(stored_filenames):

        if Path(filename).name != filename:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid filename: {filename}"
            )

        file_path = UPLOAD_DIR / filename

        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Resume not found: {filename}"
            )

        try:
            resume_data = extract_resume_text(str(file_path))

            match_result = match_resume_to_job(
                resume_data["text"],
                job_description
            )

            results.append({
                "filename": filename,
                "result": match_result
            })

        except Exception as error:
            raise HTTPException(
                status_code=500,
                detail=f"Matching failed for {filename}: {str(error)}"
            )

    results.sort(
        key=lambda item: item["result"]["match_score"],
        reverse=True
    )

    return {
        "message": "Multiple resume matching completed successfully.",
        "total_resumes_compared": len(results),
        "results": results,
        "note": "Ranking is based on recognized skill overlap and requires recruiter review."
    }

@router.post("/{stored_filename}/skill-graph")
async def get_skill_graph(stored_filename: str):

    if Path(stored_filename).name != stored_filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    file_path = UPLOAD_DIR / stored_filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Resume not found.")

    try:
        resume_data = extract_resume_text(str(file_path))

        result = generate_skill_graph(resume_data["text"])

        return {
            "filename": stored_filename,
            "skill_graph": result
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Skill graph generation failed: {str(error)}"
        )

@router.post("/{stored_filename}/score-candidate")
async def score_resume_candidate(
    stored_filename: str,
    job_description: str = Body(..., embed=True)
):
    if Path(stored_filename).name != stored_filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    file_path = UPLOAD_DIR / stored_filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Resume not found.")

    try:
        resume_data = extract_resume_text(str(file_path))

        match_result = match_resume_to_job(
            resume_data["text"],
            job_description
        )

        scoring_result = score_candidate(match_result)

        return {
            "filename": stored_filename,
            "candidate_scoring": scoring_result,
            "note": "This score measures recognized skill coverage only. It is not a final hiring decision."
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Candidate scoring failed: {str(error)}"
        )

@router.post("/{stored_filename}/career-timeline")
async def get_career_timeline(stored_filename: str):

    if Path(stored_filename).name != stored_filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    file_path = UPLOAD_DIR / stored_filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Resume not found.")

    try:
        resume_data = extract_resume_text(str(file_path))

        result = extract_career_timeline(resume_data["text"])

        return {
            "filename": stored_filename,
            "career_timeline": result
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Career timeline analysis failed: {str(error)}"
        )

@router.post("/{stored_filename}/recommend-roles")
async def get_recommended_roles(stored_filename: str):

    if Path(stored_filename).name != stored_filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    file_path = UPLOAD_DIR / stored_filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Resume not found.")

    try:
        resume_data = extract_resume_text(str(file_path))

        result = recommend_job_roles(resume_data["text"])

        return {
            "filename": stored_filename,
            "role_recommendations": result
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Job-role recommendation failed: {str(error)}"
        )


@router.post("/compare-candidates")
async def compare_candidates(
    stored_filenames: list[str] = Body(...),
    job_description: str = Body(...)
):
    if not stored_filenames:
        raise HTTPException(
            status_code=400,
            detail="Please provide at least one resume filename."
        )

    if len(stored_filenames) > 20:
        raise HTTPException(
            status_code=400,
            detail="A maximum of 20 candidates can be compared."
        )

    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty."
        )

    comparison_results = []

    for filename in dict.fromkeys(stored_filenames):

        if Path(filename).name != filename:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid filename: {filename}"
            )

        file_path = UPLOAD_DIR / filename

        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Resume not found: {filename}"
            )

        try:
            resume_data = extract_resume_text(str(file_path))

            match_result = match_resume_to_job(
                resume_data["text"],
                job_description
            )

            scoring_result = score_candidate(match_result)

            comparison_results.append({
                "candidate": filename,
                "candidate_score": scoring_result["candidate_score"],
                "matched_skill_count": scoring_result["matched_skill_count"],
                "total_job_skills": scoring_result["total_job_skills"],
                "matching_skills": scoring_result["matching_skills"],
                "missing_skills": scoring_result["missing_skills"],
                "scoring_explanation": scoring_result["explanation"]
            })

        except Exception as error:
            raise HTTPException(
                status_code=500,
                detail=f"Comparison failed for {filename}: {str(error)}"
            )

    comparison_results.sort(
        key=lambda item: item["candidate_score"],
        reverse=True
    )

    return {
        "message": "Candidate comparison completed successfully.",
        "total_candidates_compared": len(comparison_results),
        "comparison_results": comparison_results,
        "ranking_method": "Required skill coverage",
        "note": "Candidate rankings support recruiter review and are not final hiring decisions."
    }


@router.post("/{stored_filename}/generate-interview-questions")
async def generate_questions(
    stored_filename: str,
    job_description: str = Body(..., embed=True)
):
    if Path(stored_filename).name != stored_filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename."
        )

    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty."
        )

    file_path = UPLOAD_DIR / stored_filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Resume not found."
        )

    try:
        resume_data = extract_resume_text(str(file_path))

        result = generate_interview_questions(
            resume_data["text"],
            job_description
        )

        return {
            "filename": stored_filename,
            **result
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Interview question generation failed: {str(error)}"
        )

@router.post("/{stored_filename}/custom-score")
async def custom_candidate_score(
    stored_filename: str,
    job_description: str = Body(...),
    skill_weight: float = Body(100)
):
    if Path(stored_filename).name != stored_filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename."
        )

    if not 0 <= skill_weight <= 100:
        raise HTTPException(
            status_code=400,
            detail="Skill weight must be between 0 and 100."
        )

    file_path = UPLOAD_DIR / stored_filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Resume not found."
        )

    try:
        resume_data = extract_resume_text(str(file_path))

        match_result = match_resume_to_job(
            resume_data["text"],
            job_description
        )

        result = calculate_custom_score(
            match_result,
            {"skill_weight": skill_weight}
        )

        return {
            "filename": stored_filename,
            **result
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Custom scoring failed: {str(error)}"
        )

@router.post("/{stored_filename}/confidence-report")
async def confidence_report(
    stored_filename: str,
    job_description: str = Body(..., embed=True)
):
    if Path(stored_filename).name != stored_filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename."
        )

    file_path = UPLOAD_DIR / stored_filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Resume not found."
        )

    try:
        resume_data = extract_resume_text(str(file_path))

        match_result = match_resume_to_job(
            resume_data["text"],
            job_description
        )

        result = generate_confidence_report(match_result)

        return {
            "filename": stored_filename,
            **result
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Confidence report generation failed: {str(error)}"
        )

@router.post("/{stored_filename}/check-duplicates")
async def check_duplicate_resumes(stored_filename: str):
    if Path(stored_filename).name != stored_filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename."
        )

    file_path = UPLOAD_DIR / stored_filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Resume not found."
        )

    try:
        result = detect_duplicate_resumes(
            UPLOAD_DIR,
            stored_filename
        )

        return result

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Duplicate detection failed: {str(error)}"
        )

@router.post("/{stored_filename}/audit-report")
async def create_audit_report(stored_filename: str):
    if Path(stored_filename).name != stored_filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    file_path = UPLOAD_DIR / stored_filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Resume not found.")

    try:
        result = generate_audit_report(
            action="resume_review",
            filename=stored_filename,
            details={"event": "Resume audit requested"}
        )
        return result

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Audit report failed: {str(error)}"
        )


@router.post("/fairness-check")
async def check_candidate_fairness(
    candidate_data: dict = Body(..., embed=True)
):
    try:
        return check_sensitive_attributes(candidate_data)

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Fairness check failed: {str(error)}"
        )


@router.get("/privacy-report")
async def get_privacy_report():
    try:
        return generate_privacy_report()

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Privacy report failed: {str(error)}"
        )


# ========================================
# LIST ALL UPLOADED RESUMES
# ========================================

@router.get("")
async def list_uploaded_resumes():
    try:
        resumes = []
        metadata = {}

        # Read original filenames
        if METADATA_FILE.exists():
            try:
                metadata = json.loads(
                    METADATA_FILE.read_text(encoding="utf-8")
                )
            except (json.JSONDecodeError, OSError):
                metadata = {}

        for file_path in UPLOAD_DIR.iterdir():

            if not file_path.is_file():
                continue

            if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
                continue

            file_info = file_path.stat()

            resumes.append({
                "stored_filename": file_path.name,
                "original_filename": metadata.get(
                    file_path.name,
                    file_path.name
                ),
                "file_size": file_info.st_size,
                "file_type": file_path.suffix.lower(),
                "uploaded_at": datetime.fromtimestamp(
                    file_info.st_mtime
                ).isoformat()
            })

        resumes.sort(
            key=lambda item: item["uploaded_at"],
            reverse=True
        )

        return {
            "message": "Uploaded resumes retrieved successfully.",
            "total_resumes": len(resumes),
            "resumes": resumes
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve uploaded resumes: {str(error)}"
        )
