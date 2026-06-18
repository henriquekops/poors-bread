import os
import sys
import argparse
import subprocess
from pathlib import Path

from bread.preprocess.converter import convert_xlsx_to_csv
from bread.preprocess.processor import process

__PARENT = Path(__file__).parent.parent
__INPUT_PATH = f"{__PARENT}/data/input/LEM"
__OUTPUT_PATH = f"{__PARENT}/data/output"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=False)

    group.add_argument("--convert", action="store_true", help="convert xlsx files to csv")
    group.add_argument("--process", action="store_true", help="process csv files")
    group.add_argument("--dash", action="store_true", help="display dashboard")

    args = parser.parse_args()

    if args.convert:
        convert_xlsx_to_csv(input_path=__INPUT_PATH, output_path=__OUTPUT_PATH)
    elif args.process:
        process(input_path=__INPUT_PATH, output_path=__OUTPUT_PATH)
    elif args.dash:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "bread/dashboard/dashboard.py"])
        sys.exit(0)
