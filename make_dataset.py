"""Generate complex Telecom Churn dataset (7 tables, ~130k rows). Run with: py make_dataset.py"""
import random, numpy as np, pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta

SEED = 42
N = 5000
random.seed(SEED); np.random.seed(SEED)

cities = [("Cairo", "Greater Cairo"), ("Giza", "Greater Cairo"), ("Alexandria", "Delta"),
          ("Tanta", "Delta"), ("Mansoura", "Delta"), ("Assiut", "Upper Egypt"),
          ("Luxor", "Upper Egypt"), ("Aswan", "Upper Egypt"), ("Port Said", "Suez"),
          ("Suez", "Suez"), ("Ismailia", "Suez"), ("Hurghada", "Red Sea")]
plans = ["Basic", "Plus", "Ultra", "Business"]
internet = ["DSL", "Fiber", "5G", "No Internet"]
contracts = ["Month-to-month", "One year", "Two year"]
pay_methods = ["Electronic check", "Mailed check", "Bank transfer", "Credit card"]

# 1) customers
rows = []
for i in range(1, N+1):
    cid = f"C{10000+i}"
    gender = random.choice(["Male", "Female"])
    age = int(np.clip(np.random.normal(42, 14), 18, 80))
    city, region = random.choice(cities)
    join = date(2020, 1, 1) + relativedelta(days=random.randint(0, 1450))
    contract = random.choices(contracts, weights=[0.52, 0.28, 0.20])[0]
    pay = random.choices(pay_methods, weights=[0.34, 0.18, 0.24, 0.24])[0]
    rows.append([cid, gender, age, city, region, join.isoformat(), contract, pay,
                 random.choices(["Yes","No"], weights=[0.16,0.84])[0],  # senior
                 random.choice(["Yes","No"]),  # partner
                 random.choice(["Yes","No"]),  # dependents
                 random.choices(["Yes","No"], weights=[0.78, 0.22])[0]])  # paperless
customers = pd.DataFrame(rows, columns=["customer_id","gender","age","city","region","join_date","contract_type","payment_method","senior_citizen","partner","dependents","paperless_billing"])
customers.to_csv("data/customers.csv", index=False)

# 2) subscriptions
subs = []
for _, r in customers.iterrows():
    plan = random.choices(plans, weights=[0.32, 0.33, 0.22, 0.13])[0]
    inet = random.choices(internet, weights=[0.28, 0.42, 0.22, 0.08])[0]
    phone = "Yes" if random.random() < (0.92 if plan != "Basic" else 0.78) else "No"
    tenure = max(1, int((date(2024,12,31) - date.fromisoformat(r["join_date"])).days / 30.4 + np.random.normal(0, 1.5)))
    tenure = min(tenure, 60)
    base = {"Basic": 180, "Plus": 320, "Ultra": 520, "Business": 750}[plan]
    if inet == "Fiber": base += 60
    if inet == "5G": base += 90
    monthly = round(base + np.random.normal(0, 25) + (20 if r["contract_type"]=="Month-to-month" else 0), 2)
    total = round(monthly * tenure + np.random.normal(0, 80), 2)
    subs.append([f"S{10000+len(subs)+1}", r["customer_id"], plan, inet, phone,
                 random.choice(["Yes","No"]) if phone=="Yes" else "No phone",
                 random.choice(["Yes","No"]), random.choice(["Yes","No"]),
                 random.choice(["Yes","No"]), random.choice(["Yes","No"]),
                 monthly, total, tenure])
subscriptions = pd.DataFrame(subs, columns=["sub_id","customer_id","plan_name","internet_service","phone_service","multiple_lines","online_security","tech_support","streaming_tv","device_protection","monthly_charge_egp","total_charge_egp","tenure_months"])
subscriptions.to_csv("data/subscriptions.csv", index=False)

# 3) usage_monthly (12 months 2024)
months = pd.date_range("2024-01-01", "2024-12-01", freq="MS").strftime("%Y-%m").tolist()
urows = []
for _, s in subscriptions.iterrows():
    heavy = 1.4 if s["plan_name"] in ("Ultra","Business") else 1.0
    fib = 1.2 if s["internet_service"]=="Fiber" else 1.0
    for m in months:
        calls = max(0, int(np.random.normal(320*heavy, 110)))
        sms = max(0, int(np.random.normal(140, 70)))
        data = round(max(0.5, np.random.normal(38*heavy*fib, 14)), 1)
        roam = round(max(0, np.random.exponential(0.8)), 1)
        app = round(max(0, np.random.normal(46*heavy, 18)), 1)
        down = round(max(0, np.random.exponential(1.1 if s["internet_service"]=="Fiber" else 0.6)), 1)
        slow = max(0, int(np.random.poisson(1.6 if s["internet_service"]=="Fiber" else 0.7)))
        urows.append([s["customer_id"], m, calls, sms, data, roam, app, down, slow])
usage = pd.DataFrame(urows, columns=["customer_id","month","calls_minutes","sms_count","data_gb","roaming_gb","app_usage_hours","downtime_hours","slow_days"])
usage.to_csv("data/usage_monthly.csv", index=False)

