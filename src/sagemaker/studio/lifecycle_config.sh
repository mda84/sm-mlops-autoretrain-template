#!/bin/bash
set -e
echo "Bootstrapping SageMaker Studio environment"
pip install --quiet -r /home/sagemaker-user/requirements.txt
