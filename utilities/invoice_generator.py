"""
Simple invoice generator.
Reads invoice data from CSV or JSON and creates PDF invoices.
"""

import csv
import json
import argparse
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


DEFAULT_SENDER = {
    "name": "Naser Al Jarad",
    "address": "Wormser Stra\u00dfe 57\n68623 Lampertheim",
    "phone": "+49 151 68510435",
}

def load_input(input_path: Path):
    ext = input_path.suffix.lower()
    if ext == '.csv':
        with input_path.open(newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    elif ext == '.json':
        with input_path.open(encoding='utf-8') as f:
            return json.load(f)
    else:
        raise ValueError('Unsupported input format: %s' % input_path)


def load_sender(sender_file: Path | None):
    if sender_file is None:
        return DEFAULT_SENDER
    ext = sender_file.suffix.lower()
    if ext in {'.json', '.yaml', '.yml'}:
        with sender_file.open(encoding='utf-8') as f:
            return json.load(f)
    raise ValueError('Unsupported sender file format: %s' % sender_file)


def read_counter(counter_file: Path, default: int) -> int:
    if counter_file.exists():
        return int(counter_file.read_text().strip())
    return default


def write_counter(counter_file: Path, counter: int):
    counter_file.write_text(str(counter))


def create_invoice_pdf(data: dict, number: str, output_dir: Path, sender: dict):
    filename = output_dir / f"invoice_{number}.pdf"
    c = canvas.Canvas(str(filename), pagesize=A4)

    width, height = A4
    margin = 20 * mm

    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, height - margin, "INVOICE")

    c.setFont("Helvetica", 12)
    c.drawString(margin, height - margin - 30, f"Invoice No.: {number}")
    c.drawString(margin, height - margin - 50, f"Date: {data.get('date', datetime.now().date())}")

    # Sender details on the right
    sender_y = height - margin
    c.drawRightString(width - margin, sender_y - 0, sender.get('name', ''))
    sender_lines = sender.get('address', '').split('\n')
    for i, line in enumerate(sender_lines, 1):
        c.drawRightString(width - margin, sender_y - i * 15, line)
    if sender.get('phone'):
        c.drawRightString(width - margin, sender_y - (len(sender_lines) + 1) * 15, sender['phone'])

    # Recipient details
    c.drawString(margin, height - margin - 90, data.get('name', ''))
    addr = data.get('address', '').split('\n')
    for i, line in enumerate(addr):
        c.drawString(margin, height - margin - 110 - i*15, line)

    # Description and price
    c.drawString(margin, height - margin - 170, "Description:")
    c.drawString(margin + 100, height - margin - 170, data.get('description', ''))

    c.drawString(margin, height - margin - 200, "Price:")
    c.drawString(margin + 100, height - margin - 200, str(data.get('price', '')))

    c.line(margin, height - margin - 210, margin + 170, height - margin - 210)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, height - margin - 230, "Total:")
    c.drawString(margin + 100, height - margin - 230, str(data.get('price', '')))

    c.showPage()
    c.save()
    return filename


def main():
    parser = argparse.ArgumentParser(description="Generate PDF invoices from data file")
    parser.add_argument('input', type=Path, help='Path to CSV or JSON file containing invoices')
    parser.add_argument('--output-dir', type=Path, default=Path('invoices'), help='Directory to save PDF invoices')
    parser.add_argument('--counter-file', type=Path, default=Path('invoice_counter.txt'), help='File to store last invoice number')
    parser.add_argument('--prefix', type=str, default=datetime.now().year, help='Invoice number prefix, default current year')
    parser.add_argument('--start', type=int, help='Starting invoice number (overrides stored counter)')
    parser.add_argument('--sender-file', type=Path, help='Optional JSON/YAML file with sender information')

    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    start_counter = args.start if args.start is not None else 1
    counter = read_counter(args.counter_file, start_counter)

    sender = load_sender(args.sender_file)

    data_list = load_input(args.input)

    for entry in data_list:
        number = f"{args.prefix}-{counter:03d}"
        filename = create_invoice_pdf(entry, number, args.output_dir, sender)
        print(f"Created {filename}")
        counter += 1

    write_counter(args.counter_file, counter)


if __name__ == '__main__':
    main()
