import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# 1. Load the synthetic dataset
print("Loading dataset...")
data_path = "../data/triage_training_data.csv"
df = pd.read_csv(data_path)

# 2. Define our Features (X) and Target (y)
# We drop the patient_id (it's just a label) and the target column
X = df.drop(columns=["patient_id", "target_t_safe_mins"])
y = df["target_t_safe_mins"]

# 3. Split the data (80% to train the AI, 20% to test it)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Initialize and Train the Random Forest Model
print("Training the Random Forest AI Model...")
model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
model.fit(X_train, y_train)

# 5. Evaluate the Model (To prove it actually learned the rules)
predictions = model.predict(X_test)
mae = mean_absolute_error(y_test, predictions)
print(f"Model Training Complete!")
print(f"Mean Absolute Error: {mae:.2f} minutes")
print(f"(This means on average, the AI's prediction is within {mae:.2f} minutes of the true clinical safe time).")

# 6. Save the trained "Brain" to a file so our FastAPI server can use it later
model_filename = "triage_model.pkl"
with open(model_filename, "wb") as file:
    pickle.dump(model, file)

print(f"Saved trained model to model/{model_filename}")