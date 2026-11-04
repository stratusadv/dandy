from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Item:
    sku: str
    name: str
    location: str
    count: int
    unit_price: float


def load_items(path) -> list[Item]:
    p = Path(path)
    if not p.exists():
        return []
    with open(p) as f:
        raw = json.load(f)
    return [Item(**row) for row in raw]


def save_items(path, items: list[Item]) -> None:
    rows = [
        item.__dict__ for item in sorted(items, key=lambda i: (i.sku, i.location)) if item.count > 0
    ]
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w') as f:
        json.dump(rows, f, indent=2)
        f.write('\n')
