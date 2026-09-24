"""Build EDA charts + churn ML model. Run: py build_analysis_ml.py"""
import pandas as pd, numpy as np, json, pickle, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

os.makedirs("analysis/charts", exist_ok=True)
os.makedirs("ml", exist_ok=True)

cust = pd.read_csv("data/customers.csv")
subs = pd.read_csv("data/subscriptions.csv")
usage = pd.read_csv("data/usage_monthly.csv")
billing = pd.read_csv("data/billing.csv")
tickets = pd.read_csv("data/support_tickets.csv")
churn = pd.read_csv("data/churn_labels.csv")
network = pd.read_csv("data/network_quality.csv")

df = cust.merge(subs, on="customer_id").merge(churn, on="customer_id")

# Aggregated features
agg_u = usage.groupby("customer_id").agg(calls_mean=("calls_minutes","mean"), data_mean=("data_gb","mean"),
  downtime_mean=("downtime_hours","mean"), slow_mean=("slow_days","mean"), app_mean=("app_usage_hours","mean"))
agg_b = billing.groupby("customer_id").agg(late_mean=("late_days","mean"), fail_sum=("payment_failures","sum"),
  due_mean=("amount_due_egp","mean"), paid_ratio=("amount_paid_egp", lambda x: (x>0).mean()))
agg_t = tickets.groupby("customer_id").agg(ticket_cnt=("ticket_id","count"), sat_mean=("satisfaction_score","mean"), hrs_mean=("handling_time_hours","mean"))
model_df = df.set_index("customer_id").join([agg_u, agg_b, agg_t])
model_df["ticket_cnt"] = model_df["ticket_cnt"].fillna(0)
model_df["sat_mean"] = model_df["sat_mean"].fillna(4.2)
model_df["hrs_mean"] = model_df["hrs_mean"].fillna(0)
model_df = model_df.reset_index()

plt.rcParams.update({"figure.figsize": (8,5)})

def save_bar(series, title, xlabel, fname):
    plt.figure(); series.plot(kind="bar", color=["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd","#8c564b"][:len(series)])
    plt.title(title); plt.xlabel(xlabel); plt.ylabel("Churn rate"); plt.xticks(rotation=20, ha="right"); plt.tight_layout()
    plt.savefig(f"analysis/charts/{fname}", dpi=130); plt.close()

# 1 overall
rate = df["churned"].mean()
plt.figure(); plt.bar(["Stayed","Churned"], [1-rate, rate], color=["#2ca02c","#d62728"])
plt.title(f"Overall churn rate = {rate:.1%} (n=5000)"); plt.tight_layout()
plt.savefig("analysis/charts/01_overall_churn.png", dpi=130); plt.close()

save_bar(df.groupby("contract_type")["churned"].mean(), "Churn by contract type", "Contract", "02_churn_by_contract.png")
save_bar(df.groupby("plan_name")["churned"].mean(), "Churn by plan", "Plan", "03_churn_by_plan.png")
save_bar(df.groupby("payment_method")["churned"].mean(), "Churn by payment method", "Payment", "04_churn_by_payment.png")
save_bar(df.groupby("region")["churned"].mean(), "Churn by region", "Region", "05_churn_by_region.png")
save_bar(df.groupby("internet_service")["churned"].mean(), "Churn by internet service", "Internet", "06_churn_by_internet.png")
save_bar(churn.groupby("churn_reason").size(), "Churn reasons (count)", "Reason", "07_churn_reasons.png")

plt.figure(); plt.hist([df[df.churned==0]["monthly_charge_egp"], df[df.churned==1]["monthly_charge_egp"]], bins=30, label=["Stayed","Churned"], alpha=0.7)
plt.title("Monthly charge distribution: churned pay more"); plt.xlabel("EGP / month"); plt.legend(); plt.tight_layout()
plt.savefig("analysis/charts/08_monthly_charge_hist.png", dpi=130); plt.close()

