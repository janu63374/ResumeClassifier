
import pandas as pd
import re
import nltk

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download required NLTK resources
nltk.download("stopwords")
nltk.download("punkt")
nltk.download("punkt_tab")

# Load extracted resume dataset
df = pd.read_csv("resumes.csv")

# Load English stopwords
stop_words = set(stopwords.words("english"))

# Text cleaning function
def clean_text(text):

    text = str(text).lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", " ", text)

    # Remove email addresses
    text = re.sub(r"\S+@\S+", " ", text)

    # Remove special characters and numbers
    text = re.sub(r"[^a-z\s]", " ", text)

    # Tokenization
    words = word_tokenize(text)

    # Remove stopwords and short words
    words = [
        word for word in words
        if word not in stop_words and len(word) > 2
    ]

    return " ".join(words)


# Apply text preprocessing
df["Cleaned_Text"] = df["Text"].apply(clean_text)

# Save preprocessed dataset
df.to_csv("processed_resumes.csv", index=False)

print("\nTEXT PREPROCESSING COMPLETED")
print("Total resumes processed:", len(df))

print("\nCategory Summary:")
print(df["Category"].value_counts())

print("\nSample Cleaned Resume:")
print(df["Cleaned_Text"].iloc[0][:500])
