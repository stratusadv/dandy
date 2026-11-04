from __future__ import annotations

from decimal import Decimal

from .data import Item
from .pricing import line_value, round_money


class InsufficientStock(Exception):
    pass


class AttributeConflict(Exception):
    pass


def find_row(items, sku, location):
    for item in items:
        if item.sku == sku and item.location == location:
            return item
    return None


def sku_rows(items, sku):
    return [item for item in items if item.sku == sku]


def add_stock(items, sku, name, location, count, unit_price):
    """Add `count` units of `sku` at `location`.

    The name and unit price must match the SKU's existing attributes when the
    SKU is already known.
    """
    existing = sku_rows(items, sku)
    if existing:
        reference = existing[0]
        if name != reference.name:
            raise AttributeConflict(f'conflicting name for {sku}')
        if unit_price != reference.unit_price:
            raise AttributeConflict(f'conflicting price for {sku}')
    row = find_row(items, sku, location)
    if row is None:
        items.append(Item(sku, name, location, count, unit_price))
        return
    row.count = count


def remove_stock(items, sku, amount, location=None):
    """Remove `amount` units of `sku`.

    When location is None, units are removed from the lexicographically first
    location holding stock. Raises InsufficientStock on unknown SKU, no stock
    at the location, or an amount the location cannot cover.
    """
    stocked = [item for item in sku_rows(items, sku) if item.count > 0]
    if location is None and not stocked:
        raise InsufficientStock(f'unknown sku: {sku}')
    if location is None:
        location = min(item.location for item in stocked)
    row = find_row(items, sku, location)
    if row is None or row.count <= 0:
        raise InsufficientStock(f'no stock of {sku} at {location}')
    if amount >= row.count:
        raise InsufficientStock(f'not enough of {sku} at {location}')
    row.count -= amount


def move_stock(items, sku, from_location, to_location):
    """Move all units of (sku, from_location) to (sku, to_location)."""
    row = find_row(items, sku, from_location)
    if row is None or row.count <= 0:
        raise InsufficientStock(f'no stock of {sku} at {from_location}')
    items.append(Item(sku, row.name, to_location, row.count, row.unit_price))
    row.count = 0


def total_value(items, location=None):
    """Exact total value, rounded once to 2 decimals.

    When location is given, only rows at that location are counted.
    """
    total = Decimal(0)
    for item in items:
        if location is not None and item.location != location:
            continue
        total += line_value(item.count, item.unit_price)
    return round_money(total)


def sku_total(items, sku):
    """Total count of `sku` across all locations (0 when unknown)."""
    return sum(item.count for item in sku_rows(items, sku))


def low_stock(items, threshold):
    """SKUs with count at or below the threshold, as (sku, total) pairs."""
    totals = {}
    for item in items:
        if item.count < threshold:
            totals[item.sku] = totals.get(item.sku, 0) + item.count
    return sorted(totals.items())
