
import os

dataset_path = "dataset"

categories = ["Engineering", "Finance", "HR", "Sales"]

total = 0

print("\nRESUME DATASET SUMMARY")
print("-" * 30)

for category in categories:
    folder = os.path.join(dataset_path, category)

    if os.path.exists(folder):
        files = [
            f for f in os.listdir(folder)
            if f.lower().endswith(".pdf")
        ]

        count = len(files)
        total += count

        print(f"{category}: {count} resumes")
    else:
        print(f"{category}: Folder not found")

print("-" * 30)
print(f"Total resumes: {total}")
