import re
from pathlib import Path

import numpy as np
import pandas as pd

data_dir = Path("data/input/LEM")


def clean_lem_df(df: pd.DataFrame, year: str, filename: str) -> pd.DataFrame:
    """Cleans a single LEM report dataframe into a long format. (Categories, months and values as rows instead of columns)"""
    months = [
        "JAN",
        "FEV",
        "MAR",
        "ABR",
        "MAI",
        "JUN",
        "JUL",
        "AGO",
        "SET",
        "OUT",
        "NOV",
        "DEZ",
    ]

    # The first column contains categories/items
    # Row 1 typically contains the month names
    cat_col = df.columns[0]
    header_row = df.iloc[1]
    month_cols = {}
    for i, val in enumerate(header_row):
        val_str = str(val).strip().upper()
        if val_str in months:
            month_cols[df.columns[i]] = val_str

    # If month header not found at row 1, fallback to standard positions (cols 1-12)
    if not month_cols:
        for i, m in enumerate(months):
            if i + 1 < len(df.columns):
                month_cols[df.columns[i + 1]] = m

    # Data starts after the header rows (row 2 onwards)
    df_data = df.iloc[2:].copy()
    df_data = df_data.rename(columns={cat_col: "Category"})
    df_data = df_data.rename(columns=month_cols)

    # Keep only Category and Month columns
    cols_to_keep = ["Category"] + list(month_cols.values())
    df_data = df_data[[c for c in cols_to_keep if c in df_data.columns]]

    # Melt to long format
    available_months = [m for m in months if m in df_data.columns]
    melted = df_data.melt(
        id_vars=["Category"],
        value_vars=available_months,
        var_name="Month",
        value_name="Value",
    )

    # Basic cleaning
    # Filter out empty rows or section headers
    melted["Category"] = melted["Category"].astype(str).str.strip()
    melted = melted[~melted["Category"].isin(["nan", "", "None"])]

    melted["Year"] = int(year)
    melted["Source"] = filename

    # Convert values to numeric, handling 'X', spaces, etc.
    melted["Value"] = pd.to_numeric(
        melted["Value"].replace(["X", " ", "nan"], [0, 0, np.nan]), errors="coerce"
    )

    return melted


def load_all_data(data_dir: Path) -> pd.DataFrame:
    """Loads and combines all LEM files from the data directory."""
    paths = sorted(data_dir.rglob("*.xlsx"))
    all_dfs = []

    for file in paths:
        # Extract year from filename
        match = re.search(r"(20\d{2})", file.stem)
        if not match:
            continue

        year = match.group(1)
        try:
            raw_df = pd.read_excel(file, header=None)
            cleaned_df = clean_lem_df(raw_df, year, file.name)

            # Mark partial files based on filename
            cleaned_df["IsPartial"] = "_partial" in file.name.lower()
            all_dfs.append(cleaned_df)
        except Exception as e:
            print(f"Error loading {file.name}: {e}")

    combined = pd.concat(all_dfs, ignore_index=True)

    # Handle duplicates: Prefer complete files over partial ones
    # Sort so that complete files (IsPartial=False) come last
    combined = combined.sort_values(
        ["Year", "IsPartial", "Source"], ascending=[True, False, True]
    )
    combined = combined.drop_duplicates(
        subset=["Year", "Month", "Category"], keep="last"
    )

    # Month sorting
    month_order = {
        m: i
        for i, m in enumerate(
            [
                "JAN",
                "FEV",
                "MAR",
                "ABR",
                "MAI",
                "JUN",
                "JUL",
                "AGO",
                "SET",
                "OUT",
                "NOV",
                "DEZ",
            ]
        )
    }
    combined["MonthIdx"] = combined["Month"].map(month_order)
    combined = combined.sort_values(["Year", "MonthIdx", "Category"]).drop(
        columns=["MonthIdx", "IsPartial"]
    )

    return combined.reset_index(drop=True)


def process(input_path: str, output_path: str) -> None:
    df = load_all_data(Path(input_path))
    print(len(df))

    df[df["Category"] == "Atendimentos indvidual"].sort_values(["Year", "Month"])

    df.to_csv(f"{output_path}/processed.csv", index=False)