plt.figure(); plt.hist([df[df.churned==0]["tenure_months"], df[df.churned==1]["tenure_months"]], bins=30, label=["Stayed","Churned"], alpha=0.7)
plt.title("Tenure: new customers churn more"); plt.xlabel("Months"); plt.legend(); plt.tight_layout()
plt.savefig("analysis/charts/09_tenure_hist.png", dpi=130); plt.close()

plt.figure()
tmp = tickets.merge(churn, on="customer_id")
tmp.groupby("satisfaction_score")["churned"].mean().plot(kind="bar", color="#ff7f0e")
plt.title("Churn by satisfaction score"); plt.xlabel("Satisfaction 1-5"); plt.ylabel("Churn rate"); plt.tight_layout()
plt.savefig("analysis/charts/10_satisfaction_churn.png", dpi=130); plt.close()

plt.figure(); network.groupby("month")["outage_hours"].mean().plot(kind="line", marker="o")
plt.title("Avg outage hours per month (all regions)"); plt.xticks(rotation=45); plt.tight_layout()
plt.savefig("analysis/charts/11_outage_trend.png", dpi=130); plt.close()

# ---- ML ----
cat_cols = ["gender","city","region","contract_type","payment_method","senior_citizen","partner","dependents","paperless_billing",
            "plan_name","internet_service","phone_service","multiple_lines","online_security","tech_support","streaming_tv","device_protection"]
num_cols = ["age","tenure_months","monthly_charge_egp","total_charge_egp","calls_mean","data_mean","downtime_mean","slow_mean","app_mean",
            "late_mean","fail_sum","due_mean","paid_ratio","ticket_cnt","sat_mean","hrs_mean"]
X = pd.get_dummies(model_df[cat_cols+num_cols], drop_first=True)
y = model_df["churned"]
cols = X.columns.tolist()
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
clf = RandomForestClassifier(n_estimators=200, max_depth=14, min_samples_leaf=4, random_state=42, n_jobs=-1)
clf.fit(X_train, y_train)
pred = clf.predict(X_test); proba = clf.predict_proba(X_test)[:,1]
metrics = {"accuracy": round(float(accuracy_score(y_test,pred)),4),
  "precision": round(float(precision_score(y_test,pred)),4),
  "recall": round(float(recall_score(y_test,pred)),4),
  "f1": round(float(f1_score(y_test,pred)),4),
  "roc_auc": round(float(roc_auc_score(y_test,proba)),4),
  "n_train": len(X_train), "n_test": len(X_test), "churn_rate": round(float(y.mean()),4)}
with open("ml/metrics.json","w") as f: json.dump(metrics, f, indent=2)
with open("ml/model.pkl","wb") as f: pickle.dump({"model": clf, "columns": cols}, f)

# confusion matrix
cm = confusion_matrix(y_test, pred)
plt.figure(); plt.imshow(cm, cmap="Blues"); plt.title(f"Confusion matrix (acc={metrics['accuracy']})")
plt.xticks([0,1],["Stayed","Churn"]); plt.yticks([0,1],["Stayed","Churn"])
for i in range(2):
    for j in range(2): plt.text(j, i, cm[i,j], ha="center", va="center", fontsize=14)
plt.xlabel("Predicted"); plt.ylabel("True"); plt.tight_layout()
plt.savefig("analysis/charts/12_confusion_matrix.png", dpi=130); plt.close()

# feature importance top 15
imp = pd.Series(clf.feature_importances_, index=cols).sort_values(ascending=False).head(15)
plt.figure(figsize=(9,5)); imp.sort_values().plot(kind="barh", color="#1f77b4")
plt.title("Top 15 churn drivers (RandomForest)"); plt.tight_layout()
plt.savefig("analysis/charts/13_feature_importance.png", dpi=130); plt.close()

# summary for README / dashboard
summary = {"churn_rate": round(float(rate),4), "total_customers": 5000,
  "total_usage_rows": len(usage), "total_billing_rows": len(billing), "total_tickets": len(tickets),
  "metrics": metrics, "top_features": imp.index.tolist()}
with open("analysis/summary.json","w") as f: json.dump(summary, f, indent=2)
print("OK", summary)
