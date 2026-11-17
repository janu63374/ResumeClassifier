
# Resume Classifier System

An AI-powered Resume Classification System developed using Python and Machine Learning. It automatically extracts text from PDF resumes, predicts their categories, and organizes them into separate folders.

## Features

- Upload PDF resumes through a Tkinter GUI.
- Extract text using PyMuPDF.
- Preprocess resume text using NLTK.
- Convert text into numerical features using TF-IDF.
- Classify resumes using Logistic Regression.
- Automatically save resumes into categorized folders.
- View categorized resumes through the GUI.

## Resume Categories

- Engineering
- Finance
- HR
- Sales

## Technologies Used

- Python
- Tkinter
- Pandas and NumPy
- NLTK
- PyMuPDF
- Scikit-learn
- TF-IDF
- Logistic Regression
- Joblib
- Matplotlib

## Model Performance

- Algorithm: Logistic Regression
- Feature Extraction: TF-IDF
- Dataset: 200 PDF resumes
- Training Samples: 160
- Testing Samples: 40
- Test Accuracy: 95%

## Project Structure

```text
ResumeClassifier/
├── dataset/
├── categorized_resumes/
├── models/
├── app.py
├── extract_text.py
├── preprocess.py
├── feature_extraction.py
├── train_model.py
├── evaluate_model.py
├── check_dataset.py
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:

   git clone YOUR_GITHUB_REPOSITORY_URL

2. Navigate to the project folder:

   cd ResumeClassifier

3. Create a virtual environment:

   python -m venv venv

4. Activate the environment:

   .\venv\Scripts\activate

5. Install dependencies:

   pip install -r requirements.txt

## Run the Application

python app.py

## How It Works

1. Upload a PDF resume.
2. Extract text from the PDF.
3. Clean and preprocess the extracted text.
4. Transform the text using the trained TF-IDF vectorizer.
5. Predict the resume category using Logistic Regression.
6. Save the resume into its corresponding category folder.

## Project Objective

To simplify resume classification by using Natural Language Processing and Machine Learning techniques.

## Developed Using

Python | Machine Learning | NLP | Tkinter
