#!/usr/bin/env bash
set -euo pipefail
aws configure list
cd infra/cdk
pip install -r requirements.txt
cdk bootstrap
