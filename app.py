
import os
import re
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import time

import joblib
import pymupdf
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


# Project paths
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "resume_classifier.pkl"
VECTORIZER_PATH = BASE_DIR / "models" / "tfidf_vectorizer.pkl"
OUTPUT_DIR = BASE_DIR / "categorized_resumes"

CATEGORIES = ["Engineering", "Finance", "HR", "Sales"]

# Ensure category folders exist
for category in CATEGORIES:
    (OUTPUT_DIR / category).mkdir(parents=True, exist_ok=True)

# Load trained model and vectorizer
model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

# Load NLTK stopwords
try:
    stop_words = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords", quiet=True)
    stop_words = set(stopwords.words("english"))

try:
    word_tokenize("test")
except LookupError:
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)


def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"[^a-z\s]", " ", text)

    words = word_tokenize(text)
    words = [
        word for word in words
        if word not in stop_words and len(word) > 2
    ]

    return " ".join(words)


def extract_pdf_text(file_path):
    text_parts = []

    with pymupdf.open(file_path) as document:
        for page in document:
            text_parts.append(page.get_text())

    return "\n".join(text_parts)


def save_resume(file_path, category):
    destination = OUTPUT_DIR / category / Path(file_path).name

    counter = 1
    while destination.exists():
        new_name = (
            f"{Path(file_path).stem}_{counter}"
            f"{Path(file_path).suffix}"
        )
        destination = OUTPUT_DIR / category / new_name
        counter += 1

    shutil.copy2(file_path, destination)
    return destination


def refresh_category_counts():
    for category, label in count_labels.items():
        folder = OUTPUT_DIR / category
        count = len(list(folder.glob("*.pdf")))
        label.config(text=f"{count} resumes")


def open_category_folder(category):
    folder = OUTPUT_DIR / category
    os.startfile(str(folder))



import time

def classify_resume():
    file_path = filedialog.askopenfilename(
        title="Select a Resume",
        filetypes=[("PDF Files", "*.pdf")]
    )

    if not file_path:
        return

    try:
        start = time.time()
        print("\nStarting resume classification...")

        print("Extracting PDF text...")
        original_text = extract_pdf_text(file_path)
        print(f"Text extraction: {time.time() - start:.2f} seconds")

        if not original_text.strip():
            messagebox.showwarning(
                "No Text Found",
                "No selectable text found in this PDF."
            )
            return

        print("Cleaning text...")
        clean_start = time.time()
        cleaned_text = clean_text(original_text)
        print(f"Text cleaning: {time.time() - clean_start:.2f} seconds")

        if not cleaned_text.strip():
            messagebox.showwarning(
                "Invalid Resume",
                "No useful text found."
            )
            return

        print("Predicting category...")
        predict_start = time.time()
        features = vectorizer.transform([cleaned_text])
        prediction = model.predict(features)[0]
        print(f"Prediction: {time.time() - predict_start:.2f} seconds")

        print("Saving resume...")
        save_start = time.time()
        saved_path = save_resume(file_path, prediction)
        print(f"Saving: {time.time() - save_start:.2f} seconds")

        result_label.config(
            text=f"Predicted Category: {prediction}",
            foreground="#15803D"
        )

        file_label.config(
            text=f"File: {Path(file_path).name}"
        )

        refresh_category_counts()

        print(f"TOTAL TIME: {time.time() - start:.2f} seconds")

        messagebox.showinfo(
            "Classification Successful",
            f"Category: {prediction}\n\nResume saved to:\n{saved_path}"
        )

    except Exception as error:
        messagebox.showerror("Classification Error", str(error))

# ---------------- GUI ----------------

root = tk.Tk()
root.title("Resume Classifier System")
root.geometry("950x650")
root.minsize(850, 600)
root.configure(bg="#F3F6FB")

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "TButton",
    font=("Segoe UI", 10, "bold"),
    padding=10
)

style.configure(
    "Category.TButton",
    font=("Segoe UI", 10, "bold"),
    padding=12
)

# Header
header = tk.Frame(root, bg="#172554", height=135)
header.pack(fill="x")
header.pack_propagate(False)

tk.Label(
    header,
    text="RESUME CLASSIFIER",
    font=("Segoe UI", 25, "bold"),
    bg="#172554",
    fg="white"
).pack(pady=(25, 5))

tk.Label(
    header,
    text="AI-powered Resume Classification System",
    font=("Segoe UI", 11),
    bg="#172554",
    fg="#CBD5E1"
).pack()

# Main content
main = tk.Frame(root, bg="#F3F6FB")
main.pack(fill="both", expand=True, padx=35, pady=25)

tk.Label(
    main,
    text="Upload and Classify Resume",
    font=("Segoe UI", 18, "bold"),
    bg="#F3F6FB",
    fg="#172554"
).pack(anchor="w")

tk.Label(
    main,
    text="Select a PDF resume. The trained machine learning model "
         "will predict its category automatically.",
    font=("Segoe UI", 10),
    bg="#F3F6FB",
    fg="#64748B",
    wraplength=850
).pack(anchor="w", pady=(5, 20))

# Upload card
upload_card = tk.Frame(
    main,
    bg="white",
    highlightbackground="#DCE3EF",
    highlightthickness=1
)
upload_card.pack(fill="x", pady=5)

tk.Label(
    upload_card,
    text="PDF Resume Upload",
    font=("Segoe UI", 13, "bold"),
    bg="white",
    fg="#172554"
).pack(pady=(20, 8))

ttk.Button(
    upload_card,
    text="Choose Resume PDF",
    command=classify_resume
).pack(pady=8)

file_label = tk.Label(
    upload_card,
    text="No resume selected",
    font=("Segoe UI", 9),
    bg="white",
    fg="#64748B"
)
file_label.pack(pady=5)

result_label = tk.Label(
    upload_card,
    text="Predicted Category: Waiting for upload",
    font=("Segoe UI", 13, "bold"),
    bg="white",
    fg="#475569"
)
result_label.pack(pady=(8, 20))

# Category section
tk.Label(
    main,
    text="Categorized Resume Folders",
    font=("Segoe UI", 16, "bold"),
    bg="#F3F6FB",
    fg="#172554"
).pack(anchor="w", pady=(25, 12))

category_frame = tk.Frame(main, bg="#F3F6FB")
category_frame.pack(fill="x")

count_labels = {}

for index, category in enumerate(CATEGORIES):
    card = tk.Frame(
        category_frame,
        bg="white",
        highlightbackground="#DCE3EF",
        highlightthickness=1
    )
    card.grid(
        row=0,
        column=index,
        padx=6,
        pady=5,
        sticky="nsew"
    )

    tk.Label(
        card,
        text=category,
        font=("Segoe UI", 11, "bold"),
        bg="white",
        fg="#172554"
    ).pack(pady=(15, 5))

    count_label = tk.Label(
        card,
        text="0 resumes",
        font=("Segoe UI", 9),
        bg="white",
        fg="#64748B"
    )
    count_label.pack(pady=5)

    count_labels[category] = count_label

    ttk.Button(
        card,
        text="Open Folder",
        style="Category.TButton",
        command=lambda c=category: open_category_folder(c)
    ).pack(padx=10, pady=(5, 15))

    category_frame.grid_columnconfigure(index, weight=1)

# Footer
tk.Label(
    root,
    text="Resume Classifier System | Python | NLP | TF-IDF | "
         "Logistic Regression",
    font=("Segoe UI", 9),
    bg="#E2E8F0",
    fg="#475569",
    pady=12
).pack(fill="x", side="bottom")

refresh_category_counts()

root.mainloop()
