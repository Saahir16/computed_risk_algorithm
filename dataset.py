"""
This file makes the synthetic transaction data for my thesis.
Command: python dataset.py --seed 42 --n 1000 --out data/transactions_seed42.csv
"""

import argparse
import numpy as np
import pandas as pd

threshold = 10_000

departments = ["Operations", "Marketing", "Engineering", "Sales", "HR", "Facilities"]

anomaly_types = {"large_amount": 0.15, "spike_below_threshold": 0.25, "bank_change": 0.20, "split_invoicing": 0.15, "approval_ledger_bypass": 0.15, "subtle_drift": 0.10}

anomaly_rate = 0.10
bulk_order_rate = 0.05
real_bank_change_rate = 0.03

def needed_approvals(amount):
    if amount >= threshold:
        return 3
    return 2

def make_vendors(random_generator, number_of_vendors=60):
    department_cost = {}
    for department in departments:
        department_cost[department] = random_generator.uniform(80_000, 250_000)

    vendor_rows = []
    for vendor_id in range(number_of_vendors):
        size = random_generator.choice(["small", "mid", "large"], p=[0.45, 0.35, 0.20])
        if size == "small":
            average_amount = random_generator.uniform(800, 2_400)
        elif size == "mid":
            average_amount = random_generator.uniform(3_000, 7_000)
        else:
            average_amount = random_generator.uniform(11_000, 28_000)  # over the 10k rule

        spread = random_generator.uniform(0.08, 0.35)
        new_vendor = random_generator.random() < 0.08
        if new_vendor:
            tenure_months = int(random_generator.integers(1, 4))
        else:
            tenure_months = int(random_generator.integers(12, 73))

        usual_monthly_count = int(random_generator.integers(1, 7))
        history_length = int(np.clip(tenure_months * usual_monthly_count, 6, 60))
        history = average_amount * np.exp(random_generator.normal(-spread**2 / 2, spread, history_length))
        department = str(random_generator.choice(departments))

        vendor_rows.append(
            dict(
                vendor_id=vendor_id,
                department=department,
                size=size,
                new_vendor=new_vendor,
                true_average=average_amount,
                spread=spread,
                tenure_months=tenure_months,
                usual_monthly_count=usual_monthly_count,
                usual_day=int(random_generator.integers(3, 26)),
                history_average=float(history.mean()),
                history_std=float(history.std(ddof=1)),
                bank_age_days=tenure_months * 30 if new_vendor else int(random_generator.integers(400, 2000)),
                budget=average_amount * random_generator.uniform(0.95, 1.15),
                department_monthly_cost=department_cost[department],
            )
        )

    vendors = pd.DataFrame(vendor_rows)
    vendors["history_spread"] = vendors["history_std"] / vendors["history_average"]

    # average amount of other vendors in same department
    peer = vendors.groupby("department")["history_average"].agg(peer_average="mean", peer_std="std").reset_index()
    peer["peer_std"] = peer["peer_std"].fillna(1_000).clip(lower=1_000)
    return vendors.merge(peer, on="department", how="left")


