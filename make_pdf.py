"""Build super-simple PDF guide. Run: py make_pdf.py"""
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import json

with open("analysis/summary.json") as f:
    s = json.load(f)
m = s["metrics"]

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=20)
pdf.set_left_margin(12)
pdf.set_right_margin(12)

# Cover
pdf.add_page()
pdf.set_fill_color(15,23,42)
pdf.rect(0,0,210,297, style="F")
pdf.set_y(40)
pdf.set_font("Helvetica", "B", 28)
pdf.set_text_color(250,204,21)
pdf.multi_cell(0, 14, "TELECOM CHURN ANALYTICS", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(6)
pdf.set_font("Helvetica", "", 16)
pdf.set_text_color(255,255,255)
pdf.cell(0, 10, "Power BI + Python ML", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(4)
pdf.set_font("Helvetica", "", 12)
pdf.set_text_color(203,213,225)
pdf.cell(0, 8, "5000 customers | 133k rows | 7 tables", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.cell(0, 8, f"Churn {s['churn_rate']*100:.1f}% | Acc {m['accuracy']*100:.1f}% | AUC {m['roc_auc']}", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(10)
pdf.set_font("Helvetica", "B", 14)
pdf.set_text_color(250,204,21)
pdf.cell(0, 10, "by Mohamed Rashwan - 2026", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

def title(t):
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(15,23,42)
    pdf.cell(0, 10, t, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_draw_color(250,204,21)
    pdf.set_line_width(0.8)
    pdf.line(12, pdf.get_y(), 198, pdf.get_y())
    pdf.ln(4)

def body(t):
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(30,30,30)
    pdf.multi_cell(0, 6.5, t, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)

def bullet(b):
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(30,30,30)
    pdf.multi_cell(0, 6.5, "- " + b, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

pdf.add_page()
title("1. What is this project? In 30 seconds")
body("Phone companies lose money when customers leave. This is called churn. We built fake but real-like data for 5000 Egypt telecom customers, then we answer 3 questions: Who leaves? Why? Who will leave next?")
bullet("Data: 7 tables. Think like Excel sheets linked by customer_id.")
bullet("Dashboard: Power BI shows churn with charts and filters.")
bullet("Future: a smart model gives each customer a risk score 0-100%.")

title("2. The 7 tables - super simple")
body("customers: who they are (age, city, contract). subscriptions: what plan they buy (Basic/Plus/Ultra/Business, Fiber/DSL/5G, price, months). usage_monthly: what they use each month (calls, GB, downtime). billing: do they pay late? support_tickets: do they complain? network_quality: is signal bad in their region? churn_labels: did they leave + why.")
body("Link: customer_id is the key. One customer has 12 usage rows + 12 billing rows + 0-5 tickets. This is called star schema. It makes Power BI fast.")

title("3. Power BI dashboard - 5 pages")
body("Page 1 Overview: big numbers (KPIs) + churn trend. Page 2 Customer: churn by plan/contract/payment. Page 3 Usage+Network: outages vs churn, map by region. Page 4 Billing+Support: late pay + satisfaction. Page 5 Prediction: high-risk list + money at risk.")
body("DAX is just Excel formulas for Power BI. Example: Churn Rate = Churned / Total * 100. All formulas are in powerbi/DAX_measures.dax. Copy-paste them.")
body("Steps: Load 7 CSVs, fix types with PowerQuery_M.m, make links, paste DAX, drag charts. 10 minutes. See powerbi/data_model_and_dashboard.md.")

pdf.add_page()
title("4. The ML model - like a smart friend")
body("We teach the computer with old data: these customers left, these stayed. The computer finds patterns. Then for a new customer it says: 82% risk, take care!")
body("Model: RandomForest, 200 trees. Each tree votes leave/stay. Simple and strong. No deep learning needed.")
bullet(f"Score: accuracy {m['accuracy']*100:.1f}% (71 of 100 correct), AUC {m['roc_auc']} (0.5 = random, 1.0 = perfect).")
bullet("Top drivers: bill amount, monthly charge, usage, tenure, downtime, late days, tickets, satisfaction.")
bullet("Use it: py ml/predict.py. You get churn_probability + Low/Medium/High.")

title("5. Results - what we learned")
body(f"Churn rate {s['churn_rate']*100:.1f}% (2143 of 5000). Month-to-month churns 2x more than 2-year. Fiber has more tickets. Electronic check + paperless = more churn. Low satisfaction (1-2 stars) churns a lot. New customers (tenure under 6 months) are most risky.")
body("Money tip: call High-risk customers first, give discount or fix network, move them to 1-year contract. This saves lifetime money (CLV).")

title("6. How to run + files")
body("Windows: double-click run.bat. Or: pip install -r requirements.txt, py make_dataset.py, py build_analysis_ml.py, py ml/predict.py. Preview: dashboard_preview/index.html. Charts: analysis/charts (13 images).")
body("Folders: data = CSVs, powerbi = DAX+M+plan, ml = model.pkl+metrics+predict, analysis = charts, docs = this PDF + references.")

title("7. References (where to learn more)")
for r in [
 "Microsoft Power BI dashboards - learn.microsoft.com/power-bi/create-reports/",
 "DAX overview - learn.microsoft.com/dax/dax-overview",
 "Power Query M - learn.microsoft.com/powerquery-m/",
 "Star schema - learn.microsoft.com/power-bi/guidance/star-schema",
 "pandas docs - pandas.pydata.org/docs/",
 "scikit-learn RandomForest - scikit-learn.org/stable/",
 "IBM Telco Churn classic dataset - inspiration for columns",
 "Google Scholar: customer churn prediction telecom review",
]:
    bullet(r)
body("I used first 4 for dashboard, next 2 for code, last 2 for churn idea. Data here is my own fake Egypt data, bigger: 7 tables, 133k rows.")

pdf.output("docs/Telecom_Churn_Simple_Guide.pdf")
print("PDF saved")
