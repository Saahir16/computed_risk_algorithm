"""
Command: python experiments.py
"""

import numpy as np
import pandas as pd
from scipy import stats
from detectors import build_detectors, metrics, risk_score, trust_score
from dataset import anomaly_types, generate

number_of_runs = 30
number_of_transactions = 1000
seeds = list(range(1, number_of_runs + 1))
metric_names = ["detection_rate", "false_positive_rate", "false_negative_rate", "precision", "f1"]

detector_labels = {
    "single_rule": "Rule: single threshold (greater than $10k)",
    "multiple_rules": "Rule: multi-rule engine",
    "contextual_main": "Contextual: Risk>=61 OR Trust<60",
    "contextual_risk_only": "Contextual: Risk>=61 only",
    "contextual_trust_only": "Contextual: Trust<60 only",
    "contextual_looser": "Contextual: Risk>=31 OR Trust<85",
    "contextual_equal_weights": "Contextual: equal weights (primary thresholds)",
}

# 95% confidence interval
def confidence_interval(values):
    values = np.asarray(values, float)
    if len(values) < 2:
        return 0.0
    standard_error = values.std(ddof=1) / np.sqrt(len(values))
    return float(stats.t.ppf(0.975, len(values) - 1) * standard_error)

# every detector on every seed
run_results = []
type_results = []
for seed in seeds:
    data = generate(seed, number_of_transactions)
    detectors = build_detectors(data)
    for detector_name, flagged in detectors.items():
        result = metrics(data["anomaly"], flagged)
        result["seed"] = seed
        result["detector"] = detector_name
        run_results.append(result)

        # each anomaly type the detector got
        for anomaly_type in anomaly_types:
            this_type = data["anomaly_type"] == anomaly_type
            if this_type.sum() > 0:
                type_results.append(
                    dict(seed=seed, detector=detector_name, anomaly_type=anomaly_type,
                         n=int(this_type.sum()), detected=float(flagged[this_type].mean()))
                )

runs = pd.DataFrame(run_results)
runs.to_csv("results/per_run_metrics.csv", index=False)

# summary table
summary_rows = []
for detector_name in detector_labels:
    detector_runs = runs[runs["detector"] == detector_name]
    row = {"detector": detector_labels[detector_name]}
    for metric in metric_names:
        row[metric] = f"{detector_runs[metric].mean():.3f} +/- {confidence_interval(detector_runs[metric]):.3f}"
    summary_rows.append(row)
summary = pd.DataFrame(summary_rows)
summary.to_csv("results/summary.csv", index=False)

# detection rate by the anomaly type
by_type = pd.DataFrame(type_results)
type_table = by_type.groupby(["anomaly_type", "detector"])["detected"].mean().unstack("detector")
type_table = type_table[list(detector_labels)].rename(columns=detector_labels).round(3)
type_table = type_table.loc[list(anomaly_types)]
type_table.to_csv("results/detection_by_anomaly_type.csv")

# contextual detector versus multiple rules
pivot = runs.pivot(index="seed", columns="detector")
paired_rows = []
for metric in metric_names:
    difference = pivot[metric]["contextual_main"] - pivot[metric]["multiple_rules"]
    p_value = stats.ttest_rel(pivot[metric]["contextual_main"], pivot[metric]["multiple_rules"]).pvalue
    paired_rows.append(dict(metric=metric, mean_diff=difference.mean(), ci95=confidence_interval(difference), p_value=p_value))
paired = pd.DataFrame(paired_rows)
paired.to_csv("results/paired_contextual_vs_multiple_rules.csv", index=False)

# average confusion counts
counts = runs.groupby("detector")[["true_positives", "false_positives", "false_negatives", "true_negatives"]].mean()
counts = counts.loc[list(detector_labels)].round(1)
counts.index = [detector_labels[name] for name in counts.index]

with open("results/results_table.md", "w") as file:
    file.write(f"# Experiment results\n\n{number_of_runs} independent runs x {number_of_transactions} transactions "
               f"(about 10% of them are anomalies). Each value is the mean of 30 runs with a 95% confidence interval after the +/-.\n\n")
    file.write("## Overall metrics\n\n" + summary.to_markdown(index=False) + "\n\n")
    file.write("## Detection rate by anomaly type\n\n" + type_table.to_markdown() + "\n\n")
    file.write("## Paired difference: contextual minus multi rule engine\n\n" + paired.round(4).to_markdown(index=False) + "\n\n")
    file.write("## Mean confusion counts per 1,000 transactions\n\n" + counts.to_markdown() + "\n")

print(open("results/results_table.md").read())

# seed 42 data with the scores and alerts
data_42 = generate(42, number_of_transactions)
data_42["risk_score"] = risk_score(data_42).round(2)
data_42["trust_score"] = trust_score(data_42).round(2)
for detector_name, flagged in build_detectors(data_42).items():
    data_42["alert_" + detector_name] = flagged.astype(int)
data_42.to_csv("data/transactions_seed42_scored.csv", index=False)