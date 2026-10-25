# Evidence Checklist for Submission

Save sanitized screenshots and command outputs under a local `evidence/` directory. Review every artifact before committing anything to a public repository.

1. `01-architecture.png` — final architecture diagram.
2. `02-training-output.txt` — model training completion and dataset size.
3. `03-evaluation-output.txt` — actual held-out metrics and confusion matrix.
4. `04-unit-tests.txt` — complete test run with pass/fail summary.
5. `05-iam-role.png` — Lambda role and scoped permissions.
6. `06-s3-security.png` — Block Public Access and bucket encryption.
7. `07-kms-key.png` — key configuration and key policy overview.
8. `08-config-status.png` — AWS Config recorder and rule evaluation.
9. `09-lambda-cloudwatch.png` — successful invocation and logs.
10. `10-sns-alert.png` — notification evidence with personal details redacted.
11. `11-network-controls.png` — network/SG chain evidence if the VPC variant is actually deployed; otherwise explain the baseline's no-VPC decision.
12. `12-cleanup.txt` — resources deleted or retained and cost-control notes.

Never include AWS access keys, secret keys, session tokens, private keys, or sensitive account data.
