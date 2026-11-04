"""Generates analysis.ipynb (run once: python make_notebook.py)."""
import json

def md(s): return {"cell_type": "markdown", "metadata": {}, "source": s.strip().splitlines(True)}
def code(s): return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": s.strip().splitlines(True)}

cells = [
md("# Churn analysis: IBM Telco dataset\nPublic telecom data, not a SaaS company. Retention curves are by **tenure**, not calendar cohorts."),
md("## 1. Load"),
code("""import sqlite3, pandas as pd, matplotlib.pyplot as plt
from churn_lib import CSV_PATH, DB_PATH, clean, load_customers, km_by_contract, fit_model
raw = pd.read_csv(CSV_PATH)
raw.shape"""),
md("## 2. Clean\n**Decision (edit if you disagree):** `TotalCharges` is blank for 11 customers, all with `tenure = 0` (new, never billed). I drop them: no history, and a zero duration cannot be used in Kaplan-Meier."),
code("""blank = pd.to_numeric(raw["TotalCharges"], errors="coerce").isna()
print(blank.sum(), "blank TotalCharges; tenure values:", raw.loc[blank, "tenure"].unique())
df = clean(raw)
with sqlite3.connect(DB_PATH) as conn:
    df.to_sql("customers", conn, if_exists="replace", index=False)
print(df.shape, "churn rate:", round(df.Churn.mean(), 4))"""),
md("## 3. Metrics\nRun the queries in `metrics.sql` (one at a time in a SQLite client, or below)."),
code("""conn = sqlite3.connect(DB_PATH)
for q in open("metrics.sql").read().split(";"):
    if "SELECT" in q.upper():
        print(q.strip().splitlines()[0]); display(pd.read_sql(q, conn))"""),
md("## 4. Retention curves (Kaplan-Meier)"),
code("""df = load_customers()
fits, table = km_by_contract(df)
fig, ax = plt.subplots()
for k in fits.values(): k.plot_survival_function(ax=ax)
ax.set_xlabel("Tenure (months)"); ax.set_ylabel("Share retained")
plt.savefig("screenshots/retention_curves.png", dpi=150, bbox_inches="tight")
table.style.format("{:.1%}")"""),
md("## 5. Churn driver model\n`TotalCharges` excluded (≈ tenure × MonthlyCharges). ~27% churn, so accuracy alone misleads: compare recall and AUC against the always-'no churn' baseline. Coefficients are *associated with* churn, not causes."),
code("""model, metrics, odds = fit_model(df)
display(metrics.round(3)); display(odds.head(10)); display(odds.tail(10))"""),
md("## 6. Notes for the write-up\n- LTV assumes monthly churn ≈ overall churn ÷ average tenure.\n- Numbers to copy into the memo: ..."),
]
nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}, "nbformat": 4, "nbformat_minor": 5}
json.dump(nb, open("analysis.ipynb", "w"), indent=1)
