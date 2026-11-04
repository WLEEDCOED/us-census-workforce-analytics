"""
US Census Workforce Income — data downloader.

Downloads the REAL UCI "Adult" (Census Income) dataset (1994 US Census data,
donors Ronny Kohavi & Barry Becker), extracts it, cleans it, and saves the
combined train+test table to data/adult_census.csv.

Source: https://archive.ics.uci.edu/dataset/2/adult
Direct archive: https://archive.ics.uci.edu/static/public/2/adult.zip

Cleaning applied (documented):
  - adult.data / adult.test are comma-separated WITHOUT headers; the column
    names are assigned here in the documented UCI column order.
  - All string fields are stripped of leading/trailing whitespace.
  - '?' values are treated as missing (kept as-is in the CSV; they are the
    dataset's native missing-value marker).
  - The adult.test file carries a one-line header ("|1x3 Cross validator")
    and trailing periods on the income labels (">50K." / "<=50K."):
    the header line is skipped and the periods are stripped so the income
    column is consistent across train and test.
"""
import io
import os
import urllib.request
import zipfile

import pandas as pd

URL = "https://archive.ics.uci.edu/static/public/2/adult.zip"
BASE_DIR = os.path.dirname(__file__)
OUT_PATH = os.path.join(BASE_DIR, "data", "adult_census.csv")

COLUMNS = [
    "age",
    "workclass",
    "fnlwgt",
    "education",
    "education-num",
    "marital-status",
    "occupation",
    "relationship",
    "race",
    "sex",
    "capital-gain",
    "capital-loss",
    "hours-per-week",
    "native-country",
    "income",
]


def _read_frame(path: str, skip_header_line: bool) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        header=None,
        names=COLUMNS,
        skipinitialspace=True,
        skiprows=1 if skip_header_line else 0,
        na_filter=False,
    )
    return df


def clean_frame(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()
    # adult.test income labels carry a trailing period ("<=50K." / ">50K.")
    df["income"] = df["income"].str.rstrip(".")
    # numeric columns: force numeric, '?' -> NaN
    for col in ["age", "fnlwgt", "education-num", "capital-gain",
                "capital-loss", "hours-per-week"]:
        df[col] = pd.to_numeric(df[col].replace("?", pd.NA), errors="coerce")
    return df


def main() -> None:
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    print(f"Downloading {URL} ...")
    with urllib.request.urlopen(URL, timeout=120) as resp:
        payload = resp.read()
    print(f"Downloaded {len(payload):,} bytes")

    tmp_dir = os.path.join(BASE_DIR, "data", "_adult_raw")
    os.makedirs(tmp_dir, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        zf.extractall(tmp_dir)

    train = clean_frame(_read_frame(os.path.join(tmp_dir, "adult.data"), False))
    test = clean_frame(_read_frame(os.path.join(tmp_dir, "adult.test"), True))
    df = pd.concat([train, test], ignore_index=True)

    df.to_csv(OUT_PATH, index=False)
    print(f"Saved {OUT_PATH} — {len(df):,} rows, {df.shape[1]} columns")
    print(f"  >50K rate: {(df['income'] == '>50K').mean():.2%}")
    print(f"  '?' markers kept as-is in workclass/occupation/native-country")


if __name__ == "__main__":
    main()
