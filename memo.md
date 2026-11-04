# Churn memo

**Data:** public IBM Telco Customer Churn dataset (7,032 customers after dropping 11 with zero tenure). This is telecom data, not a SaaS company. The metrics are defined the same way, but findings may not transfer. Retention is by tenure, not calendar cohort.

**Headline:** 26.6% of customers churned, taking $139K of monthly charges with them, about 31% of all monthly charges in the data. Contract type, internet service and payment method separate high-churn from low-churn customers most clearly.

## 1. Contract type
**Finding:** Month-to-month customers churn at 42.7%, about 15x the two-year rate (2.9%) and 3.8x the one-year rate (11.3%).
**Evidence:** Kaplan-Meier retention at 12 months is 70.3% for month-to-month vs 99.1% for one-year. At 24 months it is 58.6% vs 97.8%. Month-to-month customers are 3,875 of 7,032 customers. In the model, a two-year contract has an odds ratio of 0.24 and a one-year contract 0.46 vs month-to-month.
**Recommendation:** Offer month-to-month customers an incentive to move to an annual plan, and test it with a small group first. Caveat: annual customers may differ from month-to-month ones in ways the data doesn't show, so the gap won't all be recovered. Two-year retention reads 100% partly because contracts lock customers in.

## 2. Fiber optic and electronic check
**Finding:** Fiber optic customers churn at 41.9% (DSL 19.0%, no internet 7.4%). Electronic-check payers churn at 45.3%, versus 15-19% for the other payment methods.
**Evidence:** Fiber optic has the largest odds ratio in the model (3.2), and electronic check is 1.5, both holding other features fixed. These are associations, not causes: price, service quality and customer type all overlap here.
**Recommendation:** Investigate fiber optic service quality and pricing, and prompt electronic-check payers to switch to automatic payment. Both are hypotheses to test, not proven fixes.

## 3. Revenue at stake
**Finding:** Churned customers represent $139,131/month in charges, against $316,530 MRR ($3.80M ARR) from active customers. ARPU is $61.31.
**Evidence:** metrics.sql Q3-Q5. Approximate LTV is $7,479, assuming monthly churn is overall churn divided by average tenure (0.82%/month). This is a rough estimate, since the data is a snapshot, so treat it as an order of magnitude.
**Recommendation:** Because the revenue at stake is large relative to MRR, even a modest reduction in month-to-month churn is worth testing.

## Model check
Logistic regression (80/20 split, balanced class weights) on the test set: recall 0.78, AUC 0.83, accuracy 0.73. An always-"no churn" baseline gets 0.73 accuracy, 0 recall and 0.50 AUC. Accuracy alone is misleading with 27% churn, which is why recall and AUC are reported. `TotalCharges` was excluded because it is roughly tenure x MonthlyCharges. Coefficients show associations only.
