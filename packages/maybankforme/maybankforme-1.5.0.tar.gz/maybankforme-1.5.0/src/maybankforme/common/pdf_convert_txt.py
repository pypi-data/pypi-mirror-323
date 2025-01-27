"""
Convert PDF files to text files
"""
import os
import argparse
from pypdf import PdfReader
from .utils import DockerSafeLogger

log = DockerSafeLogger().logger

def pdf_to_text(pdf_path, txt_path, password):
    """Convert PDF file to text file"""
    with open(pdf_path, 'rb') as pdf_file:
        try:
            reader = PdfReader(pdf_file, password=password) if password else PdfReader(pdf_file)
        except Exception as e:
            log.error(f"Failed to open {pdf_path}: {e}")
            return
        text = ""
        for page_num in range(reader.get_num_pages()):
            text += reader.get_page(page_num).extract_text()
        with open(txt_path, 'w') as txt_file:
            txt_file.write(text)
    log.info(f"converted '{pdf_path}' to '{txt_path}'")

def convert_txt_folder(input_folder, output_folder, password):
    """Convert all PDF files in a folder to text files"""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for filename in os.listdir(input_folder):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(input_folder, filename)
            txt_filename = os.path.splitext(filename)[0] + '.txt'
            txt_path = os.path.join(output_folder, txt_filename)
            pdf_to_text(pdf_path, txt_path, password)
            log.info(f"converted '{pdf_path}' to '{txt_path}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert statement pdf files to text files")
    parser.add_argument('input_folder', type=str, help="Folder containing pdf files")
    parser.add_argument('output_folder', type=str, help="Folder to save text files")
    parser.add_argument('--password', type=str, help="Password to open pdf files", default="")
    args = parser.parse_args()
    password = os.environ.get('PDF_PASSWORD', args.password)
    convert_txt_folder(args.input_folder, args.output_folder, password)
