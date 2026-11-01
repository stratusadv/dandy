from __future__ import annotations

from .data import Item


class InsufficientStock(Exception):
    pass


def find_item(items, sku):
    for item in items:
        if item.sku == sku:
            return item
    return None


def add_stock(items, sku, name, location, count, unit_price):
    """Add stock for a SKU.

    If the SKU already exists, merge: count is summed with the new amount
    and location/unit_price are updated to the new values.
    """
    existing = find_item(items, sku)
    if existing is None:
        items.append(Item(sku, name, location, count, unit_price))
        return
    existing.count += count
    existing.location = location
    existing.unit_price = unit_price


def remove_stock(items, sku, amount):
    """Remove `amount` units of a SKU.

    Allowed when amount <= the current count; the count may reach exactly 0.
    Raises InsufficientStock on unknown SKU or when amount > current count
    (no mutation in that case).
    """
    item = find_item(items, sku)
    if item is None:
        raise InsufficientStock(f'unknown sku: {sku}')
    if amount > item.count:
        raise InsufficientStock(f'not enough of {sku}')
    item.count -= amount


def move_stock(items, sku, to_location):
    """Move all units of a SKU to a new location. The count is unchanged."""
    item = find_item(items, sku)
    if item is None:
        raise InsufficientStock(f'unknown sku: {sku}')
    item.location = to_location


def total_value(items, location=None):
    """Sum of count * unit_price, rounded to 2 decimals.

    When location is given, only items at that location are counted.
    """
    total = 0.0
    for item in items:
        if location is not None and item.location != location:
            continue
        total += item.count * item.unit_price
    return round(total, 2)


def low_stock(items, threshold):
    """Items with count at or below the threshold, sorted by sku."""
    return sorted(
        (item for item in items if item.count <= threshold),
        key=lambda item: item.sku,
    )
