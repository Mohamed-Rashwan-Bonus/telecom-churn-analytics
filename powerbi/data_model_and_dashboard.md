# Power BI Data Model + Dashboard Plan

## Star schema
- **Fact tables:** usage_monthly (60k), billing (60k), support_tickets (8.5k)
- **Dimensions:** customers (5k), subscriptions (5k), network_quality (60), Calendar
- **Label table:** churn_labels (5k, 1-1 with customers)

```
customers ||--o{ subscriptions : has
customers ||--o{ usage_monthly : uses
customers ||--o{ billing : pays
customers ||--o{ support_tickets : opens
customers ||--|| churn_labels : churns
network_quality }o--|| customers : region
Calendar ||--o{ usage_monthly : month
Calendar ||--o{ billing : month
```

## Power BI pages (5 pages)

### P1 - Executive Overview
- KPI cards: Total Customers (5k), Churn Rate % (~42.9%), Total Revenue EGP, Avg Satisfaction
- Line: churn trend by churn_date month
- Bar: churn by reason
- Donut: contract mix
- Slicers: region, plan, contract

### P2 - Customer & Plan
- Bar: churn by plan, internet, payment method
- Histogram: monthly_charge + tenure split by churned
- Table: top 100 high-risk customers (churn_probability_raw > 0.6)

### P3 - Usage & Network
- Line: avg outage_hours per month
- Map: churn by region/city (use Azure map visual)
- Scatter: downtime_hours vs churn_probability_raw
- Bar: slow_days avg by internet_service

### P4 - Billing & Support
- KPI: Late Payment %, Resolution %, Total Tickets
- Bar: churn by satisfaction_score
- Stacked bar: tickets by category + priority
- Table: unpaid amount per customer

### P5 - Prediction (ML)
- Import predictions: run `py ml/predict.py --input data/new_customers.csv --output data/predictions.csv`, then load predictions.csv
- Gauge: High Risk Customers count
- Table: customer_id + churn probability + suggested action
- Card: Revenue at Risk (DAX)

## Build steps (10 min)
1. Open Power BI Desktop > Get Data > load 7 CSVs from /data
2. Paste M code from PowerQuery_M.m for types + custom columns
3. Model view > create relationships above + Calendar table
4. Paste all measures from DAX_measures.dax
5. Build the 5 pages above (screenshots in /analysis/charts as reference)
6. Publish to Power BI Service + set scheduled refresh
