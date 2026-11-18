"""
This figure shows the overall performance of the three detectors with a mean of 30 runs.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from charts import teal, coral, light_coral, gray_text, clean, save, setup

setup()

runs = pd.read_csv("results/per_run_metrics.csv")
means = runs.groupby("detector")[["detection_rate", "false_positive_rate", "precision"]].mean()

# detector name, label for the legend, bar color
detectors = [("single_rule", "Single threshold (> $10k)", light_coral), ("multiple_rules", "Multi-rule engine", coral), ("contextual_main", "Contextual framework", teal)]
metric_labels = [("detection_rate", "Detection rate\n(higher is better)"), ("false_positive_rate", "False positive rate\n(lower is better)"), ("precision", "Precision\n(higher is better)")]

figure, ax = plt.subplots(figsize=(8.5, 4.8))
positions = np.arange(len(metric_labels))
bar_width = 0.26

for number, (detector_name, label, color) in enumerate(detectors):
    values = []
    for metric_name, metric_label in metric_labels:
        values.append(means.loc[detector_name, metric_name])

    # moving each detector's bar
    bars = ax.bar(positions + (number - 1) * (bar_width + 0.03), values, bar_width, color=color, label=label, zorder=3)

    # number on top of the bar
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.015, f"{value:.2f}", ha="center", va="bottom", fontsize=10, color=gray_text)

ax.set_xticks(positions)
ax.set_xticklabels([metric_label for metric_name, metric_label in metric_labels])
ax.set_ylim(0, 1.0)
ax.set_ylabel("Share (mean of 30 runs)")
clean(ax, "y")
ax.legend(frameon=False, ncol=3, loc="lower left", bbox_to_anchor=(0, 1.0))
ax.set_title("Overall performance", pad=34)
save(figure, "overall_figure")