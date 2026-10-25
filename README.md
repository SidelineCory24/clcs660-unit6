# CLCS 660 Unit 6: AWS Predictive Maintenance

A course project scaffold for predicting elevated infrastructure failure risk from synthetic operational metrics, then routing high-risk predictions to an operator through Amazon SNS.

> **Status:** Local-first scaffold. The local model, synthetic dataset, tests, and evaluation scripts are intended to run first. The AWS SAM template is an implementation starting point and must be deployed and tested in your own AWS account before the report can claim cloud deployment evidence.

## Scenario and scope

- **Enhancement:** Predictive maintenance.
- **Operational question:** Based on recent utilization, latency, errors, and restart behavior, is a workload at elevated risk of a service failure in the next monitoring window?
- **Model:** Scikit-learn logistic regression trained locally; standardized features and coefficients are exported to JSON so Lambda inference can use Python's standard library.
- **Automation:** Scheduled AWS Lambda inference, with an Amazon SNS notification when the predicted risk meets a configurable threshold.
- **Safety boundary:** This implementation alerts only. It does not restart services or change production resources.
- **Data:** Synthetic data only. Do not commit real logs, customer data, credentials, account IDs, or production telemetry.

## Repository layout

```text
.
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   └── synthetic_metrics.csv
├── docs/
│   ├── architecture.md
│   ├── security-controls.md
│   ├── evaluation-plan.md
│   └── evidence-checklist.md
├── infrastructure/
│   └── template.yaml
├── src/
│   ├── __init__.py
│   ├── features.py
│   ├── model_runtime.py
│   ├── train_model.py
│   ├── evaluate_model.py
│   └── lambda_function.py
├── model/
│   └── model.json
├── tests/
│   ├── test_features.py
│   └── test_model_runtime.py
└── scripts/
    └── run_local_demo.sh
```

## Prerequisites

- Python 3.11 or later
- Git
- For AWS deployment: AWS CLI configured for the intended account/region, AWS SAM CLI, and permission to create the resources in `infrastructure/template.yaml`

## Run locally first

From the repository root:

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
python -m src.train_model
python -m src.evaluate_model
python -m unittest discover -s tests -v
```

The training script writes `model/model.json`. The evaluation script reports held-out metrics. Keep the exact output in your evidence folder and report; do not copy illustrative numbers from documentation.

### Run a sample prediction

```bash
python - <<'PY'
import json
from src.model_runtime import predict_failure_risk

with open("model/model.json", encoding="utf-8") as f:
    model = json.load(f)

sample = {
    "cpu_mean": 88.0,
    "cpu_trend": 8.0,
    "memory_mean": 91.0,
    "error_rate": 0.07,
    "latency_p95_ms": 1800.0,
    "restart_count": 3
}
print(predict_failure_risk(sample, model))
PY
```

## AWS deployment outline

1. Train and evaluate locally; inspect the metrics and model file.
2. Create an SNS topic and subscription for an email you control. Confirm the subscription from your inbox.
3. Review the SAM template and security controls before deployment.
4. Package and deploy from `infrastructure/` using SAM. Set the notification email and risk threshold parameters.
5. Upload a **synthetic** `latest_metrics.json` file to the provisioned input bucket, following `docs/architecture.md`.
6. Invoke the Lambda function manually for a smoke test, then verify logs in CloudWatch and notification delivery. Confirm the EventBridge schedule only after the smoke test.
7. Capture real evidence and record region, test date, resource configuration, and results. Never include credentials or sensitive AWS account details in public screenshots.

Example commands (review parameters and template first):

```bash
cd infrastructure
sam validate --lint
sam build
sam deploy --guided
```

The Lambda deployment package is isolated under `infrastructure/function/` so the local scikit-learn training dependencies are not bundled into the Lambda runtime. If you retrain the model, copy the newly generated `model/model.json` into `infrastructure/function/model/model.json` before `sam build`. The template is a starter and may require adjustments based on account policies and AWS Region. Review the generated change set before approving deployment.

## Cost and cleanup

The design uses scheduled Lambda execution, S3, SNS, CloudWatch Logs, KMS, and AWS Config. Charges depend on usage, retention, Region, and account settings. AWS Config can create ongoing charges. Review current AWS pricing and your account budgets before deployment. Delete project resources after evidence collection, while retaining local artifacts needed for submission.

## Security notes

- Least-privilege IAM is required; do not use administrator credentials for the deployed function.
- S3 objects are encrypted with a customer-managed KMS key in the template.
- No secrets belong in source control.
- This is a learning prototype using synthetic signals, not a validated production failure predictor.
- A high probability is a risk indicator, not proof of an impending failure. Alert-only behavior is intentional.
