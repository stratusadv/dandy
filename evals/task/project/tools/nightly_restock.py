from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from stockroom.data import load_items, save_items
from stockroom.ops import add_stock, sku_total

LOW_THRESHOLD = 5
RESTOCK_UNITS = 10


def restock(items):
    for sku in sorted({item.sku for item in items}):
        total = sku_total(items, sku)
        if not 0 < total <= LOW_THRESHOLD:
            continue
        stocked = [item for item in items if item.sku == sku and item.count > 0]
        location = min(item.location for item in stocked)
        reference = next(item for item in items if item.sku == sku)
        add_stock(items, sku, reference.name, location, RESTOCK_UNITS, reference.unit_price)
        print(f'restocked {sku} +{RESTOCK_UNITS}')


def main(argv=None):
    parser = argparse.ArgumentParser(prog='nightly_restock')
    parser.add_argument('--file', default='inventory.json')
    args = parser.parse_args(argv)
    items = load_items(args.file)
    restock(items)
    save_items(args.file, items)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
