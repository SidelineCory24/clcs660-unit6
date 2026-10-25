"""Scheduled AWS Lambda inference: read latest synthetic/operational metrics and alert."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import boto3

from src.model_runtime import predict_failure_risk

s3 = boto3.client("s3")
sns = boto3.client("sns")


def handler(event, context):
    """Load the model and latest metrics from S3; publish only elevated-risk alerts."""
    bucket = os.environ["DATA_BUCKET"]
    input_key = os.environ.get("INPUT_KEY", "latest_metrics.json")
    model_path = Path(__file__).resolve().parent.parent / "model" / "model.json"
    model = json.loads(model_path.read_text(encoding="utf-8"))

    payload = s3.get_object(Bucket=bucket, Key=input_key)
    record = json.loads(payload["Body"].read().decode("utf-8"))
    model["risk_threshold"] = float(os.environ.get("RISK_THRESHOLD", model.get("risk_threshold", 0.65)))
    prediction = predict_failure_risk(record, model)

    result = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "input_key": input_key,
        **prediction,
    }

    output_key = "predictions/latest_prediction.json"
    s3.put_object(
        Bucket=bucket,
        Key=output_key,
        Body=(json.dumps(result, indent=2) + "\n").encode("utf-8"),
        ContentType="application/json",
        ServerSideEncryption="aws:kms",
        SSEKMSKeyId=os.environ["KMS_KEY_ARN"],
    )

    if prediction["risk_level"] == "ELEVATED":
        sns.publish(
            TopicArn=os.environ["ALERT_TOPIC_ARN"],
            Subject="Predictive maintenance: elevated risk detected",
            Message=json.dumps(result, indent=2),
        )

    print(json.dumps(result))
    return {"statusCode": 200, "body": json.dumps(result)}
