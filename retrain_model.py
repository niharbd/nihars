
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load and prepare data
df = pd.read_csv("signals_log.csv")
df.dropna(inplace=True)

features = [
    "ema_diff", "rsi", "macd_hist", "adx",
    "atr", "atr_ratio", "rvol"
]
X = df[features]
y = df["result"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save updated model
joblib.dump(model, "model.pkl")

print("✅ Model retrained and saved as model.pkl")
