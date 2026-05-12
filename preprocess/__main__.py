import argparse

from converter import convert_xlsx_to_csv

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--convert", action="store_true")

    args = parser.parse_args()

    if args.convert:
        convert_xlsx_to_csv()