# 4) billing
brows = []
bid = 1
for _, s in subscriptions.iterrows():
    for m in months:
        due = round(s["monthly_charge_egp"] + np.random.normal(0, 12) - (random.choice([0,0,0,25,50]) if random.random()<0.12 else 0), 2)
        fail = 1 if random.random() < (0.14 if customers.set_index("customer_id").loc[s["customer_id"],"payment_method"]=="Electronic check" else 0.05) else 0
        late = max(0, int(np.random.exponential(2.2)) + (random.randint(3,14) if fail else 0))
        paid = round(due if (fail==0 and random.random()>0.03) else due*random.choice([0,0.5,0.8]), 2)
        brows.append([f"B{bid}", s["customer_id"], m, max(50,due), paid, late, fail])
        bid += 1
billing = pd.DataFrame(brows, columns=["bill_id","customer_id","month","amount_due_egp","amount_paid_egp","late_days","payment_failures"])
billing.to_csv("data/billing.csv", index=False)

# 5) support_tickets (~8500)
cats = ["Network","Billing","Technical","Account"]
trows = []
tid = 1
cust_ids = customers["customer_id"].tolist()
for _ in range(8500):
    cid = random.choice(cust_ids)
    # customers with fiber / month-to-month complain more
    sub = subscriptions.set_index("customer_id").loc[cid]
    open_d = date(2024,1,1) + relativedelta(days=random.randint(0,364))
    hrs = int(np.clip(np.random.exponential(26 if sub["internet_service"]=="Fiber" else 16), 1, 200))
    close_d = open_d + relativedelta(days=min(30, hrs//24))
    sat = random.choices([1,2,3,4,5], weights=[0.14,0.18,0.22,0.24,0.22])[0]
    trows.append([f"T{tid}", cid, open_d.isoformat(), close_d.isoformat(),
                  random.choices(cats, weights=[0.38,0.27,0.22,0.13])[0],
                  random.choices(["Low","Medium","High","Critical"], weights=[0.35,0.35,0.22,0.08])[0],
                  sat, random.choices(["Yes","No"], weights=[0.86,0.14])[0], hrs])
    tid += 1
tickets = pd.DataFrame(trows, columns=["ticket_id","customer_id","open_date","close_date","category","priority","satisfaction_score","resolved","handling_time_hours"])
tickets.to_csv("data/support_tickets.csv", index=False)

# 6) network_quality (region x month)
regs = ["Greater Cairo","Delta","Upper Egypt","Suez","Red Sea"]
nrows = []
for reg in regs:
    for m in months:
        bad = reg in ("Upper Egypt","Red Sea")
        nrows.append([reg, m, round(np.random.normal(3.4 if bad else 4.1, 0.4),2),
                      round(max(0.2, np.random.normal(2.8 if bad else 1.4, 0.8)),2),
                      round(max(5, np.random.normal(28 if bad else 52, 9)),1),
                      round(max(0, np.random.exponential(2.4 if bad else 1.0)),1)])
network = pd.DataFrame(nrows, columns=["region","month","avg_signal_bars","drop_rate_pct","avg_speed_mbps","outage_hours"])
network.to_csv("data/network_quality.csv", index=False)

# 7) churn_labels with realistic logit
ticket_cnt = tickets.groupby("customer_id").size()
avg_sat = tickets.groupby("customer_id")["satisfaction_score"].mean()
late_mean = billing.groupby("customer_id")["late_days"].mean()
fail_sum = billing.groupby("customer_id")["payment_failures"].sum()
down_mean = usage.groupby("customer_id")["downtime_hours"].mean()

ch = []
for _, s in subscriptions.iterrows():
    cid = s["customer_id"]
    cust = customers.set_index("customer_id").loc[cid]
    logit = -2.1
    logit += 1.15 if cust["contract_type"]=="Month-to-month" else 0
    logit += -0.9 if cust["contract_type"]=="Two year" else 0
    logit += 0.55 if cust["payment_method"]=="Electronic check" else 0
    logit += 0.45 if cust["paperless_billing"]=="Yes" else 0
    logit += 0.35 if cust["senior_citizen"]=="Yes" and cust["partner"]=="No" else 0
    logit += 0.012 * (s["monthly_charge_egp"]-350)
    logit += -0.045 * s["tenure_months"]
    logit += 0.28 * ticket_cnt.get(cid, 0)
    logit += -0.30 * (avg_sat.get(cid, 4.0)-3)
    logit += 0.08 * late_mean.get(cid, 0)
    logit += 0.35 * fail_sum.get(cid, 0)
    logit += 0.22 * down_mean.get(cid, 0)
    logit += 0.40 if (s["internet_service"]=="Fiber" and down_mean.get(cid,0)>1.5) else 0
    logit += -0.5 if s["plan_name"]=="Business" else 0
    p = 1/(1+np.exp(-logit/2.2))
    churned = 1 if random.random() < p else 0
    if churned:
        reason = random.choices(["Price","Competitor offer","Network quality","Poor service","Moving","Other"],
                                weights=[0.28,0.22,0.20,0.14,0.08,0.08])[0]
        cdate = (date(2024, random.randint(7,12), random.randint(1,28))).isoformat()
    else:
        reason, cdate = "No churn", ""
    clv = round(s["monthly_charge_egp"]*s["tenure_months"]*random.uniform(0.7,1.3), 2)
    ch.append([cid, churned, cdate, reason, round(p,4), clv])
churn = pd.DataFrame(ch, columns=["customer_id","churned","churn_date","churn_reason","churn_probability_raw","clv_egp"])
churn.to_csv("data/churn_labels.csv", index=False)

print(f"customers {customers.shape} churn_rate {churn.churned.mean():.3f}")
print(f"subscriptions {subscriptions.shape} usage {usage.shape} billing {billing.shape} tickets {tickets.shape} network {network.shape}")
