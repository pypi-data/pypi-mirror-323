"""
This script is used to process pdf files in a folder and save the transactions in a csv file.
"""

import os
import argparse
from .process_transaction import process_transaction


def main():
    """Main function"""
    parser = argparse.ArgumentParser()
    parser.add_argument("input_folder", type=str, help="Folder containing pdf files")
    parser.add_argument("output_file", type=str, help="csv file to save transactions")
    parser.add_argument(
        "--password", type=str, help="Password to open pdf files", default=""
    )
    parser.add_argument(
        "--dataset_folder",
        type=str,
        help="Folder containing dataset",
        default="dataset",
    )
    args = parser.parse_args()
    password = os.environ.get("PDF_PASSWORD", args.password)
    process_transaction(
        args.input_folder, args.output_file, password, args.dataset_folder
    )


if __name__ == "__main__":
    main()
