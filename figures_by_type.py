"""
This figure shows the share of each anomaly type that each detector caught with a mean of 30 runs.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from charts import dark_text, teal_scale, save, setup

setup()

type_table = pd.read_csv("results/detection_by_anomaly_type.csv", index_col=0)

# column names in the csv and labels shown on figure
detector_columns = {"Rule: single threshold (greater than $10k)": "Single\nthreshold", "Rule: multi-rule engine": "Multi-rule\nengine", "Contextual: Risk>=61 OR Trust<60": "Contextual\nframework"}
anomaly_rows = {
    "large_amount": "Large amount",
    "spike_below_threshold": "Spike below the $10k threshold",
    "bank_change": "Bank account change",
    "split_invoicing": "Split invoicing",
    "approval_ledger_bypass": "Approval / ledger bypass",
    "subtle_drift": "Subtle drift",
}
shares = type_table.loc[list(anomaly_rows), list(detector_columns)].to_numpy()
figure, ax = plt.subplots(figsize=(8, 4.8))
ax.imshow(shares, cmap=teal_scale, vmin=0, vmax=1, aspect="auto")
ax.set_xticks(range(len(detector_columns)))
ax.set_xticklabels(list(detector_columns.values()))
ax.xaxis.tick_top()
ax.set_yticks(range(len(anomaly_rows)))
ax.set_yticklabels(list(anomaly_rows.values()))

# percent written inside each cell
for row in range(shares.shape[0]):
    for column in range(shares.shape[1]):
        share = shares[row, column]
        if share > 0.65:
            text_color = "white"
        else:
            text_color = dark_text
        ax.text(column, row, f"{share * 100:.0f}%", ha="center", va="center", fontsize=11, color=text_color)

# white gaps between cells
ax.set_xticks(np.arange(-0.5, shares.shape[1], 1), minor=True)
ax.set_yticks(np.arange(-0.5, shares.shape[0], 1), minor=True)
ax.grid(which="minor", color="white", linewidth=3)
ax.tick_params(which="both", length=0)
for spine in ax.spines.values():
    spine.set_visible(False)

ax.set_title("Share of each anomaly type detected", pad=48)
save(figure, "figures_by_type")