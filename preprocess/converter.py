import os
from pathlib import Path

import pandas as pd

__PARENT = Path(__file__).parent.parent
__INPUT_PATH = f"{__PARENT}/data/input/LEM"
__OUTPUT_PATH = f"{__PARENT}/data/output"


def convert_xlsx_to_csv():
    os.makedirs(__OUTPUT_PATH, exist_ok=True)

    for file in os.listdir(__INPUT_PATH):
        input_path = f"{__INPUT_PATH}/{file}"
        df = pd.read_excel(input_path)
        name = Path(file).stem
        output_path = f"{__OUTPUT_PATH}/{name}.csv"
        df.to_csv(output_path, index=False)
        print(f"Converted {input_path} to {output_path}\n")
