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
| Unintended network exposure | No inbound network listener; Lambda in private subnets with no internet route; security-group chain (Lambda SG to endpoint SG) and endpoint policies limit egress |
| Cost or schedule abuse | Restrict invocation permissions, bound schedule frequency, monitor invocation/error metrics |

## Network design note

The original design used a no-VPC Lambda to avoid networking costs, which left security-group chaining unimplemented. The updated infrastructure template is designed to run the Lambda in a private-only VPC so the chain is real and demonstrable, without adding an EC2 instance or database. It has not been deployed yet.

- **Subnets:** two private subnets in two Availability Zones, one shared route table. No internet gateway and no NAT gateway.
- **Lambda security group:** no inbound rules. Egress is TCP 443 to the endpoint security group, plus TCP 443 to the AWS-managed S3 prefix list.
- **Endpoint security group:** attached to the SNS interface endpoint. Its only inbound rule is TCP 443 with the *source set to the Lambda security group* (a security group reference, not a CIDR). It has no outbound rules.
- **S3 gateway endpoint:** private S3 access with no hourly charge. Gateway endpoints have no security group, so the Lambda egress rule to S3 uses the S3 managed prefix list (`S3PrefixListId` parameter).
- **Endpoint policies:** each endpoint allows only the actions and resources the function needs, and only for the function's execution role.
- **Default egress removed:** both security groups carry a loopback placeholder rule so the default allow-all egress rule is not created.

### Logging and tracing

- Lambda's stdout logs are delivered by the Lambda service outside the customer VPC, so no CloudWatch Logs endpoint is deployed. Add one only if code in the VPC calls the Logs API directly.
- The template creates the function's log group explicitly with 14-day retention, and the execution role may write only to that log group.
- Active X-Ray tracing is disabled; it would need `xray:PutTraceSegments` on the role and an X-Ray endpoint.

### Finding the S3 prefix list ID

```bash
aws ec2 describe-managed-prefix-lists \
  --region <region> \
  --filters Name=prefix-list-name,Values=com.amazonaws.<region>.s3 \
  --query 'PrefixLists[0].PrefixListId' \
  --output text
```

Pass the returned `pl-...` value as the `S3PrefixListId` parameter at deploy time.

### Cost note

The SNS interface endpoint bills per AZ-hour plus per GB processed. One interface endpoint across two AZs is two endpoint network interfaces; at roughly $0.01 per hour each (verify current regional pricing) that is on the order of $15/month while deployed, plus data processing. The S3 gateway endpoint is free. Delete the stack when the demo evidence is captured.

### AWS Config

AWS Config allows one configuration recorder and one delivery channel per account per Region, and this template creates both. Before deploying, check whether the account already has them (`aws configservice describe-configuration-recorders` and `describe-delivery-channels`); if it does, the Config resources must be removed or made conditional so the deployment does not fail or conflict with centrally managed Config.
