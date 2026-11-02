#!/usr/bin/env python3
"""Print the files, columns, class counts and unique rows of a folder of CICIoV2024 CSV files.

Usage: python scripts/inspect_dataset.py data/CICIoV2024
"""

import argparse
import os

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder")
    folder = parser.parse_args().folder

    frames = []
    for f in sorted(os.listdir(folder)):
        if f.endswith(".csv"):
            df = pd.read_csv(os.path.join(folder, f))
            print(f, df.shape, list(df.columns))
            frames.append(df)
    all_df = pd.concat(frames, ignore_index=True)
    print("\nTotal rows:", len(all_df))
    print(all_df["label"].value_counts())
    feat = [c for c in all_df.columns if c.lower() not in ("label", "category", "specific_class")]
    print("\nFeature columns:", feat)
    print("Unique rows after removing duplicates:", len(all_df[feat + ["label"]].drop_duplicates()))


if __name__ == "__main__":
    main()
