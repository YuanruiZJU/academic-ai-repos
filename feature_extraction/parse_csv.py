import csv


def parse_csv(file_path, field_names):
    row_dicts = list()
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        field_names = reader.fieldnames
        for row in reader:
            pass

