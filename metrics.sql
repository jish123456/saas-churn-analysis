-- SaaS-style metrics on the IBM Telco Customer Churn dataset (public telecom data, not a SaaS company).
-- Table: customers (cleaned, Churn is 1/0, the 11 tenure=0 rows are dropped, see notebook).
-- "Active" = Churn = 0. MonthlyCharges is treated as monthly recurring revenue per customer.

-- Q1 Overall churn rate: share of customers who left (Churn = 1) out of all customers.
SELECT ROUND(AVG(Churn) * 100, 2) AS churn_rate_pct
FROM customers;

-- Q2a Churn rate by Contract: the same churn share within each contract type.
SELECT Contract, COUNT(*) AS customers, ROUND(AVG(Churn) * 100, 2) AS churn_rate_pct
FROM customers GROUP BY Contract ORDER BY churn_rate_pct DESC;

-- Q2b Churn rate by InternetService.
SELECT InternetService, COUNT(*) AS customers, ROUND(AVG(Churn) * 100, 2) AS churn_rate_pct
FROM customers GROUP BY InternetService ORDER BY churn_rate_pct DESC;

-- Q2c Churn rate by PaymentMethod.
SELECT PaymentMethod, COUNT(*) AS customers, ROUND(AVG(Churn) * 100, 2) AS churn_rate_pct
FROM customers GROUP BY PaymentMethod ORDER BY churn_rate_pct DESC;

-- Q3 MRR: monthly recurring revenue = sum of MonthlyCharges over active customers.
-- ARR: annual recurring revenue = MRR x 12.
SELECT ROUND(SUM(MonthlyCharges), 2) AS mrr,
       ROUND(SUM(MonthlyCharges) * 12, 2) AS arr
FROM customers WHERE Churn = 0;

-- Q4 ARPU: average revenue per user = MRR / number of active customers.
SELECT ROUND(SUM(MonthlyCharges) * 1.0 / COUNT(*), 2) AS arpu
FROM customers WHERE Churn = 0;

-- Q5 Revenue lost to churn: monthly revenue of customers who churned.
SELECT ROUND(SUM(MonthlyCharges), 2) AS monthly_revenue_lost,
       COUNT(*) AS churned_customers
FROM customers WHERE Churn = 1;

-- Q6 LTV: lifetime value = ARPU / monthly churn rate.
-- ASSUMPTION: the data is a snapshot, so monthly churn is approximated as
-- (overall churn rate) / (average tenure in months). This is a rough estimate, not an observed monthly rate.
WITH a AS (
  SELECT SUM(MonthlyCharges) * 1.0 / COUNT(*) AS arpu FROM customers WHERE Churn = 0
), c AS (
  SELECT AVG(Churn) AS churn_rate, AVG(tenure) AS avg_tenure FROM customers
)
SELECT ROUND(a.arpu, 2) AS arpu,
       ROUND(c.churn_rate, 4) AS overall_churn,
       ROUND(c.avg_tenure, 2) AS avg_tenure_months,
       ROUND(c.churn_rate / c.avg_tenure, 5) AS monthly_churn_approx,
       ROUND(a.arpu / (c.churn_rate / c.avg_tenure), 2) AS ltv
FROM a, c;
