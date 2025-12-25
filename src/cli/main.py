from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

import typer

from src.common.config import ProjectConfig, load_yaml
from src.data.generate_dummy import generate_dummy_dataset
from src.data.upload_to_s3 import upload_dataset
from src.model.export import export_model_artifacts
from src.model.train import train_model, save_artifacts
from src.sagemaker.autopilot.create_job import create_autopilot_job
from src.sagemaker.autopilot.monitor_job import monitor_job
from src.sagemaker.autopilot.select_best_model import select_best_candidate
from src.sagemaker.pipelines.run_pipeline import start_pipeline_execution, upsert_pipeline

app = typer.Typer(name="mlops", help="MLOps CLI for auto-retrain template")


@app.command("gen-data")
def gen_data(
    problem_type: str = typer.Option("classification", help="classification or regression"),
    n_rows: int = typer.Option(1000, help="Number of rows"),
    out: Path = typer.Option(Path("data/generated"), help="Output directory"),
):
    generate_dummy_dataset(out, n_rows, problem_type)
    typer.echo(f"Generated data at {out}")


@app.command("upload-data")
def upload_data(
    dataset_dir: Path = typer.Option(..., help="Local dataset directory"),
    problem_type: str = typer.Option("classification"),
):
    project = ProjectConfig.load("configs/project.yaml", tags_path="configs/tags.yaml")
    s3_paths = load_yaml("configs/s3_paths.yaml")
    dataset_id = upload_dataset(dataset_dir, project.s3_bucket_name, s3_paths["datasets_prefix"], problem_type)
    typer.echo(f"Uploaded dataset {dataset_id}")


@app.command("train-local")
def train_local(
    dataset_dir: Path = typer.Option(Path("data/generated")),
    problem_type: str = typer.Option("classification"),
    epochs: int = typer.Option(3),
    run_id: Optional[str] = typer.Option(None),
):
    train_csv = dataset_dir / "data.csv"
    val_csv = dataset_dir / "data.csv"
    model, metrics = train_model(train_csv, val_csv, problem_type=problem_type, epochs=epochs)
    save_artifacts(model, metrics, Path("artifacts"))
    typer.echo(f"Training complete metrics={metrics}")


@app.command("export-model")
def export_model(run_id: str = typer.Option("run-default")):
    model_path = Path("artifacts") / run_id / "model.pt"
    export_model_artifacts(model_path, Path("artifacts") / run_id / "export")
    typer.echo("Exported model artifacts")


@app.command("pipeline-upsert")
def pipeline_upsert():
    definition = upsert_pipeline()
    typer.echo(definition)


@app.command("pipeline-run")
def pipeline_run(
    dataset_s3: str = typer.Option(...),
    problem_type: str = typer.Option("classification"),
    metric_threshold: float = typer.Option(0.7),
):
    arn = start_pipeline_execution(dataset_s3, problem_type, metric_threshold)
    typer.echo(arn)


@app.command("autopilot-run")
def autopilot_run(dataset_s3: str = typer.Option(...), problem_type: str = typer.Option("classification")):
    config = load_yaml("configs/autopilot.yaml")
    project = ProjectConfig.load("configs/project.yaml", tags_path="configs/tags.yaml")
    job_name = f"{config['autopilot_job_prefix']}-{problem_type}"
    target_column = config["target_column_classification"] if problem_type == "classification" else config["target_column_regression"]
    create_autopilot_job(
        job_name=job_name,
        s3_uri=dataset_s3,
        target_column=target_column,
        problem_type=problem_type,
        objective_metric=config["objective_metric_name"],
        max_candidates=config["max_candidates"],
        max_runtime_seconds=config["max_runtime_seconds"],
        role_arn=project.sagemaker_execution_role_arn,
        output_path=config.get("output_path", f"s3://{project.s3_bucket_name}/autopilot/{job_name}"),
        region=project.aws_region,
    )
    typer.echo(f"Started AutoPilot job {job_name}")


@app.command("autopilot-monitor")
def autopilot_monitor(job_name: str = typer.Option(...)):
    resp = monitor_job(job_name)
    typer.echo(resp)


@app.command("autopilot-select")
def autopilot_select(job_name: str = typer.Option(...)):
    result = select_best_candidate(job_name)
    typer.echo(result)


@app.command("infra-deploy")
def infra_deploy():
    subprocess.check_call(["cdk", "deploy", "--all"], cwd="infra/cdk")


@app.command("infra-destroy")
def infra_destroy():
    subprocess.check_call(["cdk", "destroy", "--all", "--force"], cwd="infra/cdk")


def main():
    app()


if __name__ == "__main__":
    main()
