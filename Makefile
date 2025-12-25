PYTHON ?= python3
VENV ?= .venv
ACTIVATE = . $(VENV)/bin/activate

.PHONY: install lint test gen-data train-local cdk-deploy cdk-destroy

install:
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE) && pip install -U pip
	$(ACTIVATE) && pip install -r requirements.txt
	$(ACTIVATE) && pip install -e .[dev]

lint:
	$(ACTIVATE) && ruff check .

test:
	$(ACTIVATE) && pytest -q

gen-data:
	$(ACTIVATE) && $(PYTHON) -m src.cli.main gen-data --problem-type classification --n-rows 1000 --out data/generated

train-local:
	$(ACTIVATE) && $(PYTHON) -m src.cli.main train-local --dataset-id local-demo --problem-type classification

cdk-deploy:
	cd infra/cdk && $(ACTIVATE) && cdk deploy --all

cdk-destroy:
	cd infra/cdk && $(ACTIVATE) && cdk destroy --all
