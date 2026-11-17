
import joblib
import os

from sklearn.linear_model import LogisticRegression

# Load training and testing data
data = joblib.load("models/train_test_data.pkl")

X_train = data["X_train"]
y_train = data["y_train"]

# Initialize Logistic Regression model
model = LogisticRegression(
    max_iter=1000,
    random_state=42
)

# Train the model
print("Training Resume Classification Model...")

model.fit(X_train, y_train)

# Create models folder if not exists
os.makedirs("models", exist_ok=True)

# Save trained model
joblib.dump(model, "models/resume_classifier.pkl")

print("\nMODEL TRAINING COMPLETED")
print("Model: Logistic Regression")
print("Training samples:", X_train.shape[0])
print("Model saved successfully!")
print("\nResume Categories:")
print(model.classes_)
