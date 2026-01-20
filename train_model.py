import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import joblib

# Create a simple synthetic house price dataset
np.random.seed(42)
n_samples = 1000

# Features: bedrooms, bathrooms, sqft, age
data = {
    'bedrooms': np.random.randint(1, 6, n_samples),
    'bathrooms': np.random.randint(1, 4, n_samples),
    'sqft': np.random.randint(800, 5000, n_samples),
    'age': np.random.randint(0, 50, n_samples),
}

df = pd.DataFrame(data)

# Generate target: house price (simplified formula)
df['price'] = (
    50000 +
    df['bedrooms'] * 30000 +
    df['bathrooms'] * 25000 +
    df['sqft'] * 150 +
    df['age'] * -2000 +
    np.random.normal(0, 50000, n_samples)
)

# Prepare features and target
X = df[['bedrooms', 'bathrooms', 'sqft', 'age']]
y = df['price']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train model
model = LinearRegression()
model.fit(X_train_scaled, y_train)

# Evaluate
train_score = model.score(X_train_scaled, y_train)
test_score = model.score(X_test_scaled, y_test)

print(f"Training R² Score: {train_score:.4f}")
print(f"Testing R² Score: {test_score:.4f}")

# Save model and scaler
joblib.dump(model, 'house_price_model.joblib')
joblib.dump(scaler, 'scaler.joblib')

print("\nModel and scaler saved successfully!")
print("Files created: house_price_model.joblib, scaler.joblib")
