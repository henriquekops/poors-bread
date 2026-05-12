import os
from pathlib import Path

import pandas as pd


def convert_xlsx_to_csv(input_path: str, output_path: str) -> None:
    os.makedirs(output_path, exist_ok=True)

    for file in os.listdir(input_path):
        _input_path = f"{input_path}/{file}"
        df = pd.read_excel(_input_path)
        name = Path(file).stem
        _output_path = f"{output_path}/{name}.csv"
        df.to_csv(_output_path, index=False)
        print(f"Converted {input_path} to {output_path}\n")
