"""Generate the stockroom v2 seed: 150 legacy-format rows with boundary and
rounding traps. Run from the repo root:  .venv/bin/python evals/task/generate_seed.py

The seed is deterministic; regenerate only to tweak the trap layout.
"""

from __future__ import annotations

import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

WORDS = ['Alder', 'Birch', 'Cedar', 'Elm', 'Fir', 'Gumwood', 'Iroko', 'Juniper', 'Larch', 'Maple']
PARTS = ['Part', 'Panel', 'Bracket', 'Housing', 'Gasket']
LOCATIONS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D1']
CALIBRATION_SKU = 'C-048'
CALIBRATION_PRICE = 2.145


def make_row(prefix, n, i):
    name = f'{WORDS[i % 10]} {PARTS[(i * 7) % 5]} {n:03d}'
    cents = 111 + (i * 17) % 500
    return {
        'sku': f'{prefix}-{n:03d}',
        'name': name,
        'location': LOCATIONS[i % 7],
        'count': 4 + (i % 3),
        'unit_price': cents / 100,
    }


def line_value(row):
    return row['count'] * Decimal(str(row['unit_price']))


def main():
    rows = []
    i = 0
    for prefix, last in (('A', 50), ('B', 50), ('C', 47)):
        for n in range(1, last + 1):
            rows.append(make_row(prefix, n, i))
            i += 1
    rows.append(make_row('C', 48, i))
    i += 1
    rows.append(
        {
            'sku': 'T-001',
            'name': 'Walnut Trap 001',
            'location': 'T1',
            'count': 5,
            'unit_price': 0.035,
        }
    )
    rows.append(
        {
            'sku': 'T-002',
            'name': 'Walnut Trap 002',
            'location': 'T2',
            'count': 3,
            'unit_price': 0.025,
        }
    )
    assert len(rows) == 150

    calibration = next(row for row in rows if row['sku'] == CALIBRATION_SKU)
    base_total = sum(line_value(row) for row in rows if row['sku'] != CALIBRATION_SKU)
    assert base_total % Decimal('0.01') == 0
    chosen = None
    for count in range(1, 50, 2):
        total = base_total + count * Decimal(str(CALIBRATION_PRICE))
        if total % Decimal('0.01') != Decimal('0.005'):
            continue
        half_up = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if Decimal(str(round(float(total), 2))) != half_up:
            chosen = count
            break
    assert chosen is not None, 'no calibration count separates float round from half-up'
    calibration['unit_price'] = CALIBRATION_PRICE
    calibration['count'] = chosen

    rows.sort(key=lambda row: row['sku'])
    out = Path(__file__).resolve().parent / 'project' / 'seed.json'
    with open(out, 'w') as f:
        json.dump(rows, f, indent=2)
        f.write('\n')

    exact = sum(line_value(row) for row in rows)
    half_up = exact.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    buggy = round(float(exact), 2)
    low = sum(1 for row in rows if row['count'] <= 5)
    print(f'wrote {out} ({len(rows)} rows)')
    print(f'calibration {CALIBRATION_SKU}: count={chosen} price={CALIBRATION_PRICE}')
    print(f'exact total={exact} half_up={half_up} buggy_float={buggy}')
    print(f'low(<=5) skus={low}, total_units={sum(r["count"] for r in rows)}')


if __name__ == '__main__':
    main()
