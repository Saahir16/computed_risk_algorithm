# Experiment results

30 independent runs x 1000 transactions (about 10% of them are anomalies). Each value is the mean of 30 runs with a 95% confidence interval after the +/-.

## Overall metrics

| detector                                       | detection_rate   | false_positive_rate   | false_negative_rate   | precision       | f1              |
|:-----------------------------------------------|:-----------------|:----------------------|:----------------------|:----------------|:----------------|
| Rule: single threshold (greater than $10k)     | 0.264 +/- 0.017  | 0.212 +/- 0.020       | 0.736 +/- 0.017       | 0.127 +/- 0.012 | 0.169 +/- 0.012 |
| Rule: multi-rule engine                        | 0.633 +/- 0.019  | 0.236 +/- 0.020       | 0.367 +/- 0.019       | 0.238 +/- 0.018 | 0.343 +/- 0.019 |
| Contextual: Risk>=61 OR Trust<60               | 0.681 +/- 0.016  | 0.036 +/- 0.005       | 0.319 +/- 0.016       | 0.687 +/- 0.032 | 0.682 +/- 0.021 |
| Contextual: Risk>=61 only                      | 0.517 +/- 0.018  | 0.023 +/- 0.002       | 0.483 +/- 0.018       | 0.718 +/- 0.022 | 0.599 +/- 0.015 |
| Contextual: Trust<60 only                      | 0.172 +/- 0.013  | 0.013 +/- 0.005       | 0.828 +/- 0.013       | 0.664 +/- 0.081 | 0.267 +/- 0.018 |
| Contextual: Risk>=31 OR Trust<85               | 1.000 +/- 0.000  | 0.283 +/- 0.016       | 0.000 +/- 0.000       | 0.287 +/- 0.014 | 0.444 +/- 0.016 |
| Contextual: equal weights (primary thresholds) | 0.545 +/- 0.023  | 0.018 +/- 0.002       | 0.455 +/- 0.023       | 0.769 +/- 0.021 | 0.636 +/- 0.019 |

## Detection rate by anomaly type

| anomaly_type           |   Rule: single threshold (greater than $10k) |   Rule: multi-rule engine |   Contextual: Risk>=61 OR Trust<60 |   Contextual: Risk>=61 only |   Contextual: Trust<60 only |   Contextual: Risk>=31 OR Trust<85 |   Contextual: equal weights (primary thresholds) |
|:-----------------------|---------------------------------------------:|--------------------------:|-----------------------------------:|----------------------------:|----------------------------:|-----------------------------------:|-------------------------------------------------:|
| large_amount           |                                        1     |                     1     |                              0.985 |                       0.985 |                       0.002 |                                  1 |                                            0.877 |
| spike_below_threshold  |                                        0     |                     0     |                              0.904 |                       0.904 |                       0     |                                  1 |                                            0.484 |
| bank_change            |                                        0.206 |                     1     |                              0.163 |                       0.017 |                       0.148 |                                  1 |                                            0.143 |
| split_invoicing        |                                        0     |                     0.594 |                              0.544 |                       0.544 |                       0     |                                  1 |                                            0.476 |
| approval_ledger_bypass |                                        0.206 |                     1     |                              0.862 |                       0.007 |                       0.862 |                                  1 |                                            0.97  |
| subtle_drift           |                                        0.442 |                     0.442 |                              0.595 |                       0.578 |                       0.069 |                                  1 |                                            0.411 |

## Paired difference: contextual minus multi rule engine

| metric              |   mean_diff |   ci95 |   p_value |
|:--------------------|------------:|-------:|----------:|
| detection_rate      |      0.048  | 0.0295 |    0.0024 |
| false_positive_rate |     -0.1995 | 0.0199 |    0      |
| false_negative_rate |     -0.048  | 0.0295 |    0.0024 |
| precision           |      0.4485 | 0.0364 |    0      |
| f1                  |      0.3389 | 0.0296 |    0      |

## Mean confusion counts per 1,000 transactions

|                                                |   true_positives |   false_positives |   false_negatives |   true_negatives |
|:-----------------------------------------------|-----------------:|------------------:|------------------:|-----------------:|
| Rule: single threshold (greater than $10k)     |             26.6 |             191.2 |              74.3 |            707.9 |
| Rule: multi-rule engine                        |             63.9 |             212.2 |              37.1 |            686.9 |
| Contextual: Risk>=61 OR Trust<60               |             68.7 |              32.6 |              32.3 |            866.5 |
| Contextual: Risk>=61 only                      |             52.1 |              20.7 |              48.9 |            878.4 |
| Contextual: Trust<60 only                      |             17.3 |              12.1 |              83.6 |            887   |
| Contextual: Risk>=31 OR Trust<85               |            100.9 |             254.7 |               0   |            644.4 |
| Contextual: equal weights (primary thresholds) |             55.1 |              16.6 |              45.8 |            882.5 |
