# Lambda deployment package

This directory is the isolated AWS Lambda source package. It intentionally contains only the inference runtime and exported model, not scikit-learn training dependencies. After retraining locally, copy `model/model.json` from the repository root into `infrastructure/function/model/model.json` before building with SAM.
