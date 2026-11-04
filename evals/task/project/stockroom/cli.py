from __future__ import annotations

import argparse
import sys

from .data import load_items, save_items
from .ops import (
    AttributeConflict,
    InsufficientStock,
    add_stock,
    low_stock,
    move_stock,
    remove_stock,
    total_value,
)
from .pricing import format_money

DEFAULT_FILE = 'inventory.json'
DEFAULT_LOW_THRESHOLD = 5


def positive_int(text):
    value = int(text)
    if value <= 0:
        raise argparse.ArgumentTypeError('must be a positive integer')
    return value


def non_negative_int(text):
    value = int(text)
    if value < 0:
        raise argparse.ArgumentTypeError('must be a non-negative integer')
    return value


def positive_float(text):
    value = float(text)
    if value <= 0:
        raise argparse.ArgumentTypeError('must be a positive number')
    return value


def build_parser():
    parser = argparse.ArgumentParser(prog='stockroom')
    parser.add_argument('--file', default=DEFAULT_FILE)
    sub = parser.add_subparsers(dest='command', required=True)

    p_add = sub.add_parser('add')
    p_add.add_argument('sku')
    p_add.add_argument('name')
    p_add.add_argument('location')
    p_add.add_argument('count', type=positive_int)
    p_add.add_argument('unit_price', type=positive_float)

    p_remove = sub.add_parser('remove')
    p_remove.add_argument('sku')
    p_remove.add_argument('count', type=int)
    p_remove.add_argument('location', nargs='?')

    p_move = sub.add_parser('move')
    p_move.add_argument('sku')
    p_move.add_argument('from_location')
    p_move.add_argument('to_location')

    sub.add_parser('list')

    p_value = sub.add_parser('value')
    p_value.add_argument('location', nargs='?')

    p_low = sub.add_parser('low')
    p_low.add_argument('threshold', type=non_negative_int, nargs='?', default=DEFAULT_LOW_THRESHOLD)

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    items = load_items(args.file)
    try:
        if args.command == 'add':
            add_stock(items, args.sku, args.name, args.location, args.count, args.unit_price)
            save_items(args.file, items)
        elif args.command == 'remove':
            remove_stock(items, args.sku, args.count, args.location)
            save_items(args.file, items)
        elif args.command == 'move':
            move_stock(items, args.sku, args.from_location, args.to_location)
            save_items(args.file, items)
        elif args.command == 'list':
            for item in sorted(items, key=lambda i: (i.sku, i.location)):
                print(
                    f'{item.sku}\t{item.location}\t{item.name}\t{item.count}\t{item.unit_price:.2f}'
                )
        elif args.command == 'value':
            print(format_money(total_value(items, args.location)))
        elif args.command == 'low':
            for sku, total in low_stock(items, args.threshold):
                print(f'{sku}\t{total}')
        return 0
    except (InsufficientStock, AttributeConflict) as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
