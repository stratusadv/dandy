from __future__ import annotations


def render(items):
    out = 'STOCKROOM LEGACY REPORT\n'
    out += '======================\n'
    out += 'sku,location,name,count,unit_price,value\n'
    total = 0
    for item in sorted(items, key=lambda i: (i.sku, i.location)):
        value = int(item.count * item.unit_price)
        total += value
        out += f'{item.sku},{item.location},{item.name},{item.count},{item.unit_price},{value}\n'
    out += 'TOTAL,' + str(total) + '\n'
    return out
