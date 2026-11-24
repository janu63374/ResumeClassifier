
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
    file_paths = filedialog.askopenfilenames(
        title="Select Multiple Resumes",
        filetypes=[("PDF Files", "*.pdf")]
    )

    if not file_paths:
        return

    total = len(file_paths)
    successful = 0
    failed = 0
    results = []

    print(f"\nStarting batch classification: {total} resumes")

    for index, file_path in enumerate(file_paths, start=1):
        file_name = Path(file_path).name

        try:
            print(f"\nProcessing {index}/{total}: {file_name}")

            # Extract PDF text
            original_text = extract_pdf_text(file_path)

            if not original_text.strip():
                failed += 1
                results.append(
                    f"{file_name} - No selectable text found"
                )
                continue

            # Clean extracted text
            cleaned_text = clean_text(original_text)

            if not cleaned_text.strip():
                failed += 1
                results.append(
                    f"{file_name} - No useful text found"
                )
                continue

            # Predict resume category
            features = vectorizer.transform([cleaned_text])
            prediction = model.predict(features)[0]

            # Save resume in predicted category folder
            saved_path = save_resume(file_path, prediction)

            successful += 1
            results.append(
                f"{file_name} → {prediction}"
            )

            print(f"Predicted: {prediction}")
            print(f"Saved: {saved_path}")

        except Exception as error:
            failed += 1
            results.append(
                f"{file_name} - Error: {error}"
            )
            print(f"Error processing {file_name}: {error}")

    # Update GUI
    refresh_category_counts()

    file_label.config(
        text=f"{total} resumes selected"
    )

    result_label.config(
        text=f"Completed: {successful} successful | {failed} failed",
        foreground="#15803D" if failed == 0 else "#B45309"
    )



    # Display batch results
    result_window = tk.Toplevel(root)
    result_window.title("Classification Results")
    result_window.geometry("650x500")
    result_window.configure(bg="#F3F6FB")
    result_window.transient(root)

    # Main heading
    tk.Label(
        result_window,
        text="Batch Classification Results",
        font=("Segoe UI", 16, "bold"),
        bg="#F3F6FB",
        fg="#172554"
    ).pack(pady=(15, 5))

    # Summary
    tk.Label(
        result_window,
        text=f"Total: {total} | Successful: {successful} | Failed: {failed}",
        font=("Segoe UI", 10, "bold"),
        bg="#F3F6FB",
        fg="#475569"
    ).pack(pady=5)

    # Results area
    results_frame = tk.Frame(result_window, bg="white")
    results_frame.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=10
    )

    scrollbar = ttk.Scrollbar(results_frame)
    scrollbar.pack(side="right", fill="y")

    results_text = tk.Text(
        results_frame,
        font=("Segoe UI", 10),
        wrap="word",
        yscrollcommand=scrollbar.set,
        padx=10,
        pady=10
    )
    results_text.pack(fill="both", expand=True)

    scrollbar.config(command=results_text.yview)

    for result in results:
        results_text.insert("end", result + "\n\n")

    results_text.config(state="disabled")

    # OK button - fixed bottom section
    button_frame = tk.Frame(result_window, bg="#F3F6FB")
    button_frame.pack(fill="x", side="bottom", pady=12)

    ok_button = tk.Button(
        button_frame,
        text="OK",
        font=("Segoe UI", 10, "bold"),
        bg="#172554",
        fg="white",
        activebackground="#1E40AF",
        activeforeground="white",
        width=15,
        relief="flat",
        cursor="hand2",
        command=result_window.destroy
    )
    ok_button.pack()

    print("OK BUTTON CREATED")
    print("Button size:", ok_button.winfo_reqwidth(), ok_button.winfo_reqheight())
    print("Button visible:", ok_button.winfo_ismapped())

    # Display window
    result_window.update_idletasks()
    result_window.deiconify()
    result_window.lift()
    result_window.focus_force()

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
    text="Choose Resume PDFs",
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
