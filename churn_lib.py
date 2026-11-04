"""Shared helpers for the notebook and the Streamlit app."""
import sqlite3
import numpy as np
import pandas as pd
from lifelines import KaplanMeierFitter
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

DB_PATH = "churn.db"
CSV_PATH = "data/WA_Fn-UseC_-Telco-Customer-Churn.csv"


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Decision: drop the 11 rows with tenure = 0 (blank TotalCharges). They are brand-new
    customers with no billing history and a zero duration, which Kaplan-Meier cannot use."""
    df = df.copy()
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df = df[df["tenure"] > 0].copy()
    df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0})
    return df.reset_index(drop=True)


def load_customers(db_path: str = DB_PATH) -> pd.DataFrame:
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql("SELECT * FROM customers", conn)


def km_by_contract(df: pd.DataFrame, months=(6, 12, 24)):
    """Return {contract: fitted KM} and a retention table at the given months."""
    fits, rows = {}, []
    for contract, g in df.groupby("Contract"):
        kmf = KaplanMeierFitter().fit(g["tenure"], g["Churn"], label=contract)
        fits[contract] = kmf
        rows.append({"Contract": contract,
                     **{f"{m} mo": float(kmf.predict(m)) for m in months}})
    return fits, pd.DataFrame(rows).set_index("Contract")


def fit_model(df: pd.DataFrame, seed: int = 42):
    """Logistic regression, 80/20 stratified split.
    TotalCharges is excluded on purpose: it is ~ tenure x MonthlyCharges (redundant / leakage-prone).
    class_weight='balanced' because only ~27% churn. Numeric features are standardised, so their
    odds ratios are per 1 standard deviation."""
    X = df.drop(columns=["customerID", "Churn", "TotalCharges"], errors="ignore")
    y = df["Churn"]
    X = pd.get_dummies(X, drop_first=True).astype(float)
    num = [c for c in ["tenure", "MonthlyCharges"] if c in X.columns]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=seed, stratify=y)
    scaler = StandardScaler().fit(Xtr[num])
    Xtr, Xte = Xtr.copy(), Xte.copy()
    Xtr[num] = scaler.transform(Xtr[num])
    Xte[num] = scaler.transform(Xte[num])
    model = LogisticRegression(max_iter=2000, class_weight="balanced").fit(Xtr, ytr)
    pred, proba = model.predict(Xte), model.predict_proba(Xte)[:, 1]
    base = np.zeros(len(yte), dtype=int)
    metrics = pd.DataFrame({
        "Always 'no churn'": [accuracy_score(yte, base), recall_score(yte, base), 0.5],
        "Logistic regression": [accuracy_score(yte, pred), recall_score(yte, pred),
                                roc_auc_score(yte, proba)],
    }, index=["Accuracy", "Recall", "AUC"])
    odds = pd.DataFrame({"feature": X.columns, "odds_ratio": np.exp(model.coef_[0])})
    odds = odds.sort_values("odds_ratio", ascending=False).reset_index(drop=True)
    return model, metrics, odds
