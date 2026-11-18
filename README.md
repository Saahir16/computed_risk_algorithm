# computed_risk_algorithm
My repo for my code files for my honors thesis

“Computed Risk Algorithm: A Quantitative Framework for Contextual Anomaly Detection for Financial Platforms” (Arizona State University, Fall 2026).

What the code does is make simulated vendor transactions and then compare a contextual scoring framework (the Decision Risk Model and the Trust Score) against two rule based detectors. 

Files included are:

dataset.py: makes the simulated transactions
detectors.py: has the rule based detectors, the contextual framework, and the metrics
experiments.py: runs everything on 30 seeds and saves the results
double_check.py: checks the code with separate loops
charts.py: has the colors and style for the figures
dataset_figure.py, overall_figure.py, figures_by_type.py, score_distribution.py, and detection_and_precision_figure.py: the five figures/graphs from the experiments

How to run everything:

pip install -r requirements.txt
Make the data and results folders in the same space as the files since the figures will be saved in there alongside other things

Commands to run:
python dataset.py --seed 42 --n 1000 --out data/transactions_seed42.csv

python experiments.py

python double_check.py

python dataset_figure.py

python overall_figure.py

python figures_by_type.py

python score_distribution.py

python detection_and_precision_figure.py
