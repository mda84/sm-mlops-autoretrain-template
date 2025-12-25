import os
import pandas as pd
from sklearn.model_selection import train_test_split


def main():
    input_path = "/opt/ml/processing/input"
    df = pd.read_csv(os.path.join(input_path, "data.csv"))
    train_df, temp_df = train_test_split(df, test_size=0.3, random_state=42, stratify=df["label"] if "label" in df else None)
    val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42, stratify=temp_df["label"] if "label" in temp_df else None)

    os.makedirs("/opt/ml/processing/output/train", exist_ok=True)
    os.makedirs("/opt/ml/processing/output/val", exist_ok=True)
    os.makedirs("/opt/ml/processing/output/test", exist_ok=True)

    train_df.to_csv("/opt/ml/processing/output/train/train.csv", index=False)
    val_df.to_csv("/opt/ml/processing/output/val/val.csv", index=False)
    test_df.to_csv("/opt/ml/processing/output/test/test.csv", index=False)


if __name__ == "__main__":
    main()
