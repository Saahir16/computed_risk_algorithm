"""
This file runs separate checks on the experiment code using Python loops to catch bugs.
Command: python double_check.py
"""

import numpy as np
import pandas as pd
from detectors import risk_weights, trust_weights, build_detectors, metrics
from dataset import generate

all_passed = True

def check(name, condition, detail=""):
    global all_passed
    if not condition:
        all_passed = False
    if condition:
        print("Pass " + name + " " + detail)
    else:
        print("Fail " + name + " " + detail)

# checking that the same seed should give the same data
data = generate(42, 1000)
data_again = generate(42, 1000)
check("same seed gives identical dataset", data.equals(data_again))
check("different seed gives different dataset", not data.equals(generate(43, 1000)))

# do weights add up to 1
check("risk weights sum to 1", abs(sum(risk_weights.values()) - 1) < 1e-12)
check("trust weights sum to 1", abs(sum(trust_weights.values()) - 1) < 1e-12)

# are all the columns in the range of 0 to 100
feature_columns = list(risk_weights) + list(trust_weights)
check("all 10 feature columns within 0 to 100", data[feature_columns].min().min() >= 0 and data[feature_columns].max().max() <= 100)

# calculating the scores for the first row
row = data.iloc[0]
risk_by_hand = (0.30 * row["historical_deviation"] + 0.25 * row["revenue_cost_ratio_change"] + 0.20 * row["budget_variance"] + 0.15 * row["vendor_frequency_shift"] + 0.10 * row["peer_department_deviation"])
trust_by_hand = (0.30 * row["vendor_history"] + 0.25 * row["approval_chain"] + 0.20 * row["timing_consistency"] + 0.15 * row["bank_stability"] + 0.10 * row["cross_ledger"])
scored = pd.read_csv("data/transactions_seed42_scored.csv")
check("row 0 risk score matches hand calculation",
      abs(risk_by_hand - scored.loc[0, "risk_score"]) < 0.01, f"{risk_by_hand:.2f}")
check("row 0 trust score matches hand calculation",
      abs(trust_by_hand - scored.loc[0, "trust_score"]) < 0.01, f"{trust_by_hand:.2f}")

# redoing the detectors with loops to compare to detectors.py
detectors = build_detectors(data)
loop_flags = {"single_rule": [], "multiple_rules": [], "contextual_main": [], "contextual_looser": []}
for index, transaction in data.iterrows():
    risk = 0
    for signal in risk_weights:
        risk = risk + risk_weights[signal] * transaction[signal]
    trust = 0
    for signal in trust_weights:
        trust = trust + trust_weights[signal] * transaction[signal]

    loop_flags["single_rule"].append(transaction["amount"] > 10_000)
    loop_flags["multiple_rules"].append(
        transaction["amount"] > 10_000 or transaction["days_since_bank_change"] < 30 or transaction["signed_approvals"] < transaction["required_approvals"] or transaction["ledger_mismatch_pct"] > 10)
    loop_flags["contextual_main"].append(risk >= 61 or trust < 60)
    loop_flags["contextual_looser"].append(risk >= 31 or trust < 85)

for name, flags in loop_flags.items():
    flags = np.array(flags)
    check(name + ": loop flags equal detectors.py flags", (flags == detectors[name].to_numpy()).all())

    # confusion matrix
    true_positives = 0
    false_positives = 0
    false_negatives = 0
    true_negatives = 0
    for actual, flagged in zip(data["anomaly"], flags):
        if actual and flagged:
            true_positives = true_positives + 1
        elif not actual and flagged:
            false_positives = false_positives + 1
        elif actual and not flagged:
            false_negatives = false_negatives + 1
        else:
            true_negatives = true_negatives + 1

    result = metrics(data["anomaly"], flags)
    same_counts = (true_positives, false_positives, false_negatives, true_negatives) == (result["true_positives"], result["false_positives"], result["false_negatives"], result["true_negatives"])
    check(name + ": confusion counts match", same_counts, f"TP={true_positives} FP={false_positives} FN={false_negatives} TN={true_negatives}")
    check(name + ": detection rate + false negative rate = 1", abs(result["detection_rate"] + result["false_negative_rate"] - 1) < 1e-12)

# saved csv should have the same alerts
for name in ["single_rule", "multiple_rules", "contextual_main", "contextual_looser"]:
    check("saved csv alert_" + name + " agrees", (scored["alert_" + name].to_numpy() == detectors[name].to_numpy().astype(int)).all())

# summary table should match the per run file
runs = pd.read_csv("results/per_run_metrics.csv")
check("30 runs x 7 detectors in per run file", len(runs) == 30 * 7 and runs["seed"].nunique() == 30)
main_detection_rate = runs[runs["detector"] == "contextual_main"]["detection_rate"].mean()
summary = pd.read_csv("results/summary.csv")
main_row = summary[summary["detector"] == "Contextual: Risk>=61 OR Trust<60"]
check("summary detection rate for contextual_main matches per run mean", f"{main_detection_rate:.3f}" in main_row["detection_rate"].iloc[0], f"{main_detection_rate:.3f}")

# contextual_looser should be catching 100% of things
looser_runs = runs[runs["detector"] == "contextual_looser"]
check("contextual_looser detects every anomaly in every run", (looser_runs["false_negatives"] == 0).all(), f"max false negatives across runs = {int(looser_runs['false_negatives'].max())}")

risk_scores = 0
for signal in risk_weights:
    risk_scores = risk_scores + data[signal] * risk_weights[signal]
trust_scores = 0
for signal in trust_weights:
    trust_scores = trust_scores + data[signal] * trust_weights[signal]

anomaly_rows = data["anomaly"] == 1
print("anomalies: lowest risk %.1f, highest trust %.1f (looser thresholds: risk>=31 or trust<85)"
      % (risk_scores[anomaly_rows].min(), trust_scores[anomaly_rows].max()))
flagged_normal = (risk_scores >= 31) | (trust_scores < 85)
print("normal transactions flagged by looser thresholds = %.1f%%" % (100 * flagged_normal[~anomaly_rows].mean()))

if all_passed:
    print("\nAll checks have passed")
else:
    print("\nSome checks failed")