import numpy as np
import pandas as pd
import pickle
import json
import shap
shap.initjs()
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import precision_recall_curve


df = pd.read_csv(Path(__file__).parent / "sample_data.csv")
print(df.head())

df["transaction_time"] = pd.to_datetime(df["transaction_time"])
df["transaction_hour"] = df["transaction_time"].dt.hour
df["transaction_dayofweek"] = df["transaction_time"].dt.dayofweek


drop_cols = ["transaction_id", "customer_id", "transaction_time", "merchant_id"]
data = df.drop(columns=drop_cols)
X = data.drop(columns=["is_fraud"])
y = data["is_fraud"]

X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.4, stratify=y, random_state=42
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42
)

# Captured before encoding overwrites X_train in place — Unity Catalog
# requires a real input_example (not just type hints) to infer a model
# signature, and it needs to be raw/unencoded since predict() encodes it itself.
input_example = X_train.head(5).copy()

encoders = {}
for col in X_train.select_dtypes(include="object").columns:
    le = LabelEncoder()
    X_train[col] = le.fit_transform(X_train[col].astype(str))
    X_val[col] = le.transform(X_val[col].astype(str))
    X_test[col] = le.transform(X_test[col].astype(str))
    encoders[col] = le


scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

best_score = -1
best_model = None
best_depth = None
for depth in [3, 4, 5, 6, 7, 8]:
    candidate = XGBClassifier(
        n_estimators=300,
        max_depth=depth,
        learning_rate=0.1,
        scale_pos_weight=scale_pos_weight,
        eval_metric="aucpr",
        early_stopping_rounds=20,
        random_state=42,
    )
    candidate.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )
    val_score = average_precision_score(y_val, candidate.predict_proba(X_val)[:, 1])
    print(f"max_depth={depth}: val AUC-PR={val_score:.4f}, best_iteration={candidate.best_iteration}")
    if val_score > best_score:
        best_score, best_model, best_depth = val_score, candidate, depth

print(f"\nBest max_depth: {best_depth} (val AUC-PR={best_score:.4f})")
model = best_model


y_pred_proba = model.predict_proba(X_test)[:, 1]
y_pred = model.predict(X_test)  

print(f"\nTest AUC-PR: {average_precision_score(y_test, y_pred_proba):.4f}")
print(f"Test ROC-AUC: {roc_auc_score(y_test, y_pred_proba):.4f}")
print("\nConfusion matrix (rows=actual, cols=predicted):")
print(confusion_matrix(y_test, y_pred))
print("\nClassification report:")
print(classification_report(y_test, y_pred, target_names=["not_fraud", "fraud"]))

precisions, recalls, thresholds = precision_recall_curve(y_test, y_pred_proba)


def best_threshold_by_fbeta(precisions, recalls, thresholds, beta):
    beta_sq = beta ** 2
    scores = (1 + beta_sq) * (precisions * recalls) / (beta_sq * precisions + recalls + 1e-12)
    idx = np.argmax(scores[:-1])  # last point has no threshold behind it
    return thresholds[idx], precisions[idx], recalls[idx], scores[idx]

f1_threshold, f1_p, f1_r, f1_val = best_threshold_by_fbeta(precisions, recalls, thresholds, beta=1)
f2_threshold, f2_p, f2_r, f2_val = best_threshold_by_fbeta(precisions, recalls, thresholds, beta=2)

print("\nThreshold sweep:")
print(f"{'threshold':>10} {'precision':>10} {'recall':>10} {'f1':>8}")
for t in np.arange(0.1, 0.95, 0.05):
    preds = (y_pred_proba >= t).astype(int)
    p = precision_score(y_test, preds, zero_division=0)
    r = recall_score(y_test, preds, zero_division=0)
    f = f1_score(y_test, preds, zero_division=0)
    print(f"{t:>10.2f} {p:>10.3f} {r:>10.3f} {f:>8.3f}")

print(f"\nF1-optimal threshold:  {f1_threshold:.3f} (precision={f1_p:.3f}, recall={f1_r:.3f}, f1={f1_val:.3f})")
print(f"F2-optimal threshold:  {f2_threshold:.3f} (precision={f2_p:.3f}, recall={f2_r:.3f}, f2={f2_val:.3f})")

chosen_threshold = f2_threshold
y_pred_final = (y_pred_proba >= chosen_threshold).astype(int)

print(f"\nUsing F2-optimal threshold ({chosen_threshold:.3f}) as the final model:")
print("\nConfusion matrix:")
print(confusion_matrix(y_test, y_pred_final))
print("\nClassification report:")
print(classification_report(y_test, y_pred_final, target_names=["not_fraud", "fraud"]))

shap_sample = X_test.sample(n=min(2000, len(X_test)), random_state=42)
explainer = shap.TreeExplainer(model)
shap_values = explainer(shap_sample)

shap.summary_plot(shap_values, shap_sample, show=False)
plt.tight_layout()
plt.savefig(Path(__file__).parent / "shap_summary.png")
plt.close()
print("\nSaved SHAP summary plot to shap_summary.png")


fraud_idx = np.where(model.predict(shap_sample) == 1)[0]
if len(fraud_idx) > 0:
    shap.plots.waterfall(shap_values[fraud_idx[0]], show=False)
    plt.tight_layout()
    plt.savefig(Path(__file__).parent / "shap_waterfall_example.png")
    plt.close()
    print("Saved SHAP waterfall plot to shap_waterfall_example.png")
else:
    print("No fraud predictions in the sample — try a larger sample size.")

with open(Path(__file__).parent / "threshold.json", "w") as f:
    json.dump({"threshold": float(chosen_threshold)}, f)
input_example.to_csv(Path(__file__).parent / "input_example.csv", index=False)
with open(Path(__file__).parent / "fraud_model.pkl", "wb") as f:
    pickle.dump(model, f)
with open(Path(__file__).parent / "encoders.pkl", "wb") as f:
    pickle.dump(encoders, f)
