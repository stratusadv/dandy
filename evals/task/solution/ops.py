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
    row.count += count


def remove_stock(items, sku, amount, location=None):
    """Remove `amount` units of `sku`.

    When location is None, units are removed from the lexicographically first
    location holding stock. The count may reach exactly 0. Raises
    InsufficientStock on unknown SKU, no stock at the location, or an amount
    the location cannot cover.
    """
    stocked = [item for item in sku_rows(items, sku) if item.count > 0]
    if location is None and not stocked:
        raise InsufficientStock(f'unknown sku: {sku}')
    if location is None:
        location = min(item.location for item in stocked)
    row = find_row(items, sku, location)
    if row is None or row.count <= 0:
        raise InsufficientStock(f'no stock of {sku} at {location}')
    if amount > row.count:
        raise InsufficientStock(f'not enough of {sku} at {location}')
    row.count -= amount


def move_stock(items, sku, from_location, to_location):
    """Move all units of (sku, from_location) into (sku, to_location),
    merging into an existing to row.
    """
    row = find_row(items, sku, from_location)
    if row is None or row.count <= 0:
        raise InsufficientStock(f'no stock of {sku} at {from_location}')
    target = find_row(items, sku, to_location)
    if target is None:
        items.append(Item(sku, row.name, to_location, row.count, row.unit_price))
    else:
        target.count += row.count
    row.count = 0


def transfer_stock(items, sku, from_location, to_location, count):
    """Move exactly `count` units from (sku, from_location) into
    (sku, to_location), creating the to row when needed.
    """
    source = find_row(items, sku, from_location)
    if source is None or source.count <= 0:
        raise InsufficientStock(f'no stock of {sku} at {from_location}')
    if count > source.count:
        raise InsufficientStock(f'not enough of {sku} at {from_location}')
    target = find_row(items, sku, to_location)
    if target is None:
        items.append(Item(sku, source.name, to_location, count, source.unit_price))
    else:
        target.count += count
    source.count -= count


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
    """SKUs whose total count is at or below the threshold, as (sku, total)
    pairs sorted by sku.
    """
    totals = {}
    for item in items:
        totals[item.sku] = totals.get(item.sku, 0) + item.count
    return sorted((sku, total) for sku, total in totals.items() if total <= threshold)


def summary(items):
    """The dict printed by the `summary` command."""
    skus = {item.sku for item in items}
    return {
        'low_stock_count': len(low_stock(items, 5)),
        'total_skus': len(skus),
        'total_units': sum(item.count for item in items),
        'total_value': float(total_value(items)),
    }


def report(items):
    """The dict printed by the `report` command, keyed by location."""
    by_location = {}
    for item in items:
        by_location.setdefault(item.location, []).append(item)
    out = {}
    for location in sorted(by_location):
        rows = by_location[location]
        out[location] = {
            'skus': len({row.sku for row in rows}),
            'units': sum(row.count for row in rows),
            'value': float(total_value(rows)),
        }
    return out


def validate_items(items):
    """Violation reason strings for the `validate` command, in spec order."""
    problems = []
    first_seen = {}
    for index, item in enumerate(items):
        if item.sku == '':
            problems.append(f'row {index} has empty sku')
        if item.name == '':
            problems.append(f'row {index} has empty name')
        if item.location == '':
            problems.append(f'row {index} has empty location')
        if item.count < 0:
            problems.append(f'row {index} has negative count')
        if item.unit_price <= 0:
            problems.append(f'row {index} has non-positive price')
        key = (item.sku, item.location)
        if key in first_seen:
            problems.append(f'row {index} duplicates (sku, location) of row {first_seen[key]}')
        else:
            first_seen[key] = index
    order = []
    names = {}
    prices = {}
    for item in items:
        if item.sku == '':
            continue
        if item.sku not in names:
            order.append(item.sku)
            names[item.sku] = set()
            prices[item.sku] = set()
        names[item.sku].add(item.name)
        prices[item.sku].add(item.unit_price)
    for sku in order:
        if len(names[sku]) > 1:
            problems.append(f'sku {sku} has inconsistent name')
        if len(prices[sku]) > 1:
            problems.append(f'sku {sku} has inconsistent price')
    return problems
