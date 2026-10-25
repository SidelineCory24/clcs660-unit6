# Evaluation Plan

## Research question

Does the predictive maintenance model identify synthetic records labeled as a failure within the next observation window more effectively than a simple threshold baseline, while avoiding excessive false alarms?

## Data and split

- Use only the included synthetic dataset.
- Use a fixed random seed and stratified holdout split for reproducibility.
- Fit the scaler and model only on training data to prevent data leakage.
- Evaluate once on the held-out set; do not tune the threshold on that same test set.
- Because the data is synthetic and generated from simplified assumptions, results demonstrate pipeline behavior, not real-world predictive validity.

## Metrics

- Precision: proportion of elevated-risk predictions that are positive cases.
- Recall: proportion of positive cases detected.
- F1: harmonic mean of precision and recall.
- ROC-AUC: ranking performance across thresholds.
- Confusion matrix: counts of true/false positives and negatives.
- Operational metrics in AWS: Lambda duration, errors, invocations, SNS delivery, and estimated monthly cost.

## Baseline and threshold

Compare against a transparent threshold baseline, such as flagging when CPU mean exceeds a chosen value or when two or more operational signals exceed defined thresholds. Document the threshold before evaluating. The model threshold of 0.65 is a starting configuration, not a universally optimal value.

## Success criteria to validate

1. All automated tests pass.
2. Invalid or incomplete telemetry is rejected without sending an alert.
3. Held-out recall and precision are reported; desired minimums must be justified by the cost of missed failures versus false alarms.
4. An elevated-risk synthetic sample triggers one SNS alert; a normal sample does not.
5. IAM, encryption, logging, and Config controls are verified with real evidence.
6. The report distinguishes local results, synthetic results, and actual AWS observations.

Do not claim success until test outputs and deployed evidence have been collected.
