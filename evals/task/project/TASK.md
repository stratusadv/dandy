# Stockroom — Task

You are given a small pure-stdlib Python CLI, `stockroom`, that tracks
warehouse inventory in a JSON file. The current implementation has **known
bugs** and is **missing one command** that the spec below describes. Your
job: make the program behave **exactly** as the spec describes.

## Project layout

- `stockroom/data.py` — data model and JSON persistence (this module is correct; don't rewrite it)
- `stockroom/ops.py` — business logic (contains bugs)
- `stockroom/cli.py` — command-line interface (contains a bug and the missing command)
- `seed.json` — example data file

Run it as:

```
python3 -m stockroom --file PATH <command> ...
```

## Behavior spec

**State.** A JSON array of objects with keys `sku`, `name`, `location`,
`count`, `unit_price` (dollars, float). `sku` is unique within a file.
`--file PATH` selects the data file (default `inventory.json`); a missing
file means an empty inventory. Mutating commands (`add`, `remove`, `move`)
persist the inventory back to the file after the change.

**`add SKU NAME LOCATION COUNT UNIT_PRICE`** — add stock for a SKU.
If the SKU is new, create the row. If the SKU already exists, merge:
`count` is summed with the new amount, and `location` and `unit_price`
are updated to the new values. `COUNT` must be a positive integer.

**`remove SKU COUNT`** — remove `COUNT` units of a SKU. Allowed when the
SKU exists and `COUNT` is no more than the current count; the count may
reach exactly 0. Any other case (unknown SKU, or `COUNT` greater than the
current count) is a domain error: exit code 1, nothing changed. `COUNT`
must be a positive integer.

**`move SKU TO_LOCATION`** — move all units of the SKU to `TO_LOCATION`.
The count is unchanged. Unknown SKU is a domain error (exit code 1).

**`list`** — print one line per item, tab-separated
`sku\tname\tlocation\tcount\tunit_price` (unit_price with 2 decimals),
sorted by sku.

**`value [LOCATION]`** — print the total value, the sum of
`count * unit_price` over all items (or only the items at `LOCATION` when
given), rounded to 2 decimals and printed with 2 decimals.

**`low [THRESHOLD]`** — default threshold is 5. Print one line per item,
`sku\tcount`, for every item whose count is **at or below** the threshold,
sorted by sku.

**`summary`** — print a single JSON object with exactly these keys:
`low_stock_count` (items at or below the default threshold of 5),
`total_skus` (number of items), `total_units` (sum of all counts), and
`total_value` (the same value `value` prints, rounded to 2 decimals).

**Exit codes.** `0` success, `1` domain error (unknown or insufficient
stock), `2` usage error (bad arguments, e.g. a non-positive count).

## Rules

- Python 3 standard library only; no new dependencies.
- Keep the existing module layout and function names.
- Do not modify `TASK.md` or `seed.json`.
- Hidden tests will be run against your final tree; they are not visible
  to you. The spec above is the contract they check.
