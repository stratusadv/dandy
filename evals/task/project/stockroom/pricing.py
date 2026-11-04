from __future__ import annotations

from decimal import Decimal


def line_value(count, unit_price):
    """Exact value of `count` units at `unit_price` dollars."""
    return Decimal(count) * Decimal(str(unit_price))


def round_money(value):
    """Round a money value to 2 decimals."""
    return Decimal(str(round(float(value), 2)))


def format_money(value):
    """Format a money value with exactly 2 decimals."""
    return f'{value:.2f}'
