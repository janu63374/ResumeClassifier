# NOVA – AI Talent Intelligence Platform

**An AI-powered platform for resume analysis, skill intelligence, job matching, and candidate evaluation.**

NOVA is a web-based AI Talent Intelligence Platform designed to help recruiters analyze resumes, identify candidate skills, evaluate job compatibility, and make more informed recruitment decisions.

The platform combines Python, Machine Learning, NLP, Gemini AI, and a FastAPI backend with a web-based frontend.

## Key Features

1. **Resume Upload and Analysis** – Upload and analyze PDF resumes.
2. **Multi-label Resume Classification** – Identify multiple relevant professional categories.
3. **AI-powered Skill Extraction** – Extract skills from resume content using Gemini AI, with dictionary-based fallback.
4. **Candidate Information Extraction** – Identify available candidate details from resumes.
5. **Job Description Matching** – Compare candidate skills with job requirements.
6. **Skill Relationship Graph** – Visualize relationships between extracted skills.
7. **Evidence-based Candidate Scoring** – Calculate candidate scores based on matching skills and evidence.
8. **Career Timeline Analysis** – Analyze career experience and employment history.
9. **Alternative Job-role Recommendations** – Suggest other relevant job roles.
10. **Candidate Comparison** – Compare multiple candidates against job requirements.
11. **Interview Question Generation** – Generate role-related interview questions.
12. **Customizable Scoring** – Adjust skill weights during candidate evaluation.
13. **Confidence Reporting** – Report skill coverage and analysis confidence indicators.
14. **Duplicate Resume Detection** – Identify exact duplicate resumes using file hashing.
15. **Fairness, Privacy and Audit Monitoring** – Provide basic monitoring and audit-related checks.

## Technologies Used

**Backend**
- Python
- FastAPI
- Uvicorn
- Pydantic

**Artificial Intelligence and Machine Learning**
- Google Gemini API
- Scikit-learn
- Sentence Transformers
- NLTK
- NetworkX

**Data Processing**
- Pandas
- NumPy
- PyMuPDF
- Joblib
- Python-docx

**Frontend**
- HTML5
- CSS3
- JavaScript
- Bootstrap

**Database**
- MySQL

## Project Structure

```text
ResumeClassifier/
│
├── backend/
│   └── app/
│       ├── main.py
│       ├── api/
│       │   └── resume_routes.py
│       └── services/
│           ├── audit_monitor.py
│           ├── candidate_extractor.py
│           ├── candidate_scorer.py
│           ├── career_timeline.py
│           ├── confidence_reporter.py
│           ├── custom_scorer.py
│           ├── document_parser.py
│           ├── duplicate_detector.py
│           ├── interview_generator.py
│           ├── job_matcher.py
│           ├── multilabel_suggester.py
│           ├── resume_analyzer.py
│           ├── role_recommender.py
│           ├── skill_extractor.py
│           └── skill_graph.py
│
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
│
├── models/
├── data/
├── requirements.txt
├── .gitignore
├── .env.example
├── app.py
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd ResumeClassifier
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Use your own Gemini API key. Never upload your actual `.env` file to GitHub.

Configure MySQL credentials if required by your local database setup.

## Running NOVA

### 1. Start the Backend

From the project root:

```bash
uvicorn backend.app.main:app --reload
```

Backend:

`http://127.0.0.1:8000`

### 2. Open API Documentation

Visit:

`http://127.0.0.1:8000/docs`

### 3. Run the Frontend

Open the `frontend` folder using Visual Studio Code and launch `index.html` with Live Server.

The default development frontend address is:

`http://127.0.0.1:5500`

## API Endpoints

Interactive API documentation is available at:

`http://127.0.0.1:8000/docs`

The backend also provides:

- `/` – Application welcome endpoint.
- `/health` – Backend health check.

Resume-related API routes are registered through `backend/app/api/resume_routes.py`.

## Project Objective

The objective of NOVA is to simplify resume screening and candidate evaluation by combining artificial intelligence, natural language processing, and skill-based analysis.

It aims to support recruiters in identifying relevant candidates, understanding skill compatibility, and comparing applicants more efficiently.

## Important Notes

- Gemini-powered extraction requires a valid API key.
- MySQL configuration may be required for database-backed features.
- Candidate scores represent skill matching and coverage, not verified professional proficiency.
- Duplicate detection identifies exact file duplicates, not necessarily similar resumes.
- Fairness and audit features provide basic monitoring and should not be treated as legal or regulatory certification.
- NOVA is an academic/project prototype and requires further validation before production recruitment use.

## Developed With

**Python | Artificial Intelligence | Machine Learning | NLP | FastAPI | Gemini AI | MySQL | HTML | CSS | JavaScript**