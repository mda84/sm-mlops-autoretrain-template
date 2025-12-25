FROM public.ecr.aws/docker/library/python:3.11-slim

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /workspace/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && pip install jupyterlab

COPY . /workspace

ENV PYTHONPATH="/workspace"

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser", "--allow-root"]
