import re
from pathlib import Path

import numpy as np
import pandas as pd


def clean_lem_df(df: pd.DataFrame, year: str, filename: str) -> pd.DataFrame:
    """Transforms a single LEM into a standardized long-format DataFrame."""
    months_list = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]

    # Dynamic month column detection (handles varying header positions)
    month_cols = {}

    for _, row in df.iterrows():
        found_months = {}
        
        for i, val in enumerate(row):
            cleaned_val = str(val).strip().upper()
            
            if cleaned_val in months_list:
                found_months[i] = cleaned_val
                
        # If we found at least 3 months in this row, save them and stop searching
        if len(found_months) >= 3:
            month_cols = found_months
            break

    # Area mapping to standardize categories and handle accents/case
    area_mapping = {
        "DESDOBRAMENTOS TÉCNICOS": "desdobramentos tecnicos",
        "PROFISSIONALIZAÇÃO": "profissionalizacao",
        "SAÚDE": "saude",
        "EDUCAÇÃO": "educacao",
    }

    data = []
    current_area = None

    # Tracks current "Area" to label subsequent "Types"
    for _, row in df.iterrows():
        first_col_val = str(row[0]).strip() if pd.notna(row[0]) else ""
        first_col_upper = first_col_val.upper()

        # Update active area if a header row is detected
        for keyword, area_name in area_mapping.items():
            if keyword in first_col_upper:
                current_area = area_name
                break

        # Validation: skip empty rows, month headers, or the area header itself
        if not first_col_val or first_col_upper in months_list:
            continue
        if any(keyword in first_col_upper for keyword in area_mapping.keys()):
            continue
        if current_area is None:
            continue

        tipo = first_col_val

        # Converts 'X', empty strings, and commas to valid floats
        for col_idx, month_name in month_cols.items():
            if col_idx >= len(row):
                continue

            valor = row[col_idx]
            try:
                if pd.isna(valor) or str(valor).strip() == "" or str(valor).strip().upper() == "X":
                    val_num = 0.0
                else:
                    val_num = float(str(valor).replace(",", "."))
            except (ValueError, TypeError):
                val_num = 0.0

            data.append(
                {
                    "tipo": tipo,
                    "area": current_area,
                    "mes": month_name,
                    "ano": int(year),
                    "valor": val_num,
                    "arquivo": filename,
                }
            )

    return pd.DataFrame(data)


def load_all_data(data_dir: Path) -> pd.DataFrame:
    """File discovery, skipping partial files and aggregating results."""
    paths = sorted(data_dir.glob("*.xlsx"))
    all_dfs = []

    for file in paths:
        # Ignore files containing '_partial' to ensure data integrity
        if "_partial" in file.name.lower():
            continue

        match = re.search(r"(20\d{2})", file.stem)
        if not match:
            continue

        year = match.group(1)
        try:
            # Load raw data without headers to allow manual structure parsing
            raw_df = pd.read_excel(file, header=None)
            cleaned_df = clean_lem_df(raw_df, year, file.name)
            if not cleaned_df.empty:
                all_dfs.append(cleaned_df)
        except Exception as e:
            print(f"Error loading {file.name}: {e}")

    if not all_dfs:
        return pd.DataFrame(columns=["tipo", "area", "mes", "ano", "valor", "arquivo"])

    combined = pd.concat(all_dfs, ignore_index=True)

    # Ensure columns are in the requested order
    cols_order = ["tipo", "area", "mes", "ano", "valor", "arquivo"]
    combined = combined[cols_order]

    return combined


def process(input_path: str, output_path: str) -> None:
    """Start preprocessing pipeline."""
    input_dir = Path(input_path)
    output_dir = Path(output_path)

    if not input_dir.exists():
        print(f"Input directory {input_path} does not exist.")
        return

    df = load_all_data(input_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "processed.csv"
    df.to_csv(output_file, index=False)

    print(f"Pipeline complete: {len(df)} rows saved to {output_file}")
