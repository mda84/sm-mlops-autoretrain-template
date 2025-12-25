#!/usr/bin/env bash
set -euo pipefail
cd infra/cdk
cdk destroy --all --force
