"""Build interactive HTML dashboard (no static images). Run: py make_interactive.py"""
import pandas as pd, json
c = pd.read_csv("data/customers.csv")
s = pd.read_csv("data/subscriptions.csv")
ch = pd.read_csv("data/churn_labels.csv")
df = c.merge(s, on="customer_id").merge(ch, on="customer_id")
# small sample for table (top 200 high risk) to keep HTML light
top = df.sort_values("churn_probability_raw", ascending=False).head(200)
records = top[["customer_id","region","city","plan_name","contract_type","internet_service","monthly_charge_egp","tenure_months","churned","churn_probability_raw","churn_reason"]].to_dict(orient="records")
# agg for filters
with open("dashboard_preview/data.json","w") as f:
    json.dump(records, f)

html = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Telecom Churn - Interactive</title>
<style>body{font-family:Segoe UI,Arial;margin:0;background:#0f172a;color:#e2e8f0}header{background:#f8fafc;color:#0f172a;padding:16px 22px}select{background:#1e293b;color:#fff;padding:8px;border-radius:8px;margin:4px}.wrap{max-width:1200px;margin:auto;padding:18px}.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}.kpi{background:#1e293b;padding:14px;border-radius:12px;border-left:5px solid #facc15}.kpi b{font-size:24px;display:block}table{width:100%;border-collapse:collapse;background:#fff;color:#111;border-radius:10px;overflow:hidden}th,td{padding:8px;border-bottom:1px solid #ddd;font-size:13px;text-align:left}th{background:#facc15}.bar{height:10px;background:#334155;border-radius:6px;overflow:hidden}.bar i{display:block;height:100%;background:#ef4444}</style></head>
<body><header><h2 style="margin:0">Telecom Churn - Interactive Dashboard</h2><small>Filter and the KPIs + table update live. Full Power BI version: see /powerbi/ folder. By Mohamed Rashwan</small></header>
<div class="wrap">
<div>
<label>Region:</label><select id="fRegion"><option value="">All</option></select>
<label>Plan:</label><select id="fPlan"><option value="">All</option></select>
<label>Contract:</label><select id="fContract"><option value="">All</option></select>
<label>Internet:</label><select id="fNet"><option value="">All</option></select>
<button onclick="resetF()" style="padding:8px 14px;border-radius:8px;border:0;background:#facc15;font-weight:bold;cursor:pointer">Reset</button>
</div>
<div class="kpis" style="margin-top:12px">
<div class="kpi"><small>Filtered customers</small><b id="kN">-</b></div>
<div class="kpi" style="border-color:#ef4444"><small>Churn rate</small><b id="kChurn">-</b></div>
<div class="kpi" style="border-color:#38bdf8"><small>Avg monthly EGP</small><b id="kBill">-</b></div>
<div class="kpi" style="border-color:#22c55e"><small>Avg tenure</small><b id="kTen">-</b></div>
<div class="kpi"><small>High risk (&gt;60%)</small><b id="kHigh">-</b></div>
</div>
<h3>Top risky customers (live filter)</h3>
<table><thead><tr><th>ID</th><th>Region</th><th>Plan</th><th>Contract</th><th>Bill</th><th>Tenure</th><th>Risk</th><th>Status</th></tr></thead><tbody id="tb"></tbody></table>
<p style="opacity:.7">This page reads <code>data.json</code> (200 highest-risk sample). For full 5000 + 5 pages + maps, build Power BI in 10 min - guide in <code>powerbi/data_model_and_dashboard.md</code>.</p>
</div>
<script>
let DATA=[];
fetch('data.json').then(r=>r.json()).then(j=>{DATA=j; init();});
function uniq(k){return [...new Set(DATA.map(d=>d[k]))].sort();}
function init(){
  fill('fRegion',uniq('region')); fill('fPlan',uniq('plan_name')); fill('fContract',uniq('contract_type')); fill('fNet',uniq('internet_service'));
  ['fRegion','fPlan','fContract','fNet'].forEach(id=>document.getElementById(id).onchange=render);
  render();
}
function fill(id,vals){const el=document.getElementById(id); vals.forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v;el.appendChild(o);});}
function resetF(){['fRegion','fPlan','fContract','fNet'].forEach(id=>document.getElementById(id).value='');render();}
function render(){
  const r=document.getElementById('fRegion').value, p=document.getElementById('fPlan').value, co=document.getElementById('fContract').value, n=document.getElementById('fNet').value;
  const f=DATA.filter(d=>(!r||d.region===r)&&(!p||d.plan_name===p)&&(!co||d.contract_type===co)&&(!n||d.internet_service===n));
  const base=f.length?f:DATA;
  const churn=base.filter(d=>d.churned===1).length/base.length*100;
  const bill=base.reduce((a,d)=>a+d.monthly_charge_egp,0)/base.length;
  const ten=base.reduce((a,d)=>a+d.tenure_months,0)/base.length;
  const high=base.filter(d=>d.churn_probability_raw>0.6).length;
  document.getElementById('kN').textContent=base.length;
  document.getElementById('kChurn').textContent=churn.toFixed(1)+'%';
  document.getElementById('kBill').textContent=Math.round(bill)+' EGP';
  document.getElementById('kTen').textContent=ten.toFixed(1)+' mo';
  document.getElementById('kHigh').textContent=high;
  const tb=document.getElementById('tb'); tb.innerHTML='';
  base.slice(0,50).forEach(d=>{
    const tr=document.createElement('tr');
    const pct=Math.round(d.churn_probability_raw*100);
    tr.innerHTML=`<td>${d.customer_id}</td><td>${d.region}</td><td>${d.plan_name}</td><td>${d.contract_type}</td><td>${d.monthly_charge_egp}</td><td>${d.tenure_months}</td><td><div class="bar"><i style="width:${pct}%"></i></div>${pct}%</td><td>${d.churned?'Churned':'Stayed'}</td>`;
    tb.appendChild(tr);
  });
}
</script></body></html>"""
with open("dashboard_preview/interactive.html","w", encoding="utf-8") as f:
    f.write(html)
print("interactive saved")
