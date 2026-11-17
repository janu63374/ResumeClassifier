
import os
import pymupdf
import pandas as pd

dataset_path = "dataset"

categories = ["Engineering", "Finance", "HR", "Sales"]

resume_data = []

for category in categories:

    folder_path = os.path.join(dataset_path, category)

    for filename in os.listdir(folder_path):

        if filename.lower().endswith(".pdf"):

            file_path = os.path.join(folder_path, filename)

            try:
                document = pymupdf.open(file_path)

                text = ""

                for page in document:
                    text += page.get_text()

                document.close()

                if text.strip():
                    resume_data.append({
                        "Resume": filename,
                        "Category": category,
                        "Text": text
                    })

                    print(f"Extracted: {filename}")

                else:
                    print(f"Empty PDF: {filename}")

            except Exception as e:
                print(f"Error reading {filename}: {e}")

# Convert extracted data into DataFrame
df = pd.DataFrame(resume_data)

# Save extracted text
df.to_csv("resumes.csv", index=False)

print("\nTEXT EXTRACTION COMPLETED")
print("Total extracted resumes:", len(df))
print("\nCategory Summary:")
print(df["Category"].value_counts())
