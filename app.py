import sqlite3
import matplotlib.pyplot as plt
import streamlit as st
from churn_lib import DB_PATH, load_customers, km_by_contract, fit_model

st.set_page_config(page_title="Churn analysis (Telco data)", layout="wide")
st.title("Customer churn analysis")
st.caption("Public IBM Telco dataset, not a SaaS company. Retention is by tenure, not calendar cohorts.")


@st.cache_data
def get_data():
    return load_customers(DB_PATH)


df = get_data()
active, churned = df[df.Churn == 0], df[df.Churn == 1]

# --- KPIs (same definitions as metrics.sql) ---
mrr = active.MonthlyCharges.sum()
arpu = mrr / len(active)
churn = df.Churn.mean()
monthly_churn = churn / df.tenure.mean()  # assumption: overall churn / average tenure
ltv = arpu / monthly_churn
c1, c2, c3, c4 = st.columns(4)
c1.metric("MRR", f"${mrr:,.0f}")
c2.metric("ARR", f"${mrr * 12:,.0f}")
c3.metric("Churn rate", f"{churn:.1%}")
c4.metric("LTV (approx.)", f"${ltv:,.0f}", help="ARPU / (overall churn / avg tenure)")
st.caption(f"Revenue lost to churn: \\${churned.MonthlyCharges.sum():,.0f}/month. ARPU: \\${arpu:,.2f}.")

left, right = st.columns(2)
with left:
    st.subheader("Churn by contract")
    by_contract = df.groupby("Contract").Churn.mean().mul(100).sort_values()
    st.bar_chart(by_contract, y_label="Churn rate (%)")

with right:
    st.subheader("Retention curves by contract")
    fits, table = km_by_contract(df)
    fig, ax = plt.subplots()
    for kmf in fits.values():
        kmf.plot_survival_function(ax=ax, ci_show=False)
    ax.set_xlabel("Tenure (months)")
    ax.set_ylabel("Share retained")
    st.pyplot(fig)
    st.dataframe(table.style.format("{:.1%}"))

st.subheader("Top churn drivers (odds ratios)")
_, metrics, odds = fit_model(df)
st.caption("Associated with churn, not causal. Numeric features are per 1 SD; others vs. the baseline category.")
a, b = st.columns(2)
a.write("Higher odds of churn")
a.dataframe(odds.head(8), hide_index=True)
b.write("Lower odds of churn")
b.dataframe(odds.tail(8).iloc[::-1], hide_index=True)
st.write("Test-set performance")
st.dataframe(metrics.style.format("{:.3f}"))
