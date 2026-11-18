"""
This file has the detection approaches with the evaluation metrics.
"""
import numpy as np

threshold = 10_000
risk_weights = {"historical_deviation": 0.30, "revenue_cost_ratio_change": 0.25, "budget_variance": 0.20, "vendor_frequency_shift": 0.15, "peer_department_deviation": 0.10}

trust_weights = {"vendor_history": 0.30, "approval_chain": 0.25, "timing_consistency": 0.20, "bank_stability": 0.15, "cross_ledger": 0.10}

# same weight for every signal
equal_risk_weights = {}
for signal in risk_weights:
    equal_risk_weights[signal] = 0.20

equal_trust_weights = {}
for signal in trust_weights:
    equal_trust_weights[signal] = 0.20

def risk_score(data, weights=risk_weights):
    score = 0
    for signal in weights:
        score = score + data[signal] * weights[signal]
    return score

def trust_score(data, weights=trust_weights):
    score = 0
    for signal in weights:
        score = score + data[signal] * weights[signal]
    return score

def build_detectors(data):
    # returns each detector with True for every transaction flagged
    risk = risk_score(data)
    trust = trust_score(data)
    equal_risk = risk_score(data, equal_risk_weights)
    equal_trust = trust_score(data, equal_trust_weights)

    incomplete_approvals = data["signed_approvals"] < data["required_approvals"]

    return {
        # rule based baselines
        "single_rule": data["amount"] > threshold, "multiple_rules": ((data["amount"] > threshold) | (data["days_since_bank_change"] < 30) | incomplete_approvals | (data["ledger_mismatch_pct"] > 10)),
        # main contextual detector where 61 and higher is high risk and below 60 is blocked
        "contextual_main": (risk >= 61) | (trust < 60),
        # other thresholds and weights
        "contextual_risk_only": risk >= 61, "contextual_trust_only": trust < 60, "contextual_looser": (risk >= 31) | (trust < 85), "contextual_equal_weights": (equal_risk >= 61) | (equal_trust < 60),
    }

def metrics(actual_anomaly, flagged):
    actual = np.asarray(actual_anomaly).astype(bool)
    flagged = np.asarray(flagged).astype(bool)

    true_positives = int((actual & flagged).sum())
    false_positives = int((~actual & flagged).sum())
    false_negatives = int((actual & ~flagged).sum())
    true_negatives = int((~actual & ~flagged).sum())

    detection_rate = true_positives / (true_positives + false_negatives)
    false_positive_rate = false_positives / (false_positives + true_negatives)
    false_negative_rate = false_negatives / (true_positives + false_negatives)

    # if nothing flagged then precision is 0
    if true_positives + false_positives == 0:
        precision = 0.0
    else:
        precision = true_positives / (true_positives + false_positives)

    if precision + detection_rate == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * detection_rate / (precision + detection_rate)

    return dict(
        true_positives=true_positives,
        false_positives=false_positives,
        false_negatives=false_negatives,
        true_negatives=true_negatives,
        detection_rate=detection_rate,
        false_positive_rate=false_positive_rate,
        false_negative_rate=false_negative_rate,
        precision=precision,
        f1=f1,
    )