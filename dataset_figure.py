"""
This figure shows what is inside the simulated dataset (seed 42 and 1,000 transactions).
"""

import matplotlib.pyplot as plt
import pandas as pd
from charts import teal, gray_text, clean, save, setup

setup()

data = pd.read_csv("data/transactions_seed42.csv")

# names in the data and labels shown on figure
anomaly_names = {
    "spike_below_threshold": "Spike below $10k threshold",
    "bank_change": "Bank account change",
    "split_invoicing": "Split invoicing",
    "large_amount": "Large amount",
    "approval_ledger_bypass": "Approval / ledger bypass",
    "subtle_drift": "Subtle drift",
}
normal_names = {
    "large_vendor_routine": "Large vendor, routine invoice",
    "new_vendor": "New vendor",
    "one_off_bulk_order": "One-off bulk order",
    "legit_bank_change": "Legitimate bank change",
}

# how many of each type there are
anomaly_counts = data[data["anomaly"] == 1]["anomaly_type"].value_counts()
anomaly_counts = anomaly_counts.rename(index=anomaly_names).sort_values()

unusual_normal = data[(data["anomaly"] == 0) & (data["normal_subtype"].isin(normal_names))]
normal_counts = unusual_normal["normal_subtype"].value_counts()
normal_counts = normal_counts.rename(index=normal_names).sort_values()

figure, axes = plt.subplots(1, 2, figsize=(11, 4.4))
panels = [(axes[0], anomaly_counts, teal, f"Injected anomalies ({int(anomaly_counts.sum())} of {len(data)})"), (axes[1], normal_counts, gray_text, "Legitimate but unusual transactions")]
for ax, counts, color, title in panels:
    bars = ax.barh(counts.index, counts.values, height=0.6, color=color, zorder=3)
    for bar, count in zip(bars, counts.values):
        ax.text(count + counts.max() * 0.015, bar.get_y() + bar.get_height() / 2, str(int(count)),
                va="center", fontsize=10.5, color=gray_text)

    ax.set_xlim(0, counts.max() * 1.15)
    ax.set_title(title, fontsize=12)
    ax.set_xlabel("Number of transactions")
    clean(ax, "x")

figure.suptitle("Composition of the simulated dataset", x=0.02, ha="left", y=1.02, fontsize=13, fontweight="bold")
figure.tight_layout()
save(figure, "dataset_figure")