def generate(seed=42, number_of_transactions=1000):
    random_generator = np.random.default_rng(seed)
    vendors = make_vendors(random_generator)

    # vendors that bill more often show up more often
    vendor_weights = vendors["usual_monthly_count"].to_numpy(float)
    vendor_weights = vendor_weights / vendor_weights.sum()

    old_vendors = vendors[(vendors["true_average"] <= 2_400) & (~vendors["new_vendor"])]

    anomaly_names = list(anomaly_types)
    anomaly_probabilities = np.array(list(anomaly_types.values()))

    rows = []
    for transaction_id in range(number_of_transactions):
        anomaly = random_generator.random() < anomaly_rate
        if anomaly:
            anomaly_type = str(random_generator.choice(anomaly_names, p=anomaly_probabilities))
        else:
            anomaly_type = "none"

        if anomaly_type in ("spike_below_threshold", "split_invoicing"):
            vendor = old_vendors.iloc[int(random_generator.integers(len(old_vendors)))]
        else:
            vendor = vendors.iloc[int(random_generator.choice(len(vendors), p=vendor_weights))]

        average_amount = vendor["true_average"]
        spread = vendor["spread"]
        amount = average_amount * np.exp(random_generator.normal(-spread**2 / 2, spread))
        day_offset = random_generator.normal(0, 2)
        bank_days = float(vendor["bank_age_days"])
        ledger_mismatch = abs(random_generator.normal(0, 0.8))  # percent
        invoice_count = 1 + random_generator.poisson(max(vendor["usual_monthly_count"] - 1, 0))
        revenue_growth = random_generator.normal(0, 0.015)
        normal_subtype = "normal"

        # unusual but normal transactions
        if not anomaly:
            roll = random_generator.random()
            if roll < bulk_order_rate:
                amount = average_amount * random_generator.uniform(1.5, 2.5)
                normal_subtype = "one_off_bulk_order"
            elif roll < bulk_order_rate + real_bank_change_rate:
                bank_days = float(random_generator.integers(1, 20))
                normal_subtype = "legit_bank_change"
            elif vendor["new_vendor"]:
                normal_subtype = "new_vendor"
            elif vendor["size"] == "large":
                normal_subtype = "large_vendor_routine"

        required_approvals = needed_approvals(amount)
        signed_approvals = required_approvals

        # change transaction if it is an anomaly
        if anomaly_type == "large_amount":
            amount = max(threshold * 1.05, average_amount * random_generator.uniform(3, 8))
            required_approvals = needed_approvals(amount)
            signed_approvals = required_approvals
        elif anomaly_type == "spike_below_threshold":
            amount = min(average_amount * random_generator.uniform(4, 9), 9_900)
            revenue_growth = random_generator.normal(-0.01, 0.015)
            required_approvals = 2
            signed_approvals = 2
        elif anomaly_type == "bank_change":
            bank_days = float(random_generator.integers(1, 10))
            amount = average_amount * random_generator.uniform(1.0, 1.6)
            required_approvals = needed_approvals(amount)
            if random_generator.random() < 0.5:
                signed_approvals = required_approvals
            else:
                signed_approvals = required_approvals - 1
        elif anomaly_type == "split_invoicing":
            amount = average_amount * random_generator.uniform(1.4, 2.6)
            invoice_count = int(np.ceil(vendor["usual_monthly_count"] * random_generator.uniform(2.5, 4.0))) + 1
            day_offset = random_generator.normal(0, 4)
            required_approvals = needed_approvals(amount)
            if random_generator.random() < 0.6:
                signed_approvals = required_approvals - 1
            else:
                signed_approvals = required_approvals
        elif anomaly_type == "approval_ledger_bypass":
            amount = average_amount * random_generator.uniform(1.0, 1.5)
            required_approvals = needed_approvals(amount)
            signed_approvals = int(random_generator.integers(0, required_approvals))
            ledger_mismatch = random_generator.uniform(12, 40)
            day_offset = random_generator.choice([-1, 1]) * random_generator.uniform(5, 12)
        elif anomaly_type == "subtle_drift":
            amount = average_amount * random_generator.uniform(1.8, 3.0)
            required_approvals = needed_approvals(amount)
            signed_approvals = required_approvals
            day_offset = random_generator.choice([-1, 1]) * random_generator.uniform(5, 10)
            ledger_mismatch = random_generator.uniform(3, 9)

        # features come from the vendor's history
        z_score = abs(amount - vendor["history_average"]) / vendor["history_std"]
        revenue_cost_change = revenue_growth - (amount - vendor["history_average"]) / vendor["department_monthly_cost"]
        budget_difference = abs(amount - vendor["budget"]) / vendor["budget"]
        usual_count = vendor["usual_monthly_count"]
        frequency_difference = abs(invoice_count - usual_count) / max(usual_count, 1)
        peer_z_score = abs(amount - vendor["peer_average"]) / vendor["peer_std"]

        rows.append(
            dict(
                transaction_id=transaction_id,
                vendor_id=int(vendor["vendor_id"]),
                department=vendor["department"],
                amount=round(float(amount), 2),
                required_approvals=int(required_approvals), # rule based detectors use these
                signed_approvals=int(signed_approvals),
                days_since_bank_change=bank_days,
                ledger_mismatch_pct=round(float(ledger_mismatch), 3),
                historical_deviation=min(100.0, 100 * z_score / 5), # decision risk model features
                revenue_cost_ratio_change=min(100.0, abs(revenue_cost_change) * 1250),
                budget_variance=min(100.0, 100 * budget_difference),
                vendor_frequency_shift=min(100.0, 50 * frequency_difference),
                peer_department_deviation=min(100.0, 100 * peer_z_score / 3),
                vendor_history=100 * (1 - min(1.0, vendor["history_spread"])) * np.sqrt(min(1.0, vendor["tenure_months"] / 18)), # trust score features
                approval_chain=100 * signed_approvals / required_approvals,
                timing_consistency=100 - min(100.0, 100 * abs(day_offset) / 12),
                bank_stability=100 * min(1.0, bank_days / 180),
                cross_ledger=100 - min(100.0, 100 * ledger_mismatch / 20),
                anomaly=int(anomaly),
                anomaly_type=anomaly_type,
                normal_subtype=normal_subtype if not anomaly else "",
            )
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--n", type=int, default=1000)
    parser.add_argument("--out", default="data/transactions_seed42.csv")
    args = parser.parse_args()

    data = generate(args.seed, args.n)
    data.to_csv(args.out, index=False)
    print(f"{len(data)} transactions to {args.out}")
    print(data["anomaly_type"].value_counts().to_string())