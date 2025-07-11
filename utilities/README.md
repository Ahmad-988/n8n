# Invoice Generator Utility

This folder contains a small Python script that generates simple PDF invoices from a CSV or JSON input file. Invoices are numbered sequentially and saved in the specified output directory.

## Usage

```bash
python3 invoice_generator.py utilities/sample_invoices.csv --prefix 2025 --output-dir invoices
```

The sample CSV file demonstrates the expected format. Use `--sender-file` to supply a JSON or YAML file with sender information. Otherwise, a default address is used.
