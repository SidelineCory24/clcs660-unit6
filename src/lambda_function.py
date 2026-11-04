"""Scheduled AWS Lambda inference: read latest synthetic/operational metrics and alert."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import boto3

from src.model_runtime import predict_failure_risk

# Created at import time so warm invocations reuse the clients and their connections.
s3 = boto3.client("s3")
sns = boto3.client("sns")


def handler(event, context):
    """Load the model and latest metrics from S3; publish only elevated-risk alerts."""
    # Required settings raise KeyError if missing, surfacing a deployment error immediately.
    bucket = os.environ["DATA_BUCKET"]
    input_key = os.environ.get("INPUT_KEY", "latest_metrics.json")
    # The model ships inside the deployment package (see infrastructure/function/).
    model_path = Path(__file__).resolve().parent.parent / "model" / "model.json"
    model = json.loads(model_path.read_text(encoding="utf-8"))

    # Input is expected to be synthetic metrics JSON; invalid content raises ValueError,
    # failing the invocation so the Errors alarm fires instead of producing a prediction.
    payload = s3.get_object(Bucket=bucket, Key=input_key)
    record = json.loads(payload["Body"].read().decode("utf-8"))
    # The deployed RISK_THRESHOLD parameter overrides the value baked into the model file.
    model["risk_threshold"] = float(os.environ.get("RISK_THRESHOLD", model.get("risk_threshold", 0.65)))
    prediction = predict_failure_risk(record, model)

    result = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "input_key": input_key,
        **prediction,
    }

    # Overwritten each run; bucket versioning retains history for the lifecycle window.
    output_key = "predictions/latest_prediction.json"
    s3.put_object(
        Bucket=bucket,
        Key=output_key,
        Body=(json.dumps(result, indent=2) + "\n").encode("utf-8"),
        ContentType="application/json",
        # Explicit SSE-KMS keeps the object encrypted with the project key, not just the bucket default.
        ServerSideEncryption="aws:kms",
        SSEKMSKeyId=os.environ["KMS_KEY_ARN"],
    )

    # Alert-only: notify an operator but never change infrastructure. NORMAL runs stay quiet.
    if prediction["risk_level"] == "ELEVATED":
        sns.publish(
            TopicArn=os.environ["ALERT_TOPIC_ARN"],
            Subject="Predictive maintenance: elevated risk detected",
            Message=json.dumps(result, indent=2),
        )

    # stdout is captured by CloudWatch Logs as the audit record of each run.
    print(json.dumps(result))
    return {"statusCode": 200, "body": json.dumps(result)}
