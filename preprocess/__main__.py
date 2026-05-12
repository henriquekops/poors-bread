import argparse
from pathlib import Path

from converter import convert_xlsx_to_csv
from processor import process

__PARENT = Path(__file__).parent.parent
__INPUT_PATH = f"{__PARENT}/data/input/LEM"
__OUTPUT_PATH = f"{__PARENT}/data/output"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--convert", action="store_true")
    parser.add_argument("--process", action="store_true")

    args = parser.parse_args()

    if args.convert:
        convert_xlsx_to_csv(input_path=__INPUT_PATH, output_path=__OUTPUT_PATH)
    if args.process:
        process(input_path=__INPUT_PATH, output_path=__OUTPUT_PATH)
