# Stockroom — Task

You are given a pure-stdlib Python CLI, `stockroom`, that tracks warehouse
inventory in a JSON file. The data model was migrated from one row per SKU to
one row per `(sku, location)`, and the implementation is only partway through
that migration: it contains **known bugs**, is **missing four commands**, and
its money math is **not exact**. Your job: make the program behave **exactly**
as the spec below describes.

## Project layout

- `stockroom/data.py` — data model and JSON persistence (already correct; don't rewrite it)
- `stockroom/ops.py` — business logic (contains bugs and is missing functions)
- `stockroom/pricing.py` — money helpers (contains a rounding bug)
- `stockroom/cli.py` — command-line interface (contains a bug and the missing commands)
- `stockroom/legacy_report.py` — legacy CSV renderer (frozen; see Rules)
- `tools/nightly_restock.py` — maintenance script (must keep working; see Rules)
- `seed.json` — a legacy-format data file (at most one row per sku)

Run it from the project root as:

```
python3 -m stockroom --file PATH <command> ...
```

## Data model

- The file is a JSON array of row objects with exactly the keys `sku`,
  `location`, `name` (strings), `count` (integer), `unit_price` (number,
  dollars).
- Rows are identified by the pair `(sku, location)`. One SKU may have several
  rows — one per location it is stocked in. A well-formed file has at most one
  row per `(sku, location)` pair.
- Legacy files (such as `seed.json`) have at most one row per sku; loading
  them works unchanged.
- `name` and `unit_price` are **per-SKU attributes**: every row of a SKU
  carries the same name and unit price.
- `unit_price` is interpreted as the exact decimal value written in the file
  (`Decimal(str(unit_price))` semantics).
- **Save normalization**: every mutating command persists the file with rows
  sorted by `(sku, location)` and with zero-count rows dropped.

## Money

- All money math uses exact decimals (the Python `decimal` module or an
  equivalent); never binary floats.
- A row's value is `count * unit_price`, computed exactly.
- A total is the exact sum of the involved row values, rounded **once** to 2
  decimals with half-up rounding (`ROUND_HALF_UP`), and printed with exactly 2
  decimals. Never round intermediate values.

## Python API (contract)

The hidden tests import the following names, so keep the module layout and
names exactly as listed. Add the missing functions to the modules listed
below (do not create new modules).

- `stockroom.data` — `Item` (dataclass with fields `sku`, `name`,
  `location`, `count`, `unit_price`), `load_items(path)`, `save_items(path,
  items)`.
- `stockroom.pricing` — `line_value(count, unit_price)` (exact row value),
  `round_money(value)` (to 2 decimals, half-up), `format_money(value)` (a
  string with exactly 2 decimals).
- `stockroom.ops` — exceptions `InsufficientStock` and `AttributeConflict`;
  functions `add_stock(items, sku, name, location, count, unit_price)`,
  `remove_stock(items, sku, amount, location=None)`,
  `move_stock(items, sku, from_location, to_location)`,
  `transfer_stock(items, sku, from_location, to_location, count)`,
  `total_value(items, location=None)`, `low_stock(items, threshold)`,
  `sku_total(items, sku)`, `summary(items)`, `report(items)`,
  `validate_items(items)`.
- `stockroom.legacy_report` — `render(items)` (see Rules).

Ops functions assume well-formed input values and raise `InsufficientStock`
for stock problems and `AttributeConflict` when `add_stock` is given a name or
unit price that conflicts with an existing SKU; they never raise for
usage-style problems. `low_stock(items, threshold)` returns a list of
`(sku, total_count)` pairs sorted by sku. `summary(items)` and `report(items)`
return the dicts printed by the `summary` and `report` commands.
`validate_items(items)` returns the list of violation reason strings printed
by `validate` (without the `INVALID: ` prefix).

## Commands

**`add SKU NAME LOCATION COUNT UNIT_PRICE`** — add stock for `SKU` at
`LOCATION`. If the `(sku, location)` row exists, its count increases by
`COUNT`; otherwise the row is created with count `COUNT`. If `SKU` does not
exist yet, the row takes the given `NAME` and `UNIT_PRICE`. If `SKU` already
exists, the given `NAME` and `UNIT_PRICE` must equal the SKU's existing name
and unit price; a mismatch is a domain error. Persists on success.

**`remove SKU COUNT [LOCATION]`** — remove `COUNT` units of `SKU`. When
`LOCATION` is omitted, units are removed from the **lexicographically first
location that holds stock** of the SKU (a row with count greater than 0).
Removing down to exactly 0 is allowed; the then-zero row is dropped on save.
Domain errors (exit 1): unknown SKU, no stock at the target location, or
`COUNT` greater than the count at that location. Persists on success.

**`move SKU FROM TO`** — move all units of the `(sku, FROM)` row into the
`(sku, TO)` row, merging into an existing `TO` row when one exists. The `FROM`
row is dropped on save. Domain error (exit 1): no stock at `(sku, FROM)`.
`FROM == TO` is a usage error. Persists on success.

**`transfer SKU FROM TO COUNT`** — move exactly `COUNT` units from the
`(sku, FROM)` row into the `(sku, TO)` row, creating the `TO` row when needed
and merging when one exists; the `FROM` row is reduced (and dropped on save if
it reaches 0). Domain errors (exit 1): no stock at `(sku, FROM)`, or `COUNT`
greater than the count there. `FROM == TO` is a usage error. Persists on
success.

**`list`** — one line per row, tab-separated
`sku\tlocation\tname\tcount\tunit_price` (`unit_price` with exactly 2
decimals), sorted by `(sku, location)`. No output for an empty file.

**`value [LOCATION]`** — the sum of `count * unit_price` over all rows, or
only the rows at `LOCATION`, per the Money rules; printed with 2 decimals.

**`low [THRESHOLD]`** — default threshold 5. Prints one line per SKU whose
**total** count across all locations is **at or below** `THRESHOLD`:
`sku\ttotal`, sorted by sku.

**`summary`** — one line of JSON on stdout: an object with exactly the keys
`low_stock_count` (number of SKUs with total count at or below 5),
`total_skus` (number of distinct SKUs), `total_units` (sum of all counts), and
`total_value` (a JSON number equal to what `value` prints).

**`report`** — one line of JSON on stdout: an object keyed by location, in
location order, containing only locations that have at least one row. Each
value is an object with exactly the keys `skus` (distinct SKUs at that
location), `units` (sum of counts there), and `value` (a JSON number per the
Money rules for that location). Empty file prints `{}`.

**`validate`** — no arguments. Checks the file for these invariants:
duplicate `(sku, location)` rows; negative counts; non-positive `unit_price`;
empty `sku`, `name`, or `location`; and a SKU whose rows disagree on name or
unit price. Prints one line per violation on stderr, in this order: first,
for each row in file order (row 0 first), the per-row violations in this
order — `row <i> has empty sku`, `row <i> has empty name`, `row <i> has empty
location`, `row <i> has negative count`, `row <i> has non-positive price`,
`row <i> duplicates (sku, location) of row <j>` (where `<j>` is the first
earlier row with the same pair) — each prefixed `INVALID: `; then, for each
SKU in order of first appearance, `INVALID: sku <sku> has inconsistent name`
and/or `INVALID: sku <sku> has inconsistent price`. Exit 1 if any violation
was printed; exit 0 with no output for a clean file.

## Exit codes

- `0` — success.
- `1` — domain error (`InsufficientStock` or `AttributeConflict`): print
  `error: <message>` to stderr; the file is left unchanged.
- `2` — usage error: non-positive `COUNT` on `add`/`remove`/`transfer`,
  non-positive `UNIT_PRICE` on `add`, negative `THRESHOLD` on `low`,
  `FROM == TO` on `move`/`transfer`, or any argparse error.

## `tools/nightly_restock.py`

Run from the project root as `python3 tools/nightly_restock.py --file PATH`
(`--file` defaults to `inventory.json`). For every SKU with a total count
greater than 0 and at most 5, in sorted sku order, it adds 10 units at the
SKU's existing name and unit price to the lexicographically first location
that holds stock of the SKU — by calling `stockroom.ops.add_stock`. It prints
one line per restocked SKU, `restocked <sku> +10`, in the same sku order,
saves the file, and exits 0 (including when nothing was restocked).

## Rules

- Python 3.11+ standard library only; no new dependencies.
- Keep the existing module layout and the function names listed above.
- Do not modify `TASK.md`, `seed.json`, `stockroom/data.py`, or
  `stockroom/legacy_report.py` — the last one's current output is frozen and
  is checked byte-for-byte.
- `tools/nightly_restock.py` must keep working exactly as specified; it is a
  consumer of the `stockroom.ops` API.
- Hidden tests are run against your final tree; they are not visible to you.
  The spec above is the complete contract they check.
