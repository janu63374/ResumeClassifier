
import joblib
import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay
)

# Load trained model
model = joblib.load("models/resume_classifier.pkl")

# Load testing data
data = joblib.load("models/train_test_data.pkl")

X_test = data["X_test"]
y_test = data["y_test"]

# Predict resume categories
y_pred = model.predict(X_test)

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)

print("\nMODEL EVALUATION RESULTS")
print("-" * 40)

print(f"Accuracy: {accuracy * 100:.2f}%")

# Classification report
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Generate confusion matrix
cm = confusion_matrix(
    y_test,
    y_pred,
    labels=model.classes_
)

print("\nConfusion Matrix:")
print(cm)

# Display confusion matrix
display = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=model.classes_
)

display.plot(cmap="Blues", xticks_rotation=45)
plt.title("Resume Classification Confusion Matrix")
plt.tight_layout()

# Save confusion matrix image
plt.savefig("confusion_matrix.png")

plt.show()

print("\nConfusion matrix saved successfully!")
