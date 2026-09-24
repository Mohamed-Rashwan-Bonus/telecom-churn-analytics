"""Predict churn for new customers. Usage: py predict.py --input data/new_customers.csv --output data/predictions.csv
If no input given, it scores 5 demo customers.
"""
import argparse, pickle, pandas as pd

def load_model():
    with open("ml/model.pkl", "rb") as f:
        return pickle.load(f)

def predict(df, bundle):
    model, cols = bundle["model"], bundle["columns"]
    X = pd.get_dummies(df, drop_first=True)
    for c in cols:
        if c not in X.columns: X[c] = 0
    X = X[cols]
    df["churn_probability"] = model.predict_proba(X)[:, 1].round(4)
    df["will_churn"] = (df["churn_probability"] > 0.5).astype(int)
    df["risk"] = pd.cut(df["churn_probability"], bins=[0, 0.3, 0.6, 1.0], labels=["Low", "Medium", "High"])
    return df

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="")
    ap.add_argument("--output", default="data/predictions.csv")
    a = ap.parse_args()
    bundle = load_model()
    if a.input:
        df = pd.read_csv(a.input)
    else:
        df = pd.DataFrame([{
            "gender": "Male", "city": "Cairo", "region": "Greater Cairo", "contract_type": "Month-to-month",
            "payment_method": "Electronic check", "senior_citizen": "No", "partner": "No", "dependents": "No",
            "paperless_billing": "Yes", "plan_name": "Plus", "internet_service": "Fiber", "phone_service": "Yes",
            "multiple_lines": "Yes", "online_security": "No", "tech_support": "No", "streaming_tv": "Yes",
            "device_protection": "No", "age": 34, "tenure_months": 4, "monthly_charge_egp": 420,
            "total_charge_egp": 1680, "calls_mean": 350, "data_mean": 45, "downtime_mean": 2.5,
            "slow_mean": 3, "app_mean": 50, "late_mean": 4, "fail_sum": 1, "due_mean": 420,
            "paid_ratio": 0.8, "ticket_cnt": 3, "sat_mean": 2.0, "hrs_mean": 40} for _ in range(5)])
    out = predict(df, bundle)
    out.to_csv(a.output, index=False)
    print(out[["churn_probability", "will_churn", "risk"]].head())
    print(f"saved to {a.output}")
