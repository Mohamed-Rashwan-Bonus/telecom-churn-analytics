// Power Query M - load and clean all 7 CSVs
// In Power BI: Get Data > Text/CSV > pick files from /data > open Advanced Editor and paste each block

// --- customers ---
let
    Source = Csv.Document(File.Contents("data/customers.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promote = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Promote, {{"customer_id", type text}, {"gender", type text}, {"age", Int64.Type}, {"city", type text}, {"region", type text}, {"join_date", type date}, {"contract_type", type text}, {"payment_method", type text}, {"senior_citizen", type text}, {"partner", type text}, {"dependents", type text}, {"paperless_billing", type text}})
in Types

// --- subscriptions ---
// same pattern, set monthly_charge_egp + total_charge_egp to Currency, tenure_months to Int64

// --- usage_monthly ---
// month column: Text "YYYY-MM" -> add custom column MonthDate = Date.FromText([month] & "-01")

// --- billing ---
// add custom column: Unpaid = [amount_due_egp] - [amount_paid_egp]
// add conditional column: IsLate = if [late_days] > 0 then "Late" else "On time"

// --- support_tickets ---
// open_date + close_date to Date, satisfaction_score to Int64

// --- churn_labels ---
// churned to 0/1 Int64, churn_date to Date, churn_probability_raw to Decimal

// Relationships to create in Model view (star schema):
// customers[customer_id] 1--* subscriptions[customer_id]
// customers[customer_id] 1--* usage_monthly[customer_id]
// customers[customer_id] 1--* billing[customer_id]
// customers[customer_id] 1--* support_tickets[customer_id]
// customers[customer_id] 1--1 churn_labels[customer_id]
// customers[region] *--* network_quality[region] + month bridge via Calendar table
// Create Calendar table: Calendar = CALENDAR(DATE(2020,1,1), DATE(2024,12,31))
