## Data Versioning

- Each generated dataset includes CSV, Parquet, schema, and stats files.
- Fingerprints are computed via SHA256 of all files to produce a deterministic `dataset_id`.
- Uploads store data under `s3://<bucket>/<datasets_prefix>/<dataset_id>/` with a manifest for traceability.
