# Architecture and Data Flow

## Purpose

The solution predicts elevated failure risk from a compact set of operational indicators and alerts an operator. It is deliberately alert-only; no infrastructure mutation is performed automatically.

## Components

1. **CloudWatch (planned AWS telemetry source):** A production adaptation can collect CPU, latency, error, and restart metrics. Standard EC2 metrics do not include every feature in this model; memory and application-specific measurements require an agent or application instrumentation.
2. **S3 input bucket:** Holds `latest_metrics.json`. The initial deployment uses synthetic data. Do not upload real or sensitive logs to the public project.
3. **Python logistic regression:** Trained locally on synthetic labeled records. The exported JSON contains scaler parameters and coefficients. Lambda performs inference with Python's standard library.
4. **EventBridge Scheduler/rule:** Invokes Lambda on a schedule.
5. **Lambda:** Reads input data, calculates failure probability, stores a prediction, and publishes an alert only when the configured threshold is met.
6. **SNS:** Delivers notifications to a confirmed subscription.
7. **KMS and IAM:** Encrypt S3 objects and restrict the function to required actions and resources.
8. **AWS Config:** Records supported resource configuration and can evaluate selected configuration rules. Config is a configuration compliance service, not the predictive model.

## Data contract

`latest_metrics.json` must contain numeric fields:

```json
{
  "cpu_mean": 88.0,
  "cpu_trend": 8.0,
  "memory_mean": 91.0,
  "error_rate": 0.07,
  "latency_p95_ms": 1800.0,
  "restart_count": 3
}
```

Values are illustrative synthetic examples. `cpu_mean` and `memory_mean` are percentages; `error_rate` is between 0 and 1; `latency_p95_ms` is milliseconds; `cpu_trend` is the change in CPU percentage points over the selected observation window; `restart_count` is the restart count in that window.

## Threat model summary

| Threat | Mitigation |
|---|---|
| Unauthorized access to telemetry | S3 Block Public Access, least-privilege IAM, encryption at rest |
| Model/input tampering | Restrict write access; version artifacts; validate required fields and ranges |
| Excessive alerting | Threshold, SNS subscription controls, CloudWatch monitoring |
| Incorrect prediction | Alert-only operation, held-out testing, human review, documented limitations |
| Credential exposure | IAM roles, no embedded keys, `.gitignore`, secret scanning |
| Unintended network exposure | No inbound network listener; avoid VPC attachment unless required; document SG/endpoint design if VPC access is introduced |
| Cost or schedule abuse | Restrict invocation permissions, bound schedule frequency, monitor invocation/error metrics |

## Network design note

The starter Lambda does not require VPC attachment because it calls AWS service APIs and does not connect to private application resources. This avoids adding NAT and endpoint costs. Security-group chaining is not applicable to this no-VPC baseline. If the instructor requires an explicit security-group-chain demonstration, add a documented VPC variant with a Lambda security group referencing a private endpoint/application security group and appropriate VPC endpoints; do not claim this is implemented by the baseline template.
