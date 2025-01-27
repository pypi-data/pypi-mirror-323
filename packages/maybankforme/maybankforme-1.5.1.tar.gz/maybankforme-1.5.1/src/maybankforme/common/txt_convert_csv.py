"""
Convert text files to csv files
"""

import os
import argparse
import re
from .utils import DockerSafeLogger

log = DockerSafeLogger().logger


def regex_match_transaction(line):
    """Check if line is a transaction"""
    pattern = r"(\d{2}/\d{2}) (\d{2}/\d{2})(.*)\s(\d{1,3}(?:,\d{3})*\.\d{2})$"
    match = re.match(pattern, line)
    if match:
        return match.groups()
    return None


def regex_match_credit(line):
    """Check if line is a credit transaction"""
    pattern = r"(\d{2}/\d{2}) (\d{2}/\d{2}) (.*)CR"
    match = re.match(pattern, line)
    if match:
        return match.groups()
    return None


def txt_to_csv(txt_path, csv_path):
    """Convert text file to csv file"""
    with open(txt_path, "r") as txt_file:
        lines = txt_file.readlines()
        with open(csv_path, "w") as csv_file:
            csv_file.write('"Posting Date","Transaction Date","Description","Amount"\n')
            for line in lines:
                matches = regex_match_transaction(line.strip())
                if matches:
                    if "RTL MGMT CHRG RATE" in line.strip().upper():
                        continue
                    if regex_match_credit(line):
                        continue
                    temp_line = ""
                    for match in matches:
                        temp_line = temp_line + f'"{match.strip()}",'
                    csv_file.write(f"{temp_line.strip().strip(',')}\n")
    log.info(f"converted '{txt_path}' to '{csv_path}'")


def convert_csv_folder(input_folder, output_folder):
    """Convert all text files in a folder to csv files"""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            txt_path = os.path.join(input_folder, filename)
            csv_filename = f"{str(os.path.splitext(filename)[0]).split('_')[-1]}-{str(os.path.splitext(filename)[0]).split('_')[0]}.csv"
            csv_path = os.path.join(output_folder, csv_filename)
            txt_to_csv(txt_path, csv_path)
            log.info(f"converted '{txt_path}' to '{csv_path}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert statement text files to csv files"
    )
    parser.add_argument("input_folder", type=str, help="Folder containing text files")
    parser.add_argument("output_folder", type=str, help="Folder to save csv files")
    args = parser.parse_args()
    convert_csv_folder(args.input_folder, args.output_folder)
