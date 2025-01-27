"""
Process transaction data from PDF files
"""
import os
import csv
from multiprocessing import Pool
from datetime import datetime
from .common.pdf_convert_txt import pdf_to_text
from .common.txt_convert_csv import txt_to_csv
from .common.utils import DockerSafeLogger

log = DockerSafeLogger().logger

# "Posting Date","Transaction Date","Description","Amount"
# "07/08","06/08","PSS PERSIARAN APEC SEPANG        MY","64.46"

def process_single_csv(csv_path):
    """Process individual CSV files and return parsed data"""
    content = []
    with open(csv_path, 'r') as f:
        csv_reader = csv.reader(f)
        for i, row in enumerate(csv_reader):
            if i == 0:  # Skip header
                continue
            content.append(row)
    filename = os.path.basename(csv_path)
    return (filename.split('-')[0], content)

def process_single_report_data(report_date, data):
    year = datetime.strptime(report_date, '%Y%m%d').year
    modified_data = []
    for row in data:
        modified_data.append([
            f'{row[0]}/{year}',  # Posting Date
            f'{row[1]}/{year}',  # Transaction Date
            row[2],  # Description
            row[3],  # Amount
        ])
    return modified_data

def process_transaction(input_folder, output_file, password, dataset_folder):
    """Process transaction data from PDF files"""
    dataset = {}
    txt_folder = f'{dataset_folder}/txt'
    csv_folder = f'{dataset_folder}/csv'

    pdf_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) 
                 if f.lower().endswith('.pdf')]
    
    txt_files = [os.path.join(txt_folder, f'{os.path.splitext(f)[0]}.txt') for f in os.listdir(input_folder) 
                 if f.lower().endswith('.pdf')]
    
    csv_files = [os.path.join(csv_folder, f'{str(os.path.splitext(f)[0]).split("_")[-1]}-{str(os.path.splitext(f)[0]).split("_")[0]}.csv')
                 for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]

    with Pool() as pool:
        pool.starmap(pdf_to_text, [(pdf, txt, password) for pdf, txt in zip(pdf_files, txt_files)])
    with Pool() as pool:
        pool.starmap(txt_to_csv, [(txt, csv) for txt, csv in zip(txt_files, csv_files)])
    with Pool() as pool:
        results = pool.map(process_single_csv, csv_files)
        for key, content in results:
            dataset[key] = content
    
    log.info(f"processed {len(pdf_files)} pdf files")

    with Pool() as pool:
        processed = pool.starmap(process_single_report_data, [(report_date, data) for report_date, data in dataset.items()])
    
    final_csv = []
    for data in processed:
        final_csv.extend(data)
    log.info(f"processed {len(final_csv)} transactions")
    
    final_csv = sorted(final_csv, key=lambda x: datetime.strptime(x[1], '%d/%m/%Y'))
    final_csv.insert(0, ["Posting Date", "Transaction Date", "Description", "Amount"])
    with open(output_file, 'w', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(final_csv)
        log.info(f"saved processed data to {output_file}")