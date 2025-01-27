# maybankforme
This projects converts maybank credit card statement pdf files to a single csv file that allows to be ingestable in other workflow.

# Usage

## Python module

TBD

## Docker (Recommended)

```bash
docker run zhrif/maybankforme -h
usage: maybankforme [-h] [--password PASSWORD]
                    [--dataset_folder DATASET_FOLDER]
                    input_folder output_file

positional arguments:
  input_folder          Folder containing pdf files
  output_file           csv file to save transactions

options:
  -h, --help            show this help message and exit
  --password PASSWORD   Password to open pdf files
  --dataset_folder DATASET_FOLDER
                        Folder containing dataset
```

```bash
docker pull ghcr.io/zhrif/maybankforme
docker run -v dataset:/dataset ghcr.io/zhrif/maybankforme /dataset/pdf /dataset/Output.csv --password=<REDACTED> --dataset_folder /dataset
```
