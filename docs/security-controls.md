# Security Controls and Standards Mapping

Use this mapping as a starting point. Verify exact control identifiers and wording against the version of each framework available to you, then cite the authoritative source in the report. A mapping is not proof of implementation; attach evidence from the deployed account.

| Framework / practice | Project implementation | Evidence to collect |
|---|---|---|
| AWS Well-Architected Security: least privilege | Lambda execution role limited to input/output object access, KMS use, SNS publish, and logs | IAM role and policy screenshots; policy JSON |
| AWS Well-Architected Security: traceability | CloudWatch Logs for each invocation; prediction timestamp and model version | Log event and sample prediction |
| AWS Well-Architected Security: data protection | S3 Block Public Access and SSE-KMS for input/output objects | Bucket properties, KMS key configuration, object encryption |
| AWS Well-Architected Reliability: monitoring | Lambda errors/duration/invocations and alert delivery checks | CloudWatch metrics and test results |
| AWS Well-Architected Reliability: failure management | Input validation, bounded inference, alert-only behavior | Unit tests, invalid-input test, failed-input logs |
| AWS Well-Architected Cost Optimization: measure efficiency | Evaluate model value against a baseline and track AWS resource costs | Evaluation output and cost notes |
| CIS AWS Foundations Benchmark: logging/monitoring | CloudTrail/account logging should be enabled according to account policy; Lambda logs retained | Relevant account evidence if in scope |
| CIS AWS Foundations Benchmark: secure configuration | AWS Config recorder/rules and S3 public access protections | Config recorder/rule status and bucket configuration |

## Required control evidence checklist

- IAM role policy: no wildcard administrative permissions; resource scope justified.
- S3 Block Public Access enabled.
- KMS key and key policy reviewed; input/output object encryption verified.
- AWS Config recorder and selected managed rules enabled and evaluated.
- CloudWatch Logs show successful and elevated-risk runs.
- SNS subscription confirmed; test notification received.
- Network controls documented. For baseline no-VPC Lambda, explain why SG chaining does not apply. If a VPC variant is implemented, capture the Lambda SG, endpoint/application SG, inbound reference, routes, and endpoint policy.
- Negative tests demonstrate missing or invalid features fail safely.
- No secrets, account identifiers, sensitive telemetry, or private screenshots committed to the public repository.
