from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


def line_value(count, unit_price):
    """Exact value of `count` units at `unit_price` dollars."""
    return Decimal(count) * Decimal(str(unit_price))


def round_money(value):
    """Round a money value to 2 decimals, half up."""
    return Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def format_money(value):
    """Format a money value with exactly 2 decimals."""
    return f'{value:.2f}'
