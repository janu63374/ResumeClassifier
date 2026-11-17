
import pandas as pd
import os
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

# Load preprocessed dataset
df = pd.read_csv("processed_resumes.csv")

# Remove missing and empty text
df = df.dropna(subset=["Cleaned_Text", "Category"])
df = df[df["Cleaned_Text"].str.strip() != ""]

# Separate features and labels
X = df["Cleaned_Text"]
y = df["Category"]

# Split dataset into training and testing data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Initialize TF-IDF Vectorizer
tfidf = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2)
)

# Fit on training data and transform
X_train_tfidf = tfidf.fit_transform(X_train)

# Transform testing data
X_test_tfidf = tfidf.transform(X_test)

# Create models folder if not exists
os.makedirs("models", exist_ok=True)

# Save TF-IDF vectorizer
joblib.dump(tfidf, "models/tfidf_vectorizer.pkl")

# Save training and testing data
joblib.dump(
    {
        "X_train": X_train_tfidf,
        "X_test": X_test_tfidf,
        "y_train": y_train,
        "y_test": y_test
    },
    "models/train_test_data.pkl"
)

print("\nTF-IDF FEATURE EXTRACTION COMPLETED")

print("\nDataset Information:")
print("Total resumes:", len(df))
print("Training samples:", X_train_tfidf.shape[0])
print("Testing samples:", X_test_tfidf.shape[0])

print("\nFeature Information:")
print("Total TF-IDF features:", len(tfidf.get_feature_names_out()))
print("Training feature matrix:", X_train_tfidf.shape)
print("Testing feature matrix:", X_test_tfidf.shape)

print("\nCategory Distribution:")
print(y.value_counts())
