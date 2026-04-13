import pandas as pd
import numpy as np
import json
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from sklearn.ensemble import RandomForestRegressor

DATA_PATH = "dataset/winequality-red.csv"
MODEL_PATH = "output/model/model.joblib"
RESULTS_PATH = "output/results/results.json"

os.makedirs("output/model", exist_ok=True)
os.makedirs("output/results", exist_ok=True)

df = pd.read_csv(DATA_PATH, sep=';')

X = df.drop("quality", axis=1)
y = df["quality"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

model = RandomForestRegressor(
    n_estimators=200,
    max_depth=12,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)
y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"MSE : {mse}")
print(f"R2 Score : {r2}")

joblib.dump(model, MODEL_PATH)

results = {
    "mse": mse,
    "r2": r2,
    "accuracy" : r2
}

with open(RESULTS_PATH, "w") as f:
    json.dump(results, f, indent=4)
