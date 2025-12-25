## Auto-Retraining Pipeline

1. **Preprocess**: Split dataset into train/val/test.
2. **Train**: PyTorch estimator trains baseline model.
3. **Evaluate**: Processing step computes metrics.
4. **Condition**: Compare against configurable threshold.
5. **Register**: Successful models are registered in the Model Package Group.

EventBridge or Lambda can trigger executions on schedules or new dataset arrivals.
