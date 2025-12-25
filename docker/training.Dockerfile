FROM public.ecr.aws/docker/library/python:3.11-slim

WORKDIR /opt/ml/code

RUN apt-get update && apt-get install -y --no-install-recommends build-essential git && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /opt/ml/code/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src /opt/ml/code/src

ENV PYTHONPATH="/opt/ml/code"

ENTRYPOINT ["python", "-m", "src.model.train"]
