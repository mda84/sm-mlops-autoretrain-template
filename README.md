## sm-mlops-autoretrain-template

Production-ready template demonstrating end-to-end ML + MLOps on AWS SageMaker with auto-retraining and AutoPilot support.

### Features
- Dummy tabular data generation with deterministic dataset IDs and stats.
- Local PyTorch baseline training and evaluation.
- Dataset versioning and S3 storage helpers.
- SageMaker Pipelines for preprocess → train → eval → conditional register.
- AutoPilot workflow for automated model search and registration.
- AWS CDK stacks for S3, IAM, EventBridge, Lambda, and SageMaker assets.
- Typer-based CLI to orchestrate local and AWS flows.
- Notebooks, docs, scripts, and tests for quick onboarding.

### Quickstart
```bash
make install
cp .env.example .env
python -m src.cli.main gen-data --problem-type classification --n-rows 1000 --out data/generated
python -m src.cli.main train-local --dataset-dir data/generated --problem-type classification --epochs 1
```

### Tests
```
make test
```

See `docs/` for architecture and workflow details.
