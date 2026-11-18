"""
This figure shows the detection rate against precision for every detector and setting I tested with a mean of 30 runs.
"""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

from charts import teal, coral, dark_text, gray_text, clean, save, setup

setup()

runs = pd.read_csv("results/per_run_metrics.csv")
means = runs.groupby("detector")[["detection_rate", "precision"]].mean()

# detector name: (label, contextual detector, x offset, y offset, alignment)
points = {
    "single_rule": ("Single threshold", False, 10, 0, "left"),
    "multiple_rules": ("Multi-rule engine", False, 10, -14, "left"),
    "contextual_main": ("Contextual (primary)", True, 12, -2, "left"),
    "contextual_risk_only": ("Risk Score only", True, -10, 0, "right"),
    "contextual_trust_only": ("Trust Score only", True, 0, 16, "center"),
    "contextual_looser": ("Looser thresholds", True, -10, 0, "right"),
    "contextual_equal_weights": ("Equal weights", True, -10, 8, "right"),
}

figure, ax = plt.subplots(figsize=(8.5, 5.2))
for detector_name, (label, contextual_detector, x_offset, y_offset, alignment) in points.items():
    detection_rate = means.loc[detector_name, "detection_rate"]
    precision = means.loc[detector_name, "precision"]

    # main contextual detector gets a bigger dot and bold label
    main_detector = detector_name == "contextual_main"
    if main_detector:
        dot_size = 150
        label_color = dark_text
        label_weight = "bold"
    else:
        dot_size = 80
        label_color = gray_text
        label_weight = "normal"

    if contextual_detector:
        dot_color = teal
    else:
        dot_color = coral

    ax.scatter(detection_rate, precision, s=dot_size, color=dot_color, edgecolor="white", linewidth=1.5, zorder=3)
    ax.annotate(label, (detection_rate, precision), xytext=(x_offset, y_offset), textcoords="offset points",
                ha=alignment, va="center", fontsize=10.5, color=label_color, fontweight=label_weight)

ax.set_xlim(0, 1.08)
ax.set_ylim(0, 0.9)
ax.set_xlabel("Detection rate (share of anomalies caught)")
ax.set_ylabel("Precision (share of alerts that were real)")
clean(ax, "both")
ax.legend(
    handles=[Line2D([], [], marker="o", linestyle="", color=coral, markersize=8, label="Rule based"), Line2D([], [], marker="o", linestyle="", color=teal, markersize=8, label="Contextual framework (variants)")], frameon=False, ncol=2, loc="lower left", bbox_to_anchor=(0, 1.0))
ax.set_title("Detection vs precision across settings", pad=34)
save(figure, "detection_and_precision_figure")