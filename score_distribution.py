"""
This figure shows the Risk Score and Trust Score for normal and anomalous transactions in the seed 42 dataset.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch
from charts import teal, gray_text, clean, save, setup

setup()

# normal transactions are gray and teal for the anomalies
normal_color = gray_text
anomaly_color = teal

data = pd.read_csv("data/transactions_seed42_scored.csv")
normal = data[data["anomaly"] == 0]
anomalous = data[data["anomaly"] == 1]
bin_edges = np.arange(0, 105, 5)

# column, x label, alert line, line label
panels = [("risk_score", "Risk Score (higher means riskier)", 61, "Alert at 61 or higher", 1), ("trust_score", "Trust Score (higher means safer)", 60, "Alert below 60", -1)]

figure, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True)
for axe, (column, x_label, alert_line, line_label, side) in zip(axes, panels):
    for group, color in [(normal, normal_color), (anomalous, anomaly_color)]:
        counts = np.histogram(group[column], bins=bin_edges)[0]
        shares = counts / len(group)
        axe.stairs(shares, bin_edges, fill=True, color=color, alpha=0.55, linewidth=0)
        axe.stairs(shares, bin_edges, color=color, linewidth=1.5)

    axe.axvline(alert_line, color=gray_text, linestyle="--", linewidth=1.2)
    if side > 0:
        label_side = "left"
    else:
        label_side = "right"
    axe.text(alert_line + side * 1.5, axe.get_ylim()[1] * 0.97, line_label, fontsize=10, color=gray_text, va="top", ha=label_side)
    axe.set_xlabel(x_label)
    axe.set_xlim(0, 100)
    clean(axe, "y")

axes[0].set_ylabel("Share of that group's transactions")
figure.legend(
    handles=[Patch(facecolor=normal_color, alpha=0.55, edgecolor=normal_color, label="Normal transactions"), Patch(facecolor=anomaly_color, alpha=0.55, edgecolor=anomaly_color, label="Anomalous transactions")], frameon=False, ncol=2, loc="upper left", bbox_to_anchor=(0.06, 1.0))
figure.suptitle("Score distributions, normal vs anomalous", x=0.06, ha="left", y=1.08, fontsize=13, fontweight="bold")
save(figure, "score_distribution